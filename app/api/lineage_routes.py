"""API routes for lineage"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas import LineageCreate, LineageResponse
from app.services import LineageService

router = APIRouter(prefix="/api/v1/lineage", tags=["lineage"])


@router.post(
    "/",
    response_model=LineageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a lineage relationship",
    responses={
        201: {"description": "Lineage created successfully"},
        400: {"description": "Invalid request or cycle would be created"},
        404: {"description": "Dataset not found"},
        409: {"description": "Lineage relationship already exists"},
    }
)
def create_lineage(
    lineage: LineageCreate,
    db: Session = Depends(get_db)
) -> LineageResponse:
    """
    Create a lineage relationship between two datasets.

    This endpoint establishes a data flow from an upstream dataset to a downstream dataset.

    **Validation:**
    - Both datasets must exist
    - Lineage relationship must not already exist
    - Adding the relationship must not create a cycle

    **Example:**
    - upstream_dataset_id: 1 (orders_raw)
    - downstream_dataset_id: 2 (orders_clean)

    This means orders_clean is derived from orders_raw.
    """
    return LineageService.add_lineage(db, lineage)


@router.get(
    "/",
    response_model=List[LineageResponse],
    summary="List all lineage relationships",
    responses={200: {"description": "List of lineage relationships"}}
)
def list_lineages(db: Session = Depends(get_db)) -> List[LineageResponse]:
    """Get all lineage relationships in the system"""
    return LineageService.list_lineages(db)


@router.get(
    "/{lineage_id}",
    response_model=LineageResponse,
    summary="Get lineage by ID",
    responses={
        200: {"description": "Lineage found"},
        404: {"description": "Lineage not found"},
    }
)
def get_lineage(
    lineage_id: int,
    db: Session = Depends(get_db)
) -> LineageResponse:
    """Get a specific lineage relationship by its ID"""
    return LineageService.get_lineage(db, lineage_id)


@router.delete(
    "/{lineage_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a lineage relationship",
    responses={
        204: {"description": "Lineage deleted successfully"},
        404: {"description": "Lineage not found"},
    }
)
def delete_lineage(
    lineage_id: int,
    db: Session = Depends(get_db)
) -> None:
    """Delete a lineage relationship between two datasets"""
    LineageService.delete_lineage(db, lineage_id)
