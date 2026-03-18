from sqlalchemy import Column as SAColumn, Integer, String, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Dataset(Base):
    """Represents a dataset with metadata and lineage"""

    __tablename__ = "datasets"

    # Primary key
    id = SAColumn(Integer, primary_key=True, index=True)

    # Metadata fields
    fqn = SAColumn(String(512), unique=True, nullable=False, index=True)
    connection_name = SAColumn(String(255), nullable=False, index=True)
    database_name = SAColumn(String(255), nullable=False, index=True)
    schema_name = SAColumn(String(255), nullable=False, index=True)
    table_name = SAColumn(String(255), nullable=False, index=True)

    # Source system type (MySQL, PostgreSQL, MSSQL, Snowflake, Redshift, etc.)
    source_type = SAColumn(String(100), nullable=False)

    # Timestamps
    created_at = SAColumn(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = SAColumn(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    columns = relationship("Column", back_populates="dataset", cascade="all, delete-orphan")
    upstream_lineages = relationship(
        "Lineage",
        foreign_keys="Lineage.downstream_dataset_id",
        back_populates="downstream_dataset",
        cascade="all, delete-orphan"
    )
    downstream_lineages = relationship(
        "Lineage",
        foreign_keys="Lineage.upstream_dataset_id",
        back_populates="upstream_dataset",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_connection_db_schema_table", "connection_name", "database_name", "schema_name", "table_name"),
        UniqueConstraint("fqn", name="uq_dataset_fqn"),
    )

    def __repr__(self) -> str:
        return f"<Dataset(id={self.id}, fqn={self.fqn})>"


class Column(Base):
    """Represents a column/field in a dataset"""

    __tablename__ = "columns"

    # Primary key
    id = SAColumn(Integer, primary_key=True, index=True)

    # Foreign key
    dataset_id = SAColumn(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)

    # Column properties
    name = SAColumn(String(255), nullable=False, index=True)
    type = SAColumn(String(100), nullable=False)

    # Timestamps
    created_at = SAColumn(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    dataset = relationship("Dataset", back_populates="columns")

    # Indexes
    __table_args__ = (
        Index("idx_dataset_column_name", "dataset_id", "name"),
    )

    def __repr__(self) -> str:
        return f"<Column(id={self.id}, name={self.name}, type={self.type})>"


class Lineage(Base):
    """Represents lineage relationship between datasets"""

    __tablename__ = "lineage"

    # Primary key
    id = SAColumn(Integer, primary_key=True, index=True)

    # Foreign keys
    upstream_dataset_id = SAColumn(
        Integer,
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    downstream_dataset_id = SAColumn(
        Integer,
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Timestamps
    created_at = SAColumn(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    upstream_dataset = relationship(
        "Dataset",
        foreign_keys=[upstream_dataset_id],
        back_populates="downstream_lineages"
    )
    downstream_dataset = relationship(
        "Dataset",
        foreign_keys=[downstream_dataset_id],
        back_populates="upstream_lineages"
    )

    # Indexes
    __table_args__ = (
        Index("idx_upstream_downstream", "upstream_dataset_id", "downstream_dataset_id"),
        UniqueConstraint("upstream_dataset_id", "downstream_dataset_id", name="uq_lineage"),
    )

    def __repr__(self) -> str:
        return f"<Lineage(id={self.id}, upstream_id={self.upstream_dataset_id}, downstream_id={self.downstream_dataset_id})>"
