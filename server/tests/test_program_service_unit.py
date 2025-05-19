import pytest

from app import create_app
from app.services.program_service import ProgramService
from app.models.program import Program

@pytest.fixture()
def app_ctx():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


def test_program_service_crud_flow(app_ctx):
    # Initially empty
    assert Program.query.count() == 0

    # Create
    prog = ProgramService.create_program(name='UnitProg', tenant_id=1)
    assert prog.id is not None

    # List
    items = ProgramService.list_programs()
    assert len(items) == 1

    # Get
    fetched = ProgramService.get_program(prog.id)
    assert fetched.name == 'UnitProg'

    # Update
    ProgramService.update_program(fetched, name='UpdatedProg')
    assert fetched.name == 'UpdatedProg'

    # Delete
    ProgramService.delete_program(fetched)
    assert ProgramService.get_program(prog.id) is None 