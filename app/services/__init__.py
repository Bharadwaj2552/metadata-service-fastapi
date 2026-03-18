"""Service layer for business logic"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Tuple
from fastapi import HTTPException, status

from app.models import Dataset, Column, Lineage
from app.schemas import (
    DatasetCreate, DatasetResponse, DatasetWithLineageResponse,
    LineageCreate, LineageResponse, SearchResponse, SearchResult
)
from app.repository import DatasetRepository, LineageRepository, ColumnRepository
from app.utils import has_cycle, get_upstream_datasets, get_downstream_datasets, build_lineage_graphs


# ==================== Dataset Service ====================

class DatasetService:
    """Service for dataset operations"""

    @staticmethod
    def create_dataset(db: Session, dataset_create: DatasetCreate) -> DatasetResponse:
        """Create a new dataset with columns"""
        # Check if FQN already exists
        if DatasetRepository.exists_by_fqn(db, dataset_create.fqn):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Dataset with FQN '{dataset_create.fqn}' already exists",
                headers={"X-Error-Code": "FQN_EXISTS"}
            )

        # Create dataset
        dataset = Dataset(
            fqn=dataset_create.fqn,
            connection_name=dataset_create.connection_name,
            database_name=dataset_create.database_name,
            schema_name=dataset_create.schema_name,
            table_name=dataset_create.table_name,
            source_type=dataset_create.source_type
        )

        dataset = DatasetRepository.create(db, dataset)

        # Add columns
        for col_data in dataset_create.columns:
            column = Column(
                dataset_id=dataset.id,
                name=col_data.name,
                type=col_data.type
            )
            ColumnRepository.create(db, column)

        # Refresh to load relationships
        db.refresh(dataset)

        # Return with lineage (initially empty since it's new)
        response_data = DatasetResponse.model_validate(dataset)
        return DatasetWithLineageResponse(
            **response_data.model_dump(),
            upstream_datasets=[],
            downstream_datasets=[]
        )

    @staticmethod
    def get_dataset(db: Session, dataset_id: int) -> DatasetWithLineageResponse:
        """Get dataset by ID with lineage information"""
        dataset = DatasetRepository.get_by_id(db, dataset_id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset with ID {dataset_id} not found"
            )
        
        # Get lineage information
        upstream = LineageRepository.get_upstream(db, dataset_id)
        downstream = LineageRepository.get_downstream(db, dataset_id)
        
        response_data = DatasetResponse.model_validate(dataset)
        
        return DatasetWithLineageResponse(
            **response_data.model_dump(),
            upstream_datasets=[DatasetResponse.model_validate(d) for d in upstream],
            downstream_datasets=[DatasetResponse.model_validate(d) for d in downstream]
        )

    @staticmethod
    def get_dataset_with_lineage(db: Session, dataset_id: int) -> DatasetWithLineageResponse:
        """Get dataset with complete lineage information"""
        dataset = DatasetRepository.get_by_id(db, dataset_id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset with ID {dataset_id} not found"
            )

        # Get upstream and downstream datasets
        upstream = LineageRepository.get_upstream(db, dataset_id)
        downstream = LineageRepository.get_downstream(db, dataset_id)

        response_data = DatasetResponse.model_validate(dataset)

        return DatasetWithLineageResponse(
            **response_data.model_dump(),
            upstream_datasets=[DatasetResponse.model_validate(d) for d in upstream],
            downstream_datasets=[DatasetResponse.model_validate(d) for d in downstream]
        )

    @staticmethod
    def list_datasets(db: Session, skip: int = 0, limit: int = 100) -> List[DatasetWithLineageResponse]:
        """List all datasets with pagination and lineage information"""
        datasets = DatasetRepository.get_all(db, skip, limit)
        results = []
        for d in datasets:
            upstream = LineageRepository.get_upstream(db, d.id)
            downstream = LineageRepository.get_downstream(db, d.id)
            
            response_data = DatasetResponse.model_validate(d)
            
            results.append(
                DatasetWithLineageResponse(
                    **response_data.model_dump(),
                    upstream_datasets=[DatasetResponse.model_validate(u) for u in upstream],
                    downstream_datasets=[DatasetResponse.model_validate(dn) for dn in downstream]
                )
            )
        return results

    @staticmethod
    def delete_dataset(db: Session, dataset_id: int) -> Dict:
        """Delete a dataset"""
        if not DatasetRepository.delete(db, dataset_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset with ID {dataset_id} not found"
            )
        return {"message": "Dataset deleted successfully", "dataset_id": dataset_id}


# ==================== Lineage Service ====================

class LineageService:
    """Service for lineage operations"""

    @staticmethod
    def add_lineage(db: Session, lineage_create: LineageCreate) -> LineageResponse:
        """Add lineage relationship between datasets"""
        upstream_id = lineage_create.upstream_dataset_id
        downstream_id = lineage_create.downstream_dataset_id

        # Validate datasets exist
        upstream = DatasetRepository.get_by_id(db, upstream_id)
        downstream = DatasetRepository.get_by_id(db, downstream_id)

        if not upstream:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Upstream dataset with ID {upstream_id} not found",
                headers={"X-Error-Code": "UPSTREAM_NOT_FOUND"}
            )
        if not downstream:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Downstream dataset with ID {downstream_id} not found",
                headers={"X-Error-Code": "DOWNSTREAM_NOT_FOUND"}
            )

        # Check if lineage already exists
        if LineageRepository.exists(db, upstream_id, downstream_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Lineage relationship between {upstream_id} and {downstream_id} already exists",
                headers={"X-Error-Code": "LINEAGE_EXISTS"}
            )

        # Check for cycles
        edges = LineageRepository.get_edges_as_tuples(db)
        forward_graph, _ = build_lineage_graphs(edges)

        # Check if adding this edge would create a cycle
        # A cycle is created if downstream can reach upstream (after adding the edge)
        if has_cycle(forward_graph, downstream_id, upstream_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Adding this lineage would create a cycle in the data flow graph",
                headers={"X-Error-Code": "CYCLE_DETECTED"}
            )

        # Create lineage
        lineage = Lineage(
            upstream_dataset_id=upstream_id,
            downstream_dataset_id=downstream_id
        )

        lineage = LineageRepository.create(db, lineage)
        return LineageResponse.model_validate(lineage)

    @staticmethod
    def get_lineage(db: Session, lineage_id: int) -> LineageResponse:
        """Get lineage by ID"""
        lineage = LineageRepository.get_by_id(db, lineage_id)
        if not lineage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lineage with ID {lineage_id} not found"
            )
        return LineageResponse.model_validate(lineage)

    @staticmethod
    def list_lineages(db: Session) -> List[LineageResponse]:
        """List all lineage relationships"""
        lineages = LineageRepository.get_all(db)
        return [LineageResponse.model_validate(l) for l in lineages]

    @staticmethod
    def delete_lineage(db: Session, lineage_id: int) -> Dict:
        """Delete a lineage relationship"""
        if not LineageRepository.delete(db, lineage_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lineage with ID {lineage_id} not found"
            )
        return {"message": "Lineage deleted successfully", "lineage_id": lineage_id}


# ==================== Search Service ====================

class SearchService:
    """Service for search operations"""

    @staticmethod
    def search_datasets(db: Session, query: str) -> SearchResponse:
        """Search datasets by name, column name, schema name, or database name"""
        query_lower = query.lower()

        # Priority 1: Table name match
        table_matches = db.query(Dataset).filter(
            Dataset.table_name.ilike(f"%{query}%")
        ).all()

        # Priority 2: Column name match
        column_matches = db.query(Dataset).join(Column).filter(
            Column.name.ilike(f"%{query}%")
        ).distinct().all()

        # Priority 3: Schema name match
        schema_matches = db.query(Dataset).filter(
            Dataset.schema_name.ilike(f"%{query}%")
        ).all()

        # Priority 4: Database name match
        db_matches = db.query(Dataset).filter(
            Dataset.database_name.ilike(f"%{query}%")
        ).all()

        # Combine results with deduplication and proper priority ordering
        seen_dataset_ids: Dict[int, Tuple[int, str]] = {}  # dataset_id -> (priority, match_type)

        # Add priority 1 matches
        for dataset in table_matches:
            if dataset.id not in seen_dataset_ids or seen_dataset_ids[dataset.id][0] > 1:
                seen_dataset_ids[dataset.id] = (1, "table_name")

        # Add priority 2 matches (only if not already seen with higher priority)
        for dataset in column_matches:
            if dataset.id not in seen_dataset_ids or seen_dataset_ids[dataset.id][0] > 2:
                seen_dataset_ids[dataset.id] = (2, "column_name")

        # Add priority 3 matches (only if not already seen with higher priority)
        for dataset in schema_matches:
            if dataset.id not in seen_dataset_ids or seen_dataset_ids[dataset.id][0] > 3:
                seen_dataset_ids[dataset.id] = (3, "schema_name")

        # Add priority 4 matches (only if not already seen with higher priority)
        for dataset in db_matches:
            if dataset.id not in seen_dataset_ids:
                seen_dataset_ids[dataset.id] = (4, "database_name")

        # Sort by priority and build results
        sorted_results = sorted(seen_dataset_ids.items(), key=lambda x: x[1][0])

        results = []
        for dataset_id, (priority, match_type) in sorted_results:
            dataset = DatasetRepository.get_by_id(db, dataset_id)
            if dataset:
                results.append(
                    SearchResult(
                        dataset=DatasetResponse.model_validate(dataset),
                        match_type=match_type,
                        priority=priority
                    )
                )

        return SearchResponse(
            query=query,
            total_results=len(results),
            results=results
        )
