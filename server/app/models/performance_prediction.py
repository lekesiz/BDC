"""Performance prediction models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db


class PredictionModel(db.Model):
    """Model for storing trained ML models metadata."""
    __tablename__ = 'prediction_models'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)  # linear_regression, classifier, time_series
    target_metric = Column(String(50), nullable=False)  # score_trend, pass_fail, attendance
    version = Column(String(20), nullable=False)
    
    # Model performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    mae = Column(Float)  # Mean Absolute Error for regression
    rmse = Column(Float)  # Root Mean Square Error
    
    # Model metadata
    features_used = Column(JSON)  # List of feature names
    hyperparameters = Column(JSON)  # Model hyperparameters
    training_data_size = Column(Integer)
    validation_data_size = Column(Integer)
    
    # Model storage
    model_path = Column(String(255))  # Path to serialized model
    scaler_path = Column(String(255))  # Path to feature scaler
    
    # Status
    status = Column(String(20), default='active')  # active, inactive, deprecated
    is_default = Column(Boolean, default=False)  # Default model for its type
    
    # Foreign keys
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    trained_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship('Tenant', backref='prediction_models')
    creator = relationship('User', backref='created_prediction_models')
    predictions = relationship('PerformancePrediction', back_populates='model', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'model_type': self.model_type,
            'target_metric': self.target_metric,
            'version': self.version,
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'mae': self.mae,
            'rmse': self.rmse,
            'features_used': self.features_used,
            'hyperparameters': self.hyperparameters,
            'training_data_size': self.training_data_size,
            'validation_data_size': self.validation_data_size,
            'status': self.status,
            'is_default': self.is_default,
            'trained_at': self.trained_at.isoformat() if self.trained_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PerformancePrediction(db.Model):
    """Model for storing individual predictions."""
    __tablename__ = 'performance_predictions'
    
    id = Column(Integer, primary_key=True)
    beneficiary_id = Column(Integer, ForeignKey('beneficiaries.id'), nullable=False)
    model_id = Column(Integer, ForeignKey('prediction_models.id'), nullable=False)
    
    # Prediction details
    prediction_type = Column(String(50), nullable=False)  # score, attendance, completion
    prediction_value = Column(Float, nullable=False)
    confidence_score = Column(Float)  # 0-1 confidence in prediction
    prediction_date = Column(DateTime, nullable=False)  # Date prediction is for
    
    # Additional predictions
    predicted_score = Column(Float)  # For test score predictions
    predicted_attendance_rate = Column(Float)  # For attendance predictions
    completion_probability = Column(Float)  # 0-1 probability of completion
    risk_level = Column(String(20))  # low, medium, high
    
    # Time horizon
    prediction_horizon = Column(String(20))  # week, month, quarter
    
    # Features snapshot
    features_snapshot = Column(JSON)  # Input features used for prediction
    
    # Actual values (for tracking accuracy)
    actual_value = Column(Float)
    actual_date = Column(DateTime)
    prediction_error = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    beneficiary = relationship('Beneficiary', backref='performance_predictions')
    model = relationship('PredictionModel', back_populates='predictions')
    recommendations = relationship('PredictionRecommendation', back_populates='prediction', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert prediction to dictionary."""
        return {
            'id': self.id,
            'beneficiary_id': self.beneficiary_id,
            'model_id': self.model_id,
            'prediction_type': self.prediction_type,
            'prediction_value': self.prediction_value,
            'confidence_score': self.confidence_score,
            'prediction_date': self.prediction_date.isoformat() if self.prediction_date else None,
            'predicted_score': self.predicted_score,
            'predicted_attendance_rate': self.predicted_attendance_rate,
            'completion_probability': self.completion_probability,
            'risk_level': self.risk_level,
            'prediction_horizon': self.prediction_horizon,
            'features_snapshot': self.features_snapshot,
            'actual_value': self.actual_value,
            'actual_date': self.actual_date.isoformat() if self.actual_date else None,
            'prediction_error': self.prediction_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PredictionRecommendation(db.Model):
    """Model for storing recommendations based on predictions."""
    __tablename__ = 'prediction_recommendations'
    
    id = Column(Integer, primary_key=True)
    prediction_id = Column(Integer, ForeignKey('performance_predictions.id'), nullable=False)
    
    # Recommendation details
    recommendation_type = Column(String(50), nullable=False)  # intervention, resource, schedule
    priority = Column(String(20), default='medium')  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Action items
    action_items = Column(JSON)  # List of specific actions
    resources = Column(JSON)  # Recommended resources
    
    # Implementation tracking
    status = Column(String(20), default='pending')  # pending, in_progress, completed, dismissed
    implemented_at = Column(DateTime)
    implemented_by = Column(Integer, ForeignKey('users.id'))
    implementation_notes = Column(Text)
    
    # Effectiveness tracking
    effectiveness_score = Column(Float)  # 0-5 rating
    effectiveness_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prediction = relationship('PerformancePrediction', back_populates='recommendations')
    implementer = relationship('User', backref='implemented_recommendations')
    
    def to_dict(self):
        """Convert recommendation to dictionary."""
        return {
            'id': self.id,
            'prediction_id': self.prediction_id,
            'recommendation_type': self.recommendation_type,
            'priority': self.priority,
            'title': self.title,
            'description': self.description,
            'action_items': self.action_items,
            'resources': self.resources,
            'status': self.status,
            'implemented_at': self.implemented_at.isoformat() if self.implemented_at else None,
            'implemented_by': self.implemented_by,
            'implementation_notes': self.implementation_notes,
            'effectiveness_score': self.effectiveness_score,
            'effectiveness_notes': self.effectiveness_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ModelTrainingHistory(db.Model):
    """Model for tracking model training history."""
    __tablename__ = 'model_training_history'
    
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('prediction_models.id'), nullable=False)
    
    # Training details
    training_start = Column(DateTime, nullable=False)
    training_end = Column(DateTime, nullable=False)
    training_duration = Column(Integer)  # in seconds
    
    # Data details
    data_start_date = Column(DateTime)
    data_end_date = Column(DateTime)
    total_records = Column(Integer)
    feature_count = Column(Integer)
    
    # Performance metrics
    train_score = Column(Float)
    validation_score = Column(Float)
    test_score = Column(Float)
    cross_validation_scores = Column(JSON)
    
    # Training configuration
    algorithm = Column(String(50))
    hyperparameters = Column(JSON)
    feature_importance = Column(JSON)
    
    # Status
    status = Column(String(20))  # completed, failed, interrupted
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    model = relationship('PredictionModel', backref='training_history')
    
    def to_dict(self):
        """Convert training history to dictionary."""
        return {
            'id': self.id,
            'model_id': self.model_id,
            'training_start': self.training_start.isoformat() if self.training_start else None,
            'training_end': self.training_end.isoformat() if self.training_end else None,
            'training_duration': self.training_duration,
            'data_start_date': self.data_start_date.isoformat() if self.data_start_date else None,
            'data_end_date': self.data_end_date.isoformat() if self.data_end_date else None,
            'total_records': self.total_records,
            'feature_count': self.feature_count,
            'train_score': self.train_score,
            'validation_score': self.validation_score,
            'test_score': self.test_score,
            'cross_validation_scores': self.cross_validation_scores,
            'algorithm': self.algorithm,
            'hyperparameters': self.hyperparameters,
            'feature_importance': self.feature_importance,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }