"""Performance predictions API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.performance_prediction_service import PerformancePredictionService
from app.models import User
from app.extensions import db
from app.utils.decorators import require_role

from app.utils.logging import logger

bp = Blueprint('performance_predictions', __name__, url_prefix='/api/performance-predictions')
performance_service = PerformancePredictionService()


@bp.route('/train/score-model', methods=['POST'])
@jwt_required()
@require_role(['admin', 'trainer'])
def train_score_model():
    """Train a new score prediction model."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        result = performance_service.train_score_prediction_model(
            tenant_id=user.tenant_id,
            user_id=current_user_id
        )
        
        if result['success']:
            return jsonify({
                'message': 'Score prediction model trained successfully',
                'model_id': result['model_id'],
                'metrics': {
                    'mae': result['mae'],
                    'rmse': result['rmse'],
                    'r2_score': result['r2_score']
                }
            }), 200
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/train/classifier', methods=['POST'])
@jwt_required()
@require_role(['admin', 'trainer'])
def train_classifier():
    """Train a new pass/fail classifier model."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        result = performance_service.train_pass_fail_classifier(
            tenant_id=user.tenant_id,
            user_id=current_user_id
        )
        
        if result['success']:
            return jsonify({
                'message': 'Pass/fail classifier trained successfully',
                'model_id': result['model_id'],
                'metrics': {
                    'accuracy': result['accuracy'],
                    'precision': result['precision'],
                    'recall': result['recall'],
                    'f1_score': result['f1_score']
                }
            }), 200
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/train/attendance-model', methods=['POST'])
@jwt_required()
@require_role(['admin', 'trainer'])
def train_attendance_model():
    """Train a new attendance time series model."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        result = performance_service.train_attendance_time_series_model(
            tenant_id=user.tenant_id,
            user_id=current_user_id
        )
        
        if result['success']:
            return jsonify({
                'message': 'Attendance model trained successfully',
                'model_id': result['model_id'],
                'metrics': {
                    'mae': result['mae'],
                    'rmse': result['rmse']
                }
            }), 200
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/predict/<int:beneficiary_id>', methods=['GET'])
@jwt_required()
def predict_performance(beneficiary_id):
    """Generate performance predictions for a beneficiary."""
    horizon = request.args.get('horizon', 'month')
    
    if horizon not in ['week', 'month', 'quarter']:
        return jsonify({'error': 'Invalid prediction horizon. Use week, month, or quarter'}), 400
    
    try:
        predictions = performance_service.predict_performance(
            beneficiary_id=beneficiary_id,
            prediction_horizon=horizon
        )
        
        return jsonify(predictions), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/history/<int:beneficiary_id>', methods=['GET'])
@jwt_required()
def get_prediction_history(beneficiary_id):
    """Get prediction history for a beneficiary."""
    limit = request.args.get('limit', 10, type=int)
    
    try:
        history = performance_service.get_prediction_history(
            beneficiary_id=beneficiary_id,
            limit=limit
        )
        
        return jsonify({
            'beneficiary_id': beneficiary_id,
            'predictions': history
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/evaluate/<int:model_id>', methods=['POST'])
@jwt_required()
@require_role(['admin', 'trainer'])
def evaluate_model(model_id):
    """Evaluate accuracy of a prediction model."""
    try:
        evaluation = performance_service.evaluate_prediction_accuracy(model_id)
        return jsonify(evaluation), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/update-actuals/<int:beneficiary_id>', methods=['POST'])
@jwt_required()
@require_role(['admin', 'trainer'])
def update_actual_values(beneficiary_id):
    """Update actual values for past predictions."""
    try:
        performance_service.update_actual_values(beneficiary_id)
        return jsonify({
            'message': 'Actual values updated successfully',
            'beneficiary_id': beneficiary_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/features/<int:beneficiary_id>', methods=['GET'])
@jwt_required()
def get_beneficiary_features(beneficiary_id):
    """Get extracted features for a beneficiary."""
    feature_type = request.args.get('type', 'all')
    
    try:
        features_df = performance_service.extract_features(
            beneficiary_id=beneficiary_id,
            feature_type=feature_type
        )
        
        features_dict = features_df.to_dict('records')[0] if not features_df.empty else {}
        
        return jsonify({
            'beneficiary_id': beneficiary_id,
            'feature_type': feature_type,
            'features': features_dict
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500