from datetime import datetime
from typing import List, Optional

from flask import current_app

from app.extensions import db
from app.models.program import Program


class ProgramService:
    """Service layer for Program CRUD operations."""

    @staticmethod
    def list_programs(tenant_id: Optional[int] = None) -> List[Program]:
        query = Program.query.filter_by(is_active=True)
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        return query.order_by(Program.created_at.desc()).all()

    @staticmethod
    def get_program(program_id: int) -> Optional[Program]:
        return Program.query.get(program_id)

    @staticmethod
    def create_program(name: str, tenant_id: int, **kwargs) -> Program:
        program = Program(name=name, tenant_id=tenant_id, is_active=True, **kwargs)
        db.session.add(program)
        db.session.commit()
        # Emit real-time event for program creation
        try:
            from app.realtime import emit_to_tenant
            emit_to_tenant(
                tenant_id,
                'program_created',
                {
                    'program': program.to_dict()
                }
            )
        except Exception as e:
            current_app.logger.warning(f"Failed to emit program_created event: {e}")
        return program

    @staticmethod
    def update_program(program: Program, **kwargs) -> Program:
        for key, value in kwargs.items():
            if hasattr(program, key):
                setattr(program, key, value)
        program.updated_at = datetime.utcnow()
        db.session.commit()
        # Emit real-time event for program update
        try:
            from app.realtime import emit_to_tenant
            emit_to_tenant(
                program.tenant_id,
                'program_updated',
                {
                    'program': program.to_dict()
                }
            )
        except Exception as e:
            current_app.logger.warning(f"Failed to emit program_updated event: {e}")
        return program

    @staticmethod
    def delete_program(program: Program) -> None:
        tenant_id = program.tenant_id
        program_id = program.id
        db.session.delete(program)
        db.session.commit()
        # Emit real-time event for program deletion
        try:
            from app.realtime import emit_to_tenant
            emit_to_tenant(
                tenant_id,
                'program_deleted',
                {
                    'program_id': program_id
                }
            )
        except Exception as e:
            current_app.logger.warning(f"Failed to emit program_deleted event: {e}") 