"""
Security tests for VeritasAd API.

Run these tests to verify security fixes:
    pytest tests/unit/security/test_security_fixes.py -v

Requirements:
    - Test database configured (SQLite by default)
    - pytest, pytest-asyncio installed
"""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
import hashlib
import os
import socket

# Set test environment BEFORE importing app
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-min-32-chars")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-testing-min-64-chars-long-enough")

from app.main import create_app
from app.models.database import get_db, User, UserPlan, UserRole, Analysis, AnalysisStatus, SourceType
from app.core.dependencies import hash_api_key


@pytest_asyncio.fixture
async def app():
    """Create test app."""
    test_app = create_app()
    return test_app


@pytest_asyncio.fixture
async def client(app):
    """Create async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        timeout=30.0,
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session(app):
    """Create test database session."""
    from app.models.database import engine, Base, AsyncSessionLocal
    from sqlalchemy.ext.asyncio import AsyncSession
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    
    # Cleanup
    await engine.dispose()


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user with hashed API key."""
    api_key = "test_api_key_12345"
    user = User(
        api_key_hash=hash_api_key(api_key),
        email="test@example.com",
        plan=UserPlan.FREE,
        role=UserRole.USER,
        daily_limit=100,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user, api_key


@pytest_asyncio.fixture
async def admin_user(db_session):
    """Create a test admin user."""
    api_key = "admin_api_key_67890"
    user = User(
        api_key_hash=hash_api_key(api_key),
        email="admin@example.com",
        plan=UserPlan.PRO,
        role=UserRole.ADMIN,
        daily_limit=10000,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user, api_key


# ==================== AUTHENTICATION TESTS ====================

class TestAuthentication:
    """Test authentication security fixes."""

    @pytest.mark.asyncio
    async def test_api_key_hash_lookup(self, client, test_user, db_session):
        """Test that API key hash lookup works correctly."""
        user, api_key = test_user
        
        # Override get_db dependency
        app = client.app
        app.dependency_overrides[get_db] = lambda: db_session
        
        try:
            response = await client.get(
                "/api/v1/health",
                headers={"X-API-Key": api_key}
            )
            
            # Should authenticate successfully
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_invalid_api_key_rejected(self, client):
        """Test that invalid API keys are rejected."""
        response = await client.get(
            "/api/v1/health",
            headers={"X-API-Key": "invalid_key"}
        )
        
        # Should be rejected (401)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_no_auth_required_for_public_endpoints(self, client):
        """Test that public endpoints don't require auth."""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        
        response = await client.get("/")
        assert response.status_code == 200


# ==================== ADMIN AUTHORIZATION TESTS ====================

class TestAdminAuthorization:
    """Test admin authorization security fixes."""

    @pytest.mark.asyncio
    async def test_admin_endpoint_without_auth(self, client):
        """CRITICAL: Test admin endpoint without authentication."""
        response = await client.get("/api/v1/admin/users")
        
        # Should be rejected (401)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_admin_endpoint_with_user_token(self, client, test_user, db_session):
        """CRITICAL: Test admin endpoint with regular user token."""
        user, api_key = test_user
        
        app = client.app
        app.dependency_overrides[get_db] = lambda: db_session
        
        try:
            response = await client.get(
                "/api/v1/admin/users",
                headers={"X-API-Key": api_key}
            )
            
            # Should be forbidden (403)
            assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_admin_endpoint_with_admin_token(self, client, admin_user, db_session):
        """Test admin endpoint with admin token."""
        admin, api_key = admin_user
        
        app = client.app
        app.dependency_overrides[get_db] = lambda: db_session
        
        try:
            response = await client.get(
                "/api/v1/admin/users",
                headers={"X-API-Key": api_key}
            )
            
            # Should succeed (200)
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()


# ==================== URL SANITIZATION TESTS ====================

class TestURLSanitization:
    """Test URL sanitization in logs."""

    @pytest.mark.asyncio
    async def test_token_removed_from_logs(self, client):
        """Test that tokens are removed from logged URLs."""
        from app.middleware.security import sanitize_url
        
        url_with_token = "http://example.com/api?token=secret123&foo=bar"
        sanitized = sanitize_url(url_with_token)
        
        assert "token=" not in sanitized
        assert "foo=bar" in sanitized

    @pytest.mark.asyncio
    async def test_api_key_removed_from_logs(self, client):
        """Test that API keys are removed from logged URLs."""
        from app.middleware.security import sanitize_url
        
        url_with_key = "http://example.com/api?api_key=secret&data=123"
        sanitized = sanitize_url(url_with_key)
        
        assert "api_key=" not in sanitized
        assert "data=123" in sanitized

    @pytest.mark.asyncio
    async def test_multiple_sensitive_params_removed(self, client):
        """Test that multiple sensitive parameters are removed."""
        from app.middleware.security import sanitize_url
        
        url = "http://example.com/api?token=abc&password=xyz&api_key=123&normal=value"
        sanitized = sanitize_url(url)
        
        assert "token=" not in sanitized
        assert "password=" not in sanitized
        assert "api_key=" not in sanitized
        assert "normal=value" in sanitized


# ==================== WEBHOOK SECURITY TESTS ====================

class TestWebhookSecurity:
    """Test webhook signature verification."""

    @pytest.mark.asyncio
    async def test_webhook_without_signature_rejected(self, client):
        """CRITICAL: Test webhook without signature is rejected."""
        response = await client.post(
            "/api/v1/payment/webhook",
            json={
                "payment_id": "test123",
                "status": "succeeded",
                "metadata": {}
            }
        )
        
        # Should be rejected (401 - missing signature)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_webhook_with_invalid_signature(self, client):
        """Test webhook with invalid signature is rejected."""
        response = await client.post(
            "/api/v1/payment/webhook",
            json={
                "payment_id": "test123",
                "status": "succeeded",
                "metadata": {}
            },
            headers={"X-Hub-Signature-256": "sha256=invalid"}
        )
        
        # Should be rejected (401 - invalid signature)
        assert response.status_code == 401


# ==================== PATH TRAVERSAL TESTS ====================

class TestPathTraversal:
    """Test path traversal prevention."""

    @pytest.mark.asyncio
    async def test_report_path_traversal_blocked(self, client, test_user, db_session):
        """CRITICAL: Test path traversal in report endpoint."""
        user, api_key = test_user
        
        app = client.app
        app.dependency_overrides[get_db] = lambda: db_session
        
        try:
            # Try path traversal
            response = await client.get(
                "/api/v1/report/../../../etc/passwd",
                headers={"X-API-Key": api_key}
            )
            
            # Should be rejected (400 - invalid format)
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_report_invalid_chars_blocked(self, client, test_user, db_session):
        """Test invalid characters in video_id are blocked."""
        user, api_key = test_user
        
        app = client.app
        app.dependency_overrides[get_db] = lambda: db_session
        
        try:
            # Try with special characters
            response = await client.get(
                "/api/v1/report/video$(id)",
                headers={"X-API-Key": api_key}
            )
            
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_report_valid_video_id_format(self, client, test_user, db_session):
        """Test that valid video_id format is accepted."""
        user, api_key = test_user
        
        app = client.app
        app.dependency_overrides[get_db] = lambda: db_session
        
        try:
            # Valid format but report not found (404, not 400)
            response = await client.get(
                "/api/v1/report/valid_video_id_123",
                headers={"X-API-Key": api_key}
            )
            
            # Should be 404 (not found) not 400 (bad format)
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()


# ==================== SSRF URL VALIDATION TESTS ====================

class TestSSRFValidation:
    """Test SSRF prevention in URL validation."""

    def test_is_safe_url_blocks_internal_ips(self):
        """Test that internal IP addresses are blocked."""
        from app.api.v1.analyze import is_safe_url
        
        # Block internal metadata service
        assert is_safe_url("http://169.254.169.254/latest/meta-data/") == False
        
        # Block localhost
        assert is_safe_url("http://localhost:8080/admin") == False
        assert is_safe_url("http://127.0.0.1:8080") == False
        
        # Block private IPs
        assert is_safe_url("http://192.168.1.1/admin") == False
        assert is_safe_url("http://10.0.0.1/internal") == False
        assert is_safe_url("http://172.16.0.1/admin") == False

    def test_is_safe_url_allows_public_urls(self):
        """Test that public URLs are allowed (syntax validation only)."""
        from app.api.v1.analyze import is_safe_url
        import socket
        
        # Note: DNS resolution may fail in test environment
        # Test URL format validation instead
        try:
            # Try to resolve a domain to test the function
            socket.getaddrinfo("example.com", None)
            # If DNS works, test real URLs
            assert is_safe_url("https://example.com/video") == True
        except socket.gaierror:
            # DNS not available, skip this test
            pytest.skip("DNS resolution not available in test environment")

    def test_is_safe_url_blocks_non_http_schemes(self):
        """Test that non-HTTP schemes are blocked."""
        from app.api.v1.analyze import is_safe_url
        
        assert is_safe_url("file:///etc/passwd") == False
        assert is_safe_url("ftp://example.com/file") == False
        assert is_safe_url("gopher://internal:70/") == False


# ==================== API KEY HASHING TESTS ====================

class TestAPIKeyHashing:
    """Test API key hashing functionality."""

    def test_hash_api_key_consistency(self):
        """Test that API key hashing is consistent."""
        api_key = "test_api_key_123"
        
        hash1 = hash_api_key(api_key)
        hash2 = hash_api_key(api_key)
        
        # Same key should produce same hash
        assert hash1 == hash2

    def test_hash_api_key_different_keys(self):
        """Test that different keys produce different hashes."""
        hash1 = hash_api_key("key1")
        hash2 = hash_api_key("key2")
        
        assert hash1 != hash2

    def test_hash_api_key_format(self):
        """Test that hash is SHA-256 hex format (64 chars)."""
        hash_value = hash_api_key("test_key")
        
        # SHA-256 produces 64 hex characters
        assert len(hash_value) == 64
        assert all(c in '0123456789abcdef' for c in hash_value)


# ==================== SECURITY HEADERS TESTS ====================

class TestSecurityHeaders:
    """Test security headers."""

    @pytest.mark.asyncio
    async def test_security_headers_present(self, client):
        """Test that security headers are present in responses."""
        response = await client.get("/api/v1/health")
        
        assert response.status_code == 200
        
        # Check security headers
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers
