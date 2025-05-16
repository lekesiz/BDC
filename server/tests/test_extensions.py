"""Tests for Flask extensions."""

from app.extensions import db, jwt, ma, cors, cache, mail, limiter


def test_db_configured(app):
    """Test that the database extension is configured."""
    assert db.app is not None


def test_jwt_configured(app):
    """Test that the JWT extension is configured."""
    assert jwt.app is not None


def test_marshmallow_configured(app):
    """Test that the Marshmallow extension is configured."""
    assert ma.app is not None


def test_cors_configured(app):
    """Test that the CORS extension is configured."""
    assert cors._real_app is not None


def test_cache_configured(app):
    """Test that the Cache extension is configured."""
    assert cache.app is not None


def test_mail_configured(app):
    """Test that the Mail extension is configured."""
    assert mail.app is not None


def test_limiter_configured(app):
    """Test that the Rate Limiter extension is configured."""
    assert limiter.app is not None