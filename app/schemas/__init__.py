from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


# ==================== Column Schemas ====================

class ColumnBase(BaseModel):
    """Base column schema"""
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=100)


class ColumnCreate(ColumnBase):
    """Schema for creating a column"""
    pass


class ColumnResponse(ColumnBase):
    """Schema for column response"""
    id: int
    dataset_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Dataset Schemas ====================

class DatasetBase(BaseModel):
    """Base dataset schema"""
    fqn: str = Field(..., min_length=1, max_length=512)
    connection_name: str = Field(..., min_length=1, max_length=255)
    database_name: str = Field(..., min_length=1, max_length=255)
    schema_name: str = Field(..., min_length=1, max_length=255)
    table_name: str = Field(..., min_length=1, max_length=255)
    source_type: str = Field(..., min_length=1, max_length=100)

    @validator('source_type')
    def validate_source_type(cls, v):
        """Validate source type is one of supported systems"""
        valid_types = ['MySQL', 'PostgreSQL', 'MSSQL', 'Snowflake', 'Redshift', 'BigQuery', 'Oracle']
        if v not in valid_types:
            raise ValueError(f'source_type must be one of {valid_types}')
        return v

    @validator('fqn')
    def validate_fqn_format(cls, v):
        """Validate FQN has correct format: connection.database.schema.table"""
        parts = v.split('.')
        if len(parts) != 4:
            raise ValueError('FQN must be in format: connection_name.database_name.schema_name.table_name')
        return v


class DatasetCreate(DatasetBase):
    """Schema for creating a dataset"""
    columns: List[ColumnCreate] = Field(default_factory=list)


class DatasetUpdate(BaseModel):
    """Schema for updating a dataset"""
    columns: Optional[List[ColumnCreate]] = None


class DatasetResponse(DatasetBase):
    """Schema for dataset response"""
    id: int
    columns: List[ColumnResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DatasetWithLineageResponse(DatasetResponse):
    """Schema for dataset with complete lineage information"""
    upstream_datasets: List['DatasetResponse'] = []
    downstream_datasets: List['DatasetResponse'] = []

    class Config:
        from_attributes = True


# Update forward references
DatasetWithLineageResponse.model_rebuild()


# ==================== Lineage Schemas ====================

class LineageBase(BaseModel):
    """Base lineage schema"""
    upstream_dataset_id: int = Field(..., gt=0)
    downstream_dataset_id: int = Field(..., gt=0)

    @validator('downstream_dataset_id')
    def validate_different_datasets(cls, v, values):
        """Ensure upstream and downstream are different"""
        if 'upstream_dataset_id' in values and v == values['upstream_dataset_id']:
            raise ValueError('upstream_dataset_id and downstream_dataset_id must be different')
        return v


class LineageCreate(LineageBase):
    """Schema for creating a lineage relationship"""
    pass


class LineageResponse(LineageBase):
    """Schema for lineage response"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LineageWithDetailsResponse(LineageBase):
    """Schema for lineage response with full dataset details"""
    id: int
    upstream_dataset: DatasetResponse
    downstream_dataset: DatasetResponse
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Search Schemas ====================

class SearchResult(BaseModel):
    """Search result entry"""
    dataset: DatasetResponse
    match_type: str = Field(..., description="Type of match: table_name, column_name, schema_name, database_name")
    priority: int = Field(..., description="Search priority: 1=table, 2=column, 3=schema, 4=database")

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Search response with results"""
    query: str
    total_results: int
    results: List[SearchResult] = []


# ==================== Error Schemas ====================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    status_code: int


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    error: str = "Validation Error"
    details: List[dict]
