"""Integration tests for API endpoints"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models import Dataset, Column, Lineage
from app.schemas import DatasetCreate, ColumnCreate, LineageCreate


# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_teardown():
    """Setup and teardown for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestDatasetEndpoints:
    """Test dataset API endpoints"""

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_create_dataset(self):
        """Test creating a dataset"""
        dataset_data = {
            "fqn": "snowflake.sales.public.orders",
            "connection_name": "snowflake",
            "database_name": "sales",
            "schema_name": "public",
            "table_name": "orders",
            "source_type": "Snowflake",
            "columns": [
                {"name": "order_id", "type": "INT"},
                {"name": "customer_id", "type": "INT"},
                {"name": "amount", "type": "DECIMAL"}
            ]
        }

        response = client.post("/api/v1/datasets/", json=dataset_data)
        assert response.status_code == 201
        data = response.json()
        assert data["fqn"] == "snowflake.sales.public.orders"
        assert len(data["columns"]) == 3

    def test_create_dataset_duplicate_fqn(self):
        """Test creating dataset with duplicate FQN"""
        dataset_data = {
            "fqn": "snowflake.sales.public.orders",
            "connection_name": "snowflake",
            "database_name": "sales",
            "schema_name": "public",
            "table_name": "orders",
            "source_type": "Snowflake",
            "columns": []
        }

        # Create first one
        client.post("/api/v1/datasets/", json=dataset_data)

        # Try to create duplicate
        response = client.post("/api/v1/datasets/", json=dataset_data)
        assert response.status_code == 409

    def test_create_dataset_invalid_fqn_format(self):
        """Test creating dataset with invalid FQN format"""
        dataset_data = {
            "fqn": "invalid.fqn",  # Should be 4 parts
            "connection_name": "snowflake",
            "database_name": "sales",
            "schema_name": "public",
            "table_name": "orders",
            "source_type": "Snowflake",
            "columns": []
        }

        response = client.post("/api/v1/datasets/", json=dataset_data)
        assert response.status_code == 422

    def test_list_datasets(self):
        """Test listing datasets"""
        # Create a dataset
        dataset_data = {
            "fqn": "snowflake.sales.public.orders",
            "connection_name": "snowflake",
            "database_name": "sales",
            "schema_name": "public",
            "table_name": "orders",
            "source_type": "Snowflake",
            "columns": []
        }
        client.post("/api/v1/datasets/", json=dataset_data)

        # List datasets
        response = client.get("/api/v1/datasets/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_dataset(self):
        """Test getting a specific dataset"""
        # Create dataset
        dataset_data = {
            "fqn": "snowflake.sales.public.orders",
            "connection_name": "snowflake",
            "database_name": "sales",
            "schema_name": "public",
            "table_name": "orders",
            "source_type": "Snowflake",
            "columns": []
        }
        create_response = client.post("/api/v1/datasets/", json=dataset_data)
        dataset_id = create_response.json()["id"]

        # Get dataset
        response = client.get(f"/api/v1/datasets/{dataset_id}")
        assert response.status_code == 200
        assert response.json()["fqn"] == "snowflake.sales.public.orders"

    def test_get_dataset_not_found(self):
        """Test getting non-existent dataset"""
        response = client.get("/api/v1/datasets/999")
        assert response.status_code == 404


class TestLineageEndpoints:
    """Test lineage API endpoints"""

    def setup_method(self):
        """Setup test data"""
        # Create two datasets
        self.dataset1_data = {
            "fqn": "snowflake.sales.public.orders_raw",
            "connection_name": "snowflake",
            "database_name": "sales",
            "schema_name": "public",
            "table_name": "orders_raw",
            "source_type": "Snowflake",
            "columns": []
        }

        self.dataset2_data = {
            "fqn": "snowflake.sales.public.orders_clean",
            "connection_name": "snowflake",
            "database_name": "sales",
            "schema_name": "public",
            "table_name": "orders_clean",
            "source_type": "Snowflake",
            "columns": []
        }

    def test_create_lineage(self):
        """Test creating lineage relationship"""
        # Create datasets
        resp1 = client.post("/api/v1/datasets/", json=self.dataset1_data)
        resp2 = client.post("/api/v1/datasets/", json=self.dataset2_data)

        dataset1_id = resp1.json()["id"]
        dataset2_id = resp2.json()["id"]

        # Create lineage
        lineage_data = {
            "upstream_dataset_id": dataset1_id,
            "downstream_dataset_id": dataset2_id
        }

        response = client.post("/api/v1/lineage/", json=lineage_data)
        assert response.status_code == 201
        assert response.json()["upstream_dataset_id"] == dataset1_id

    def test_create_lineage_cycle_detection(self):
        """Test cycle detection in lineage"""
        # Create 3 datasets: A -> B -> C
        resp1 = client.post("/api/v1/datasets/", json=self._make_dataset("dataset_a"))
        resp2 = client.post("/api/v1/datasets/", json=self._make_dataset("dataset_b"))
        resp3 = client.post("/api/v1/datasets/", json=self._make_dataset("dataset_c"))

        id1 = resp1.json()["id"]
        id2 = resp2.json()["id"]
        id3 = resp3.json()["id"]

        # Create A -> B
        client.post("/api/v1/lineage/", json={
            "upstream_dataset_id": id1,
            "downstream_dataset_id": id2
        })

        # Create B -> C
        client.post("/api/v1/lineage/", json={
            "upstream_dataset_id": id2,
            "downstream_dataset_id": id3
        })

        # Try to create C -> A (would create cycle)
        response = client.post("/api/v1/lineage/", json={
            "upstream_dataset_id": id3,
            "downstream_dataset_id": id1
        })

        assert response.status_code == 400
        assert "cycle" in response.json()["detail"].lower()

    def test_create_lineage_duplicate(self):
        """Test creating duplicate lineage"""
        resp1 = client.post("/api/v1/datasets/", json=self.dataset1_data)
        resp2 = client.post("/api/v1/datasets/", json=self.dataset2_data)

        dataset1_id = resp1.json()["id"]
        dataset2_id = resp2.json()["id"]

        lineage_data = {
            "upstream_dataset_id": dataset1_id,
            "downstream_dataset_id": dataset2_id
        }

        # Create first time
        client.post("/api/v1/lineage/", json=lineage_data)

        # Try to create duplicate
        response = client.post("/api/v1/lineage/", json=lineage_data)
        assert response.status_code == 409

    def _make_dataset(self, name: str):
        """Helper to create dataset data"""
        return {
            f"fqn": f"snowflake.sales.public.{name}",
            "connection_name": "snowflake",
            "database_name": "sales",
            "schema_name": "public",
            "table_name": name,
            "source_type": "Snowflake",
            "columns": []
        }


class TestSearchEndpoints:
    """Test search API endpoints"""

    def setup_method(self):
        """Setup test data"""
        # Create datasets with various matching fields
        datasets = [
            {
                "fqn": "snowflake.sales.public.orders",
                "connection_name": "snowflake",
                "database_name": "sales",
                "schema_name": "public",
                "table_name": "orders",
                "source_type": "Snowflake",
                "columns": [
                    {"name": "order_id", "type": "INT"},
                    {"name": "customer_id", "type": "INT"}
                ]
            },
            {
                "fqn": "snowflake.sales.public.customers",
                "connection_name": "snowflake",
                "database_name": "sales",
                "schema_name": "public",
                "table_name": "customers",
                "source_type": "Snowflake",
                "columns": [
                    {"name": "customer_id", "type": "INT"},
                    {"name": "customer_name", "type": "VARCHAR"}
                ]
            }
        ]

        for dataset in datasets:
            client.post("/api/v1/datasets/", json=dataset)

    def test_search_by_table_name(self):
        """Test search by table name (priority 1)"""
        response = client.get("/api/v1/search/?q=orders")
        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] > 0
        # First result should be table_name match
        assert data["results"][0]["match_type"] == "table_name"

    def test_search_by_column_name(self):
        """Test search by column name (priority 2)"""
        response = client.get("/api/v1/search/?q=customer_id")
        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] > 0
        # Should find datasets with customer_id column
        assert any(r["match_type"] == "column_name" for r in data["results"])

    def test_search_by_schema_name(self):
        """Test search by schema name (priority 3)"""
        response = client.get("/api/v1/search/?q=public")
        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] > 0

    def test_search_no_results(self):
        """Test search with no results"""
        response = client.get("/api/v1/search/?q=nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] == 0
        assert len(data["results"]) == 0
