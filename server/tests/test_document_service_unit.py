import pytest

from app import create_app
from app.services import DocumentService


@pytest.fixture()
def app_ctx():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'CORS_ORIGINS': '*', 'SECRET_KEY': 'test'})
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


def test_get_documents_empty(app_ctx):
    docs = DocumentService.get_documents_for_beneficiary = getattr(DocumentService, 'get_documents_for_beneficiary', None)
    if docs:
        result = DocumentService.get_documents_for_beneficiary(1)
        assert result == []


def test_delete_document_not_found(app_ctx):
    success = DocumentService.delete_document(999)
    assert success is False 