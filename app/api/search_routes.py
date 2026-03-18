"""API routes for search"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import SearchResponse
from app.services import SearchService

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get(
    "/",
    response_model=SearchResponse,
    summary="Search datasets",
    responses={200: {"description": "Search results"}}
)
def search_datasets(
    q: str = Query(..., min_length=1, max_length=255, description="Search query"),
    db: Session = Depends(get_db)
) -> SearchResponse:
    """
    Search for datasets by name, column name, schema name, or database name.

    **Priority-based Results:**
    1. **table_name** - Exact or partial match on table name (highest priority)
    2. **column_name** - Match on column names within datasets
    3. **schema_name** - Match on schema names
    4. **database_name** - Match on database names (lowest priority)

    **Example Search Queries:**
    - `q=orders` - Find all datasets with "orders" in table name or columns
    - `q=customer_id` - Find datasets with "customer_id" column
    - `q=public` - Find datasets in "public" schema

    Results are deduplicated and sorted by priority, so each dataset appears only once
    with its highest priority match type.
    """
    return SearchService.search_datasets(db, q)
