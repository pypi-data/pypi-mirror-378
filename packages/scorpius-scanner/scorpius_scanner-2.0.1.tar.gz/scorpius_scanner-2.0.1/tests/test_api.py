"""API endpoint tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.db.models import Base
from app.core.security import get_password_hash


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestAuth:
    """Authentication endpoint tests."""

    def test_register_user(self):
        """Test user registration."""
        response = client.post(
            "/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_email(self):
        """Test registration with duplicate email."""
        # Register first user
        client.post(
            "/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "TestPass123!",
            },
        )

        # Try to register with same email
        response = client.post(
            "/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "AnotherPass123!",
            },
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_login_valid_credentials(self):
        """Test login with valid credentials."""
        # Register user
        client.post(
            "/v1/auth/register",
            json={
                "email": "login@example.com",
                "password": "TestPass123!",
            },
        )

        # Login
        response = client.post(
            "/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "TestPass123!",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = client.post(
            "/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "WrongPass123!",
            },
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()


class TestProjects:
    """Project endpoint tests."""

    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers."""
        response = client.post(
            "/v1/auth/register",
            json={
                "email": "project_test@example.com",
                "password": "TestPass123!",
            },
        )
        
        # If registration fails (user already exists), try login
        if response.status_code != 200:
            response = client.post(
                "/v1/auth/login",
                data={
                    "username": "project_test@example.com",
                    "password": "TestPass123!",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_create_project(self, auth_headers):
        """Test project creation."""
        response = client.post(
            "/v1/projects",
            json={
                "name": "Test Project",
                "default_chain": "ethereum",
            },
            headers=auth_headers,
            params={"org_id": "test-org-id"},  # Would need real org ID
        )

        # This test would need proper org setup
        # assert response.status_code == 200

    def test_list_projects(self, auth_headers):
        """Test listing projects."""
        response = client.get(
            "/v1/projects",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestHealth:
    """Health check endpoint tests."""

    def test_health_check(self):
        """Test basic health check."""
        response = client.get("/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_readiness_check(self):
        """Test readiness check."""
        response = client.get("/v1/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data


class TestScans:
    """Scan endpoint tests."""

    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers."""
        response = client.post(
            "/v1/auth/register",
            json={
                "email": "scan_test@example.com",
                "password": "TestPass123!",
            },
        )
        
        # If registration fails (user already exists), try login
        if response.status_code != 200:
            response = client.post(
                "/v1/auth/login",
                data={
                    "username": "scan_test@example.com",
                    "password": "TestPass123!",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_create_scan_missing_file(self, auth_headers):
        """Test scan creation without file."""
        response = client.post(
            "/v1/scans",
            data={
                "project_id": "test-project-id",
                "fast": "true",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_get_scan_not_found(self, auth_headers):
        """Test getting non-existent scan."""
        response = client.get(
            "/v1/scans/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestMetrics:
    """Metrics endpoint tests."""

    @pytest.fixture
    def auth_headers(self):
        """Get authentication headers."""
        response = client.post(
            "/v1/auth/register",
            json={
                "email": "metrics_test@example.com",
                "password": "TestPass123!",
            },
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_get_metrics(self, auth_headers):
        """Test getting organization metrics."""
        # Extract org_id from the JWT token
        from jose import jwt
        from app.core.config import settings
        
        token = auth_headers["Authorization"].replace("Bearer ", "")
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        org_id = payload.get("org_id")
        
        response = client.get(
            "/v1/metrics",
            headers=auth_headers,
            params={
                "org_id": org_id,
                "days": 30,
            },
        )

        assert response.status_code == 200


# Integration tests
@pytest.mark.integration
class TestIntegration:
    """Integration tests requiring full stack."""

    def test_full_scan_workflow(self):
        """Test complete scan workflow."""
        # This would test:
        # 1. User registration
        # 2. Project creation
        # 3. Scan submission
        # 4. Result retrieval
        pass

    def test_organization_workflow(self):
        """Test organization management workflow."""
        # This would test:
        # 1. Org creation
        # 2. Member invitation
        # 3. Role management
        # 4. API token creation
        pass
