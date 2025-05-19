import os
import io
import pytest
from botocore.stub import Stubber

from app import create_app
from app.services.storage_service import storage_service, s3_client, S3_BUCKET, USE_S3

pytestmark = pytest.mark.skipif(not USE_S3, reason="S3 backend not enabled")


@pytest.fixture()
def app_ctx(monkeypatch):
    os.environ['STORAGE_BACKEND'] = 's3'
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    ctx = app.app_context()
    ctx.push()
    # Stub S3
    with Stubber(s3_client) as stubber:
        stubber.add_response('upload_fileobj', {}, {'Bucket': S3_BUCKET, 'Key': 'test.txt'})
        yield app
    ctx.pop()
    os.environ.pop('STORAGE_BACKEND')


def test_save_file_s3(app_ctx):
    fake_file = io.BytesIO(b'hello world')
    fake_file.filename = 'test.txt'
    path, err = storage_service.save_file(fake_file, 'documents', 'document')
    assert err is None
    assert path.startswith('s3://') 