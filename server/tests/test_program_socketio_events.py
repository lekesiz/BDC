from app.services.program_service import ProgramService
import pytest

# A simple stub to capture emitted events
class EmitStub:
    def __init__(self):
        self.calls = []

    def __call__(self, tenant_id, event_name, data):
        self.calls.append((tenant_id, event_name, data))


@pytest.fixture()
def app_with_realtime(monkeypatch):
    from app import create_app
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    emit_stub = EmitStub()
    # Patch emit_to_tenant used inside ProgramService
    monkeypatch.setattr('app.realtime.emit_to_tenant', emit_stub)
    ctx = app.app_context()
    ctx.push()
    yield app, emit_stub
    ctx.pop()


def test_program_events_emitted(app_with_realtime):
    app, emit_stub = app_with_realtime

    # Create
    prog = ProgramService.create_program(name='WSProg', tenant_id=1)
    assert ('program_created' in [c[1] for c in emit_stub.calls])

    # Update
    ProgramService.update_program(prog, name='WSProg2')
    assert ('program_updated' in [c[1] for c in emit_stub.calls])

    # Delete
    ProgramService.delete_program(prog)
    assert ('program_deleted' in [c[1] for c in emit_stub.calls]) 