"""API routes for datasets"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas import DatasetCreate, DatasetResponse, DatasetWithLineageResponse
from app.services import DatasetService

router = APIRouter(prefix="/api/v1/datasets", tags=["datasets"])


@router.post(
    "/",
    response_model=DatasetWithLineageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new dataset",
    responses={
        201: {"description": "Dataset created successfully"},
        400: {"description": "Invalid request data"},
        409: {"description": "Dataset FQN already exists"},
    }
)
def create_dataset(
    dataset: DatasetCreate,
    db: Session = Depends(get_db)
) -> DatasetWithLineageResponse:
    """
    Create a new dataset with metadata and columns.

    - **fqn**: Fully qualified name (format: connection.database.schema.table)
    - **connection_name**: Name of the connection/source system
    - **database_name**: Name of the database
    - **schema_name**: Name of the schema
    - **table_name**: Name of the table
    - **source_type**: Type of source system (MySQL, PostgreSQL, MSSQL, Snowflake, etc.)
    - **columns**: List of columns with name and type
    
    Returns the newly created dataset with lineage information.
    """
    return DatasetService.create_dataset(db, dataset)


@router.get(
    "/",
    response_model=List[DatasetWithLineageResponse],
    summary="List all datasets",
    responses={200: {"description": "List of datasets with lineage"}}
)
def list_datasets(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db)
) -> List[DatasetWithLineageResponse]:
    """
    List all datasets with pagination support and lineage information.

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 100, max: 1000)
    - **upstream_datasets**: Datasets that feed into each dataset
    - **downstream_datasets**: Datasets that each dataset feeds into
    """
    return DatasetService.list_datasets(db, skip, limit)


@router.get(
    "/{dataset_id}",
    response_model=DatasetWithLineageResponse,
    summary="Get dataset by ID",
    responses={
        200: {"description": "Dataset found with lineage information"},
        404: {"description": "Dataset not found"},
    }
)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db)
) -> DatasetWithLineageResponse:
    """Get a specific dataset by its ID with full lineage information"""
    return DatasetService.get_dataset(db, dataset_id)


@router.get(
    "/{dataset_id}/lineage",
    response_model=DatasetWithLineageResponse,
    summary="Get dataset with lineage information",
    responses={
        200: {"description": "Dataset with lineage information"},
        404: {"description": "Dataset not found"},
    }
)
def get_dataset_lineage(
    dataset_id: int,
    db: Session = Depends(get_db)
) -> DatasetWithLineageResponse:
    """
    Get a dataset with all its upstream (source) and downstream (target) relationships.

    - **upstream_datasets**: Datasets that feed into this dataset
    - **downstream_datasets**: Datasets that this dataset feeds into
    """
    return DatasetService.get_dataset_with_lineage(db, dataset_id)


@router.delete(
    "/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a dataset",
    responses={
        204: {"description": "Dataset deleted successfully"},
        404: {"description": "Dataset not found"},
    }
)
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db)
) -> None:
    """Delete a dataset and all its associated relationships"""
    DatasetService.delete_dataset(db, dataset_id)
