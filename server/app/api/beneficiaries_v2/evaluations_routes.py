from flask import jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, current_user
from io import BytesIO

from app.middleware.request_context import role_required
from app.services import BeneficiaryService
from app.schemas import EvaluationSchema
from app.models import Evaluation, TestSession, Document

from . import beneficiaries_bp


def _check_tenant_permission(beneficiary):
    if current_user.role != 'tenant_admin':
        return True
    tenant_id = current_user.tenants[0].id if current_user.tenants else None
    return beneficiary.tenant_id == tenant_id


@beneficiaries_bp.route('/<int:beneficiary_id>/evaluations', methods=['GET'])
@jwt_required()
def list_evaluations(beneficiary_id):
    try:
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        if not beneficiary:
            return jsonify({'error': 'not_found', 'message': 'Beneficiary not found'}), 404
        if not _check_tenant_permission(beneficiary):
            return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403

        evaluations = Evaluation.query.filter_by(beneficiary_id=beneficiary_id).all()
        return jsonify({
            'evaluations': EvaluationSchema(many=True).dump(evaluations),
            'total': len(evaluations),
            'completed': sum(1 for e in evaluations if e.status == 'completed'),
        }), 200
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500


@beneficiaries_bp.route('/<int:beneficiary_id>/sessions', methods=['GET'])
@jwt_required()
def list_sessions(beneficiary_id):
    try:
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        if not beneficiary:
            return jsonify({'error': 'not_found', 'message': 'Beneficiary not found'}), 404
        if not _check_tenant_permission(beneficiary):
            return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403

        sessions = TestSession.query.filter_by(beneficiary_id=beneficiary_id).all()
        return jsonify({
            'sessions': [{
                'id': s.id,
                'evaluation_id': s.evaluation_id,
                'start_time': s.start_time.isoformat() if s.start_time else None,
                'end_time': s.end_time.isoformat() if s.end_time else None,
                'status': s.status,
                'score': s.score,
                'duration': s.duration,
                'created_at': s.created_at.isoformat(),
            } for s in sessions],
            'total': len(sessions),
        }), 200
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500


@beneficiaries_bp.route('/<int:beneficiary_id>/progress', methods=['GET'])
@jwt_required()
def beneficiary_progress(beneficiary_id):
    try:
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        if not beneficiary:
            return jsonify({'error': 'not_found', 'message': 'Beneficiary not found'}), 404
        if not _check_tenant_permission(beneficiary):
            return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403

        evaluations = Evaluation.query.filter_by(beneficiary_id=beneficiary_id).all()
        sessions = TestSession.query.filter_by(beneficiary_id=beneficiary_id).all()
        completed = [e for e in evaluations if e.status == 'completed']
        avg_score = sum(s.score for s in sessions if s.score) / len(sessions) if sessions else 0

        return jsonify({
            'overview': {
                'total_evaluations': len(evaluations),
                'completed_evaluations': len(completed),
                'in_progress_evaluations': len([e for e in evaluations if e.status == 'in_progress']),
                'total_sessions': len(sessions),
                'average_score': round(avg_score, 2),
                'completion_rate': round(len(completed) / len(evaluations) * 100, 2) if evaluations else 0,
            },
            'recent_activity': [{
                'type': 'evaluation',
                'title': e.title,
                'date': e.created_at.isoformat(),
                'status': e.status,
            } for e in evaluations[:5]],
        }), 200
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500


@beneficiaries_bp.route('/<int:beneficiary_id>/skills', methods=['GET'])
@jwt_required()
def beneficiary_skills(beneficiary_id):
    try:
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        if not beneficiary or not _check_tenant_permission(beneficiary):
            return jsonify({'error': 'forbidden'}), 403

        skills = [
            {'name': 'Communication', 'level': 75, 'trend': 'up'},
            {'name': 'Problem Solving', 'level': 85, 'trend': 'stable'},
            {'name': 'Leadership', 'level': 60, 'trend': 'up'},
            {'name': 'Teamwork', 'level': 90, 'trend': 'stable'},
            {'name': 'Time Management', 'level': 70, 'trend': 'down'},
        ]
        return jsonify({'skills': skills, 'last_assessment': '2024-01-15', 'next_assessment': '2024-02-15'}), 200
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500


@beneficiaries_bp.route('/<int:beneficiary_id>/comparison', methods=['GET'])
@jwt_required()
def beneficiary_comparison(beneficiary_id):
    try:
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        if not beneficiary or not _check_tenant_permission(beneficiary):
            return jsonify({'error': 'forbidden'}), 403

        return jsonify({
            'comparison': {
                'average_score': {'beneficiary': 85, 'cohort': 78, 'benchmark': 82},
                'completion_rate': {'beneficiary': 90, 'cohort': 85, 'benchmark': 88},
                'skills': {
                    'communication': {'beneficiary': 75, 'cohort': 72},
                    'leadership': {'beneficiary': 85, 'cohort': 80},
                    'problem_solving': {'beneficiary': 90, 'cohort': 83},
                },
            }
        }), 200
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500


@beneficiaries_bp.route('/<int:beneficiary_id>/report', methods=['GET'])
@jwt_required()
def beneficiary_report(beneficiary_id):
    try:
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        if not beneficiary or not _check_tenant_permission(beneficiary):
            return jsonify({'error': 'forbidden'}), 403

        pdf_buffer = BytesIO()
        pdf_buffer.write(b"Mock PDF Report Content")
        pdf_buffer.seek(0)
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'beneficiary_report_{beneficiary_id}.pdf',
        )
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500 