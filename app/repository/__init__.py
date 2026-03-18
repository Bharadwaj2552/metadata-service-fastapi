"""Repository layer for database operations"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List, Optional
from app.models import Dataset, Column, Lineage


# ==================== Dataset Repository ====================

class DatasetRepository:
    """Repository for dataset database operations"""

    @staticmethod
    def get_by_id(db: Session, dataset_id: int) -> Optional[Dataset]:
        """Get dataset by ID"""
        return db.query(Dataset).filter(Dataset.id == dataset_id).first()

    @staticmethod
    def get_by_fqn(db: Session, fqn: str) -> Optional[Dataset]:
        """Get dataset by fully qualified name"""
        return db.query(Dataset).filter(Dataset.fqn == fqn).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Dataset]:
        """Get all datasets with pagination"""
        datasets = db.query(Dataset).order_by(desc(Dataset.id)).all()
        return datasets[skip:skip + limit]

    @staticmethod
    def create(db: Session, dataset: Dataset) -> Dataset:
        """Create a new dataset"""
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset

    @staticmethod
    def update(db: Session, dataset_id: int, updates: dict) -> Optional[Dataset]:
        """Update an existing dataset"""
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if dataset:
            for key, value in updates.items():
                setattr(dataset, key, value)
            db.commit()
            db.refresh(dataset)
        return dataset

    @staticmethod
    def delete(db: Session, dataset_id: int) -> bool:
        """Delete a dataset"""
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if dataset:
            db.delete(dataset)
            db.commit()
            return True
        return False

    @staticmethod
    def exists_by_fqn(db: Session, fqn: str) -> bool:
        """Check if dataset exists by FQN"""
        return db.query(Dataset).filter(Dataset.fqn == fqn).first() is not None


# ==================== Lineage Repository ====================

class LineageRepository:
    """Repository for lineage database operations"""

    @staticmethod
    def get_by_id(db: Session, lineage_id: int) -> Optional[Lineage]:
        """Get lineage by ID"""
        return db.query(Lineage).filter(Lineage.id == lineage_id).first()

    @staticmethod
    def get_all(db: Session) -> List[Lineage]:
        """Get all lineage relationships"""
        return db.query(Lineage).order_by(desc(Lineage.created_at)).all()

    @staticmethod
    def get_upstream(db: Session, dataset_id: int) -> List[Dataset]:
        """Get all upstream datasets"""
        return db.query(Dataset).join(
            Lineage, Lineage.upstream_dataset_id == Dataset.id
        ).filter(
            Lineage.downstream_dataset_id == dataset_id
        ).all()

    @staticmethod
    def get_downstream(db: Session, dataset_id: int) -> List[Dataset]:
        """Get all downstream datasets"""
        return db.query(Dataset).join(
            Lineage, Lineage.downstream_dataset_id == Dataset.id
        ).filter(
            Lineage.upstream_dataset_id == dataset_id
        ).all()

    @staticmethod
    def get_edges_as_tuples(db: Session) -> List[tuple]:
        """Get all lineage edges as (upstream_id, downstream_id) tuples"""
        edges = db.query(
            Lineage.upstream_dataset_id,
            Lineage.downstream_dataset_id
        ).all()
        return [(e[0], e[1]) for e in edges]

    @staticmethod
    def exists(db: Session, upstream_id: int, downstream_id: int) -> bool:
        """Check if lineage relationship exists"""
        return db.query(Lineage).filter(
            Lineage.upstream_dataset_id == upstream_id,
            Lineage.downstream_dataset_id == downstream_id
        ).first() is not None

    @staticmethod
    def create(db: Session, lineage: Lineage) -> Lineage:
        """Create a new lineage relationship"""
        db.add(lineage)
        db.commit()
        db.refresh(lineage)
        return lineage

    @staticmethod
    def delete(db: Session, lineage_id: int) -> bool:
        """Delete a lineage relationship"""
        lineage = db.query(Lineage).filter(Lineage.id == lineage_id).first()
        if lineage:
            db.delete(lineage)
            db.commit()
            return True
        return False


# ==================== Column Repository ====================

class ColumnRepository:
    """Repository for column database operations"""

    @staticmethod
    def get_by_id(db: Session, column_id: int) -> Optional[Column]:
        """Get column by ID"""
        return db.query(Column).filter(Column.id == column_id).first()

    @staticmethod
    def get_by_dataset_id(db: Session, dataset_id: int) -> List[Column]:
        """Get all columns for a dataset"""
        return db.query(Column).filter(Column.dataset_id == dataset_id).all()

    @staticmethod
    def create(db: Session, column: Column) -> Column:
        """Create a new column"""
        db.add(column)
        db.commit()
        db.refresh(column)
        return column

    @staticmethod
    def delete(db: Session, column_id: int) -> bool:
        """Delete a column"""
        column = db.query(Column).filter(Column.id == column_id).first()
        if column:
            db.delete(column)
            db.commit()
            return True
        return False

    @staticmethod
    def search_by_name(db: Session, column_name: str) -> List[Column]:
        """Search columns by name pattern"""
        return db.query(Column).filter(
            Column.name.ilike(f"%{column_name}%")
        ).all()
