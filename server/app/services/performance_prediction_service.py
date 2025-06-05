"""Performance prediction service using machine learning."""

import os
import pickle
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from sklearn.feature_selection import SelectKBest, f_regression, f_classif
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
import joblib

from app.models import (
    Beneficiary, Assessment, SessionAttendance, ProgramEnrollment,
    TrainingSession, User
)
from app.models.performance_prediction import (
    PredictionModel, PerformancePrediction, PredictionRecommendation,
    ModelTrainingHistory
)
from app.extensions import db
from app.utils.logger import logger
from app.services.notification_service import NotificationService


class PerformancePredictionService:
    """Service for predicting beneficiary performance using ML."""
    
    def __init__(self):
        """Initialize the performance prediction service."""
        self.models_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'ml_models')
        os.makedirs(self.models_dir, exist_ok=True)
        self.notification_service = NotificationService()
        self.logger = logger
        
    def extract_features(self, beneficiary_id: int, feature_type: str = 'all') -> pd.DataFrame:
        """
        Extract features for a beneficiary from historical data.
        
        Args:
            beneficiary_id: ID of the beneficiary
            feature_type: Type of features to extract ('all', 'scores', 'attendance', 'engagement')
            
        Returns:
            DataFrame with extracted features
        """
        beneficiary = Beneficiary.query.get(beneficiary_id)
        if not beneficiary:
            raise ValueError(f"Beneficiary {beneficiary_id} not found")
        
        features = {}
        
        # Basic demographics
        if feature_type in ['all', 'demographics']:
            features['years_of_experience'] = beneficiary.years_of_experience or 0
            features['education_level_numeric'] = self._encode_education_level(beneficiary.education_level)
            
        # Assessment scores history
        if feature_type in ['all', 'scores']:
            assessments = Assessment.query.filter_by(
                beneficiary_id=beneficiary_id,
                status='graded'
            ).order_by(Assessment.graded_at.desc()).limit(10).all()
            
            if assessments:
                scores = [a.score for a in assessments if a.score is not None]
                features['avg_score'] = np.mean(scores) if scores else 0
                features['max_score'] = np.max(scores) if scores else 0
                features['min_score'] = np.min(scores) if scores else 0
                features['score_std'] = np.std(scores) if len(scores) > 1 else 0
                features['score_trend'] = self._calculate_trend(scores) if len(scores) > 2 else 0
                features['recent_score'] = scores[0] if scores else 0
                features['assessment_count'] = len(assessments)
                features['pass_rate'] = sum(1 for a in assessments if a.passed) / len(assessments)
            else:
                for key in ['avg_score', 'max_score', 'min_score', 'score_std', 
                           'score_trend', 'recent_score', 'assessment_count', 'pass_rate']:
                    features[key] = 0
        
        # Attendance history
        if feature_type in ['all', 'attendance']:
            # Get attendance records for the last 3 months
            three_months_ago = datetime.utcnow() - timedelta(days=90)
            attendance_records = SessionAttendance.query.filter(
                SessionAttendance.beneficiary_id == beneficiary_id,
                SessionAttendance.created_at >= three_months_ago
            ).all()
            
            if attendance_records:
                total_sessions = len(attendance_records)
                present_count = sum(1 for a in attendance_records if a.status == 'present')
                features['attendance_rate'] = present_count / total_sessions if total_sessions > 0 else 0
                features['total_sessions_attended'] = present_count
                features['absence_count'] = sum(1 for a in attendance_records if a.status == 'absent')
                features['excused_absence_count'] = sum(1 for a in attendance_records if a.status == 'excused')
                
                # Calculate attendance trend
                monthly_attendance = self._calculate_monthly_attendance(attendance_records)
                features['attendance_trend'] = self._calculate_trend(monthly_attendance) if len(monthly_attendance) > 1 else 0
            else:
                for key in ['attendance_rate', 'total_sessions_attended', 'absence_count', 
                           'excused_absence_count', 'attendance_trend']:
                    features[key] = 0
        
        # Engagement metrics
        if feature_type in ['all', 'engagement']:
            # Program participation
            enrollments = ProgramEnrollment.query.filter_by(
                beneficiary_id=beneficiary_id
            ).all()
            
            features['enrolled_programs_count'] = len(enrollments)
            features['completed_programs_count'] = sum(1 for e in enrollments if e.status == 'completed')
            features['active_programs_count'] = sum(1 for e in enrollments if e.status == 'active')
            
            if enrollments:
                progress_rates = [e.progress for e in enrollments if e.progress is not None]
                features['avg_progress_rate'] = np.mean(progress_rates) if progress_rates else 0
            else:
                features['avg_progress_rate'] = 0
            
            # Session feedback
            feedback_ratings = [a.rating for a in attendance_records if a.rating is not None] if 'attendance_records' in locals() else []
            features['avg_session_rating'] = np.mean(feedback_ratings) if feedback_ratings else 0
            features['feedback_count'] = len(feedback_ratings)
        
        return pd.DataFrame([features])
    
    def _encode_education_level(self, education_level: str) -> int:
        """Encode education level to numeric value."""
        education_mapping = {
            'high_school': 1,
            'diploma': 2,
            'bachelor': 3,
            'master': 4,
            'phd': 5
        }
        return education_mapping.get(education_level, 0)
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend coefficient from a list of values."""
        if len(values) < 2:
            return 0
        
        x = np.arange(len(values))
        y = np.array(values)
        
        # Calculate linear regression coefficient
        if len(values) > 1:
            coefficients = np.polyfit(x, y, 1)
            return coefficients[0]  # Slope indicates trend
        return 0
    
    def _calculate_monthly_attendance(self, attendance_records: List[SessionAttendance]) -> List[float]:
        """Calculate monthly attendance rates."""
        monthly_data = {}
        
        for record in attendance_records:
            month_key = record.created_at.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {'total': 0, 'present': 0}
            
            monthly_data[month_key]['total'] += 1
            if record.status == 'present':
                monthly_data[month_key]['present'] += 1
        
        # Calculate rates for each month
        rates = []
        for month in sorted(monthly_data.keys()):
            data = monthly_data[month]
            rate = data['present'] / data['total'] if data['total'] > 0 else 0
            rates.append(rate * 100)
        
        return rates
    
    def train_score_prediction_model(self, tenant_id: int, user_id: int) -> Dict[str, Any]:
        """
        Train a linear regression model to predict assessment scores.
        
        Args:
            tenant_id: ID of the tenant
            user_id: ID of the user training the model
            
        Returns:
            Dictionary with training results
        """
        self.logger.info(f"Training score prediction model for tenant {tenant_id}")
        
        # Prepare training data
        X, y, feature_names = self._prepare_score_training_data(tenant_id)
        
        if len(X) < 50:
            return {
                'success': False,
                'error': 'Insufficient data for training. Need at least 50 records.'
            }
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Feature selection
        selector = SelectKBest(f_regression, k=min(10, X_train.shape[1]))
        X_train_selected = selector.fit_transform(X_train_scaled, y_train)
        X_test_selected = selector.transform(X_test_scaled)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        
        # Grid search for hyperparameter tuning
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5, 10]
        }
        
        grid_search = GridSearchCV(model, param_grid, cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)
        grid_search.fit(X_train_selected, y_train)
        
        best_model = grid_search.best_estimator_
        
        # Evaluate model
        y_pred = best_model.predict(X_test_selected)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(best_model, X_train_selected, y_train, cv=5, 
                                   scoring='neg_mean_absolute_error')
        
        # Save model
        model_version = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        model_path = os.path.join(self.models_dir, f'score_predictor_{tenant_id}_{model_version}.pkl')
        scaler_path = os.path.join(self.models_dir, f'score_scaler_{tenant_id}_{model_version}.pkl')
        selector_path = os.path.join(self.models_dir, f'score_selector_{tenant_id}_{model_version}.pkl')
        
        joblib.dump(best_model, model_path)
        joblib.dump(scaler, scaler_path)
        joblib.dump(selector, selector_path)
        
        # Get feature importance
        selected_feature_names = [feature_names[i] for i in selector.get_support(indices=True)]
        feature_importance = dict(zip(selected_feature_names, best_model.feature_importances_))
        
        # Save model metadata
        prediction_model = PredictionModel(
            name=f"Score Predictor v{model_version}",
            model_type='regression',
            target_metric='assessment_score',
            version=model_version,
            accuracy=r2,
            mae=mae,
            rmse=rmse,
            features_used=selected_feature_names,
            hyperparameters=grid_search.best_params_,
            training_data_size=len(X_train),
            validation_data_size=len(X_test),
            model_path=model_path,
            scaler_path=scaler_path,
            tenant_id=tenant_id,
            created_by=user_id,
            is_default=True
        )
        
        db.session.add(prediction_model)
        db.session.commit()
        
        # Log training history
        training_history = ModelTrainingHistory(
            model_id=prediction_model.id,
            training_start=datetime.utcnow() - timedelta(minutes=5),  # Approximate
            training_end=datetime.utcnow(),
            training_duration=300,  # Approximate in seconds
            total_records=len(X),
            feature_count=len(selected_feature_names),
            train_score=r2,
            validation_score=r2,
            test_score=r2,
            cross_validation_scores=cv_scores.tolist(),
            algorithm='RandomForestRegressor',
            hyperparameters=grid_search.best_params_,
            feature_importance=feature_importance,
            status='completed'
        )
        
        db.session.add(training_history)
        db.session.commit()
        
        return {
            'success': True,
            'model_id': prediction_model.id,
            'mae': mae,
            'rmse': rmse,
            'r2_score': r2,
            'cv_scores': cv_scores.tolist(),
            'feature_importance': feature_importance,
            'best_params': grid_search.best_params_
        }
    
    def train_pass_fail_classifier(self, tenant_id: int, user_id: int) -> Dict[str, Any]:
        """
        Train a classification model to predict pass/fail outcomes.
        
        Args:
            tenant_id: ID of the tenant
            user_id: ID of the user training the model
            
        Returns:
            Dictionary with training results
        """
        self.logger.info(f"Training pass/fail classifier for tenant {tenant_id}")
        
        # Prepare training data
        X, y, feature_names = self._prepare_classification_training_data(tenant_id)
        
        if len(X) < 50:
            return {
                'success': False,
                'error': 'Insufficient data for training. Need at least 50 records.'
            }
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Feature selection
        selector = SelectKBest(f_classif, k=min(10, X_train.shape[1]))
        X_train_selected = selector.fit_transform(X_train_scaled, y_train)
        X_test_selected = selector.transform(X_test_scaled)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, class_weight='balanced')
        
        # Grid search for hyperparameter tuning
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5, 10]
        }
        
        grid_search = GridSearchCV(model, param_grid, cv=5, scoring='f1', n_jobs=-1)
        grid_search.fit(X_train_selected, y_train)
        
        best_model = grid_search.best_estimator_
        
        # Evaluate model
        y_pred = best_model.predict(X_test_selected)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        # Save model
        model_version = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        model_path = os.path.join(self.models_dir, f'pass_fail_classifier_{tenant_id}_{model_version}.pkl')
        scaler_path = os.path.join(self.models_dir, f'classifier_scaler_{tenant_id}_{model_version}.pkl')
        selector_path = os.path.join(self.models_dir, f'classifier_selector_{tenant_id}_{model_version}.pkl')
        
        joblib.dump(best_model, model_path)
        joblib.dump(scaler, scaler_path)
        joblib.dump(selector, selector_path)
        
        # Get feature importance
        selected_feature_names = [feature_names[i] for i in selector.get_support(indices=True)]
        feature_importance = dict(zip(selected_feature_names, best_model.feature_importances_))
        
        # Save model metadata
        prediction_model = PredictionModel(
            name=f"Pass/Fail Classifier v{model_version}",
            model_type='classifier',
            target_metric='pass_fail',
            version=model_version,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            features_used=selected_feature_names,
            hyperparameters=grid_search.best_params_,
            training_data_size=len(X_train),
            validation_data_size=len(X_test),
            model_path=model_path,
            scaler_path=scaler_path,
            tenant_id=tenant_id,
            created_by=user_id,
            is_default=True
        )
        
        db.session.add(prediction_model)
        db.session.commit()
        
        return {
            'success': True,
            'model_id': prediction_model.id,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'feature_importance': feature_importance,
            'best_params': grid_search.best_params_,
            'classification_report': classification_report(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
    
    def train_attendance_time_series_model(self, tenant_id: int, user_id: int) -> Dict[str, Any]:
        """
        Train a time series model to predict attendance patterns.
        
        Args:
            tenant_id: ID of the tenant
            user_id: ID of the user training the model
            
        Returns:
            Dictionary with training results
        """
        self.logger.info(f"Training attendance time series model for tenant {tenant_id}")
        
        # Prepare time series data
        attendance_data = self._prepare_attendance_time_series_data(tenant_id)
        
        if len(attendance_data) < 30:
            return {
                'success': False,
                'error': 'Insufficient data for time series analysis. Need at least 30 data points.'
            }
        
        # Split data
        train_size = int(0.8 * len(attendance_data))
        train_data = attendance_data[:train_size]
        test_data = attendance_data[train_size:]
        
        # Train SARIMA model
        try:
            model = SARIMAX(train_data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7))
            fitted_model = model.fit(disp=False)
            
            # Make predictions
            predictions = fitted_model.forecast(steps=len(test_data))
            
            # Calculate metrics
            mae = mean_absolute_error(test_data, predictions)
            rmse = np.sqrt(mean_squared_error(test_data, predictions))
            
            # Save model
            model_version = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            model_path = os.path.join(self.models_dir, f'attendance_timeseries_{tenant_id}_{model_version}.pkl')
            
            joblib.dump(fitted_model, model_path)
            
            # Save model metadata
            prediction_model = PredictionModel(
                name=f"Attendance Time Series v{model_version}",
                model_type='time_series',
                target_metric='attendance_pattern',
                version=model_version,
                mae=mae,
                rmse=rmse,
                features_used=['historical_attendance'],
                hyperparameters={
                    'order': (1, 1, 1),
                    'seasonal_order': (1, 1, 1, 7)
                },
                training_data_size=train_size,
                validation_data_size=len(test_data),
                model_path=model_path,
                tenant_id=tenant_id,
                created_by=user_id,
                is_default=True
            )
            
            db.session.add(prediction_model)
            db.session.commit()
            
            return {
                'success': True,
                'model_id': prediction_model.id,
                'mae': mae,
                'rmse': rmse,
                'aic': fitted_model.aic,
                'bic': fitted_model.bic
            }
            
        except Exception as e:
            self.logger.error(f"Error training time series model: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to train time series model: {str(e)}'
            }
    
    def predict_performance(self, beneficiary_id: int, prediction_horizon: str = 'month') -> Dict[str, Any]:
        """
        Generate comprehensive performance predictions for a beneficiary.
        
        Args:
            beneficiary_id: ID of the beneficiary
            prediction_horizon: Time horizon for predictions ('week', 'month', 'quarter')
            
        Returns:
            Dictionary with predictions and recommendations
        """
        beneficiary = Beneficiary.query.get(beneficiary_id)
        if not beneficiary:
            raise ValueError(f"Beneficiary {beneficiary_id} not found")
        
        # Extract features
        features_df = self.extract_features(beneficiary_id)
        
        predictions = {}
        recommendations = []
        
        # Score prediction
        score_model = PredictionModel.query.filter_by(
            tenant_id=beneficiary.tenant_id,
            model_type='regression',
            target_metric='assessment_score',
            is_default=True,
            status='active'
        ).first()
        
        if score_model:
            score_pred = self._make_score_prediction(score_model, features_df, beneficiary_id, prediction_horizon)
            predictions['score'] = score_pred
            
            # Generate recommendations based on predicted score
            if score_pred['predicted_score'] < 70:
                recommendations.extend(self._generate_score_recommendations(score_pred, beneficiary))
        
        # Pass/fail prediction
        classifier_model = PredictionModel.query.filter_by(
            tenant_id=beneficiary.tenant_id,
            model_type='classifier',
            target_metric='pass_fail',
            is_default=True,
            status='active'
        ).first()
        
        if classifier_model:
            pass_fail_pred = self._make_pass_fail_prediction(classifier_model, features_df, beneficiary_id, prediction_horizon)
            predictions['pass_fail'] = pass_fail_pred
            
            # Generate recommendations for at-risk beneficiaries
            if pass_fail_pred['completion_probability'] < 0.5:
                recommendations.extend(self._generate_completion_recommendations(pass_fail_pred, beneficiary))
        
        # Attendance prediction
        attendance_model = PredictionModel.query.filter_by(
            tenant_id=beneficiary.tenant_id,
            model_type='time_series',
            target_metric='attendance_pattern',
            is_default=True,
            status='active'
        ).first()
        
        if attendance_model:
            attendance_pred = self._make_attendance_prediction(attendance_model, beneficiary_id, prediction_horizon)
            predictions['attendance'] = attendance_pred
            
            # Generate recommendations for low attendance
            if attendance_pred['predicted_attendance_rate'] < 80:
                recommendations.extend(self._generate_attendance_recommendations(attendance_pred, beneficiary))
        
        # Determine overall risk level
        risk_level = self._calculate_risk_level(predictions)
        
        # Save predictions to database
        for pred_type, pred_data in predictions.items():
            prediction = PerformancePrediction(
                beneficiary_id=beneficiary_id,
                model_id=pred_data['model_id'],
                prediction_type=pred_type,
                prediction_value=pred_data.get('prediction_value', 0),
                confidence_score=pred_data.get('confidence_score', 0),
                prediction_date=datetime.utcnow() + self._get_horizon_timedelta(prediction_horizon),
                predicted_score=pred_data.get('predicted_score'),
                predicted_attendance_rate=pred_data.get('predicted_attendance_rate'),
                completion_probability=pred_data.get('completion_probability'),
                risk_level=risk_level,
                prediction_horizon=prediction_horizon,
                features_snapshot=features_df.to_dict('records')[0]
            )
            db.session.add(prediction)
            db.session.flush()
            
            # Save recommendations
            for rec in recommendations:
                if rec['type'] == pred_type:
                    recommendation = PredictionRecommendation(
                        prediction_id=prediction.id,
                        recommendation_type=rec['recommendation_type'],
                        priority=rec['priority'],
                        title=rec['title'],
                        description=rec['description'],
                        action_items=rec.get('action_items', []),
                        resources=rec.get('resources', [])
                    )
                    db.session.add(recommendation)
        
        db.session.commit()
        
        # Send notifications for high-risk beneficiaries
        if risk_level in ['high', 'critical']:
            self._send_risk_notifications(beneficiary, risk_level, predictions, recommendations)
        
        return {
            'beneficiary_id': beneficiary_id,
            'prediction_horizon': prediction_horizon,
            'risk_level': risk_level,
            'predictions': predictions,
            'recommendations': recommendations,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _prepare_score_training_data(self, tenant_id: int) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare training data for score prediction."""
        # Get all beneficiaries with assessments
        beneficiaries = Beneficiary.query.filter_by(tenant_id=tenant_id).all()
        
        X_list = []
        y_list = []
        
        for beneficiary in beneficiaries:
            assessments = Assessment.query.filter_by(
                beneficiary_id=beneficiary.id,
                status='graded'
            ).all()
            
            if len(assessments) >= 2:  # Need at least 2 assessments
                # Extract features for each assessment
                for i in range(1, len(assessments)):
                    features = self.extract_features(beneficiary.id, 'all')
                    X_list.append(features.values[0])
                    y_list.append(assessments[i].score)
        
        if not X_list:
            return np.array([]), np.array([]), []
        
        feature_names = list(features.columns)
        return np.array(X_list), np.array(y_list), feature_names
    
    def _prepare_classification_training_data(self, tenant_id: int) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare training data for pass/fail classification."""
        beneficiaries = Beneficiary.query.filter_by(tenant_id=tenant_id).all()
        
        X_list = []
        y_list = []
        
        for beneficiary in beneficiaries:
            enrollments = ProgramEnrollment.query.filter_by(
                beneficiary_id=beneficiary.id
            ).filter(ProgramEnrollment.status.in_(['completed', 'failed'])).all()
            
            for enrollment in enrollments:
                features = self.extract_features(beneficiary.id, 'all')
                X_list.append(features.values[0])
                y_list.append(1 if enrollment.status == 'completed' else 0)
        
        if not X_list:
            return np.array([]), np.array([]), []
        
        feature_names = list(features.columns)
        return np.array(X_list), np.array(y_list), feature_names
    
    def _prepare_attendance_time_series_data(self, tenant_id: int) -> pd.Series:
        """Prepare attendance time series data."""
        # Get daily attendance rates for the tenant
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=180)  # 6 months of data
        
        attendance_data = {}
        
        # Query all attendance records
        attendance_records = db.session.query(SessionAttendance).join(
            TrainingSession
        ).join(
            Beneficiary
        ).filter(
            Beneficiary.tenant_id == tenant_id,
            SessionAttendance.created_at >= start_date,
            SessionAttendance.created_at <= end_date
        ).all()
        
        # Group by date and calculate daily attendance rate
        for record in attendance_records:
            date_key = record.created_at.date()
            if date_key not in attendance_data:
                attendance_data[date_key] = {'total': 0, 'present': 0}
            
            attendance_data[date_key]['total'] += 1
            if record.status == 'present':
                attendance_data[date_key]['present'] += 1
        
        # Convert to time series
        dates = sorted(attendance_data.keys())
        rates = []
        
        for date in dates:
            data = attendance_data[date]
            rate = (data['present'] / data['total'] * 100) if data['total'] > 0 else 0
            rates.append(rate)
        
        return pd.Series(rates, index=pd.DatetimeIndex(dates))
    
    def _make_score_prediction(self, model: PredictionModel, features_df: pd.DataFrame, 
                              beneficiary_id: int, horizon: str) -> Dict[str, Any]:
        """Make score prediction using trained model."""
        # Load model and preprocessors
        model_obj = joblib.load(model.model_path)
        scaler = joblib.load(model.scaler_path) if model.scaler_path else None
        selector = joblib.load(model.scaler_path.replace('scaler', 'selector')) if model.scaler_path else None
        
        # Preprocess features
        X = features_df.values
        if scaler:
            X = scaler.transform(X)
        if selector:
            X = selector.transform(X)
        
        # Make prediction
        predicted_score = model_obj.predict(X)[0]
        
        # Calculate confidence (based on prediction interval)
        if hasattr(model_obj, 'predict_proba'):
            confidence = max(model_obj.predict_proba(X)[0])
        else:
            # For regression, use a heuristic based on historical accuracy
            confidence = 0.85 if model.mae < 5 else 0.7
        
        return {
            'model_id': model.id,
            'predicted_score': float(predicted_score),
            'confidence_score': float(confidence),
            'prediction_value': float(predicted_score)
        }
    
    def _make_pass_fail_prediction(self, model: PredictionModel, features_df: pd.DataFrame,
                                  beneficiary_id: int, horizon: str) -> Dict[str, Any]:
        """Make pass/fail prediction using trained classifier."""
        # Load model and preprocessors
        model_obj = joblib.load(model.model_path)
        scaler = joblib.load(model.scaler_path) if model.scaler_path else None
        selector = joblib.load(model.scaler_path.replace('scaler', 'selector')) if model.scaler_path else None
        
        # Preprocess features
        X = features_df.values
        if scaler:
            X = scaler.transform(X)
        if selector:
            X = selector.transform(X)
        
        # Make prediction
        prediction = model_obj.predict(X)[0]
        probability = model_obj.predict_proba(X)[0][1]  # Probability of passing
        
        return {
            'model_id': model.id,
            'completion_probability': float(probability),
            'predicted_outcome': 'pass' if prediction == 1 else 'fail',
            'confidence_score': float(max(model_obj.predict_proba(X)[0])),
            'prediction_value': float(probability)
        }
    
    def _make_attendance_prediction(self, model: PredictionModel, beneficiary_id: int,
                                   horizon: str) -> Dict[str, Any]:
        """Make attendance prediction using time series model."""
        # Load model
        model_obj = joblib.load(model.model_path)
        
        # Get recent attendance data for the beneficiary
        attendance_history = self._get_beneficiary_attendance_history(beneficiary_id)
        
        # Make prediction
        horizon_days = {'week': 7, 'month': 30, 'quarter': 90}
        steps = horizon_days.get(horizon, 30)
        
        predictions = model_obj.forecast(steps=steps)
        predicted_rate = np.mean(predictions)
        
        return {
            'model_id': model.id,
            'predicted_attendance_rate': float(predicted_rate),
            'confidence_score': 0.75,  # Time series confidence is harder to calculate
            'prediction_value': float(predicted_rate)
        }
    
    def _get_beneficiary_attendance_history(self, beneficiary_id: int) -> pd.Series:
        """Get attendance history for a specific beneficiary."""
        # Get last 30 days of attendance
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        attendance_records = SessionAttendance.query.filter(
            SessionAttendance.beneficiary_id == beneficiary_id,
            SessionAttendance.created_at >= start_date,
            SessionAttendance.created_at <= end_date
        ).order_by(SessionAttendance.created_at).all()
        
        # Convert to daily rates
        daily_data = {}
        for record in attendance_records:
            date = record.created_at.date()
            if date not in daily_data:
                daily_data[date] = {'total': 0, 'present': 0}
            
            daily_data[date]['total'] += 1
            if record.status == 'present':
                daily_data[date]['present'] += 1
        
        # Create time series
        dates = pd.date_range(start_date, end_date, freq='D')
        rates = []
        
        for date in dates:
            date_key = date.date()
            if date_key in daily_data:
                data = daily_data[date_key]
                rate = (data['present'] / data['total'] * 100) if data['total'] > 0 else 100
            else:
                rate = 100  # No sessions means full attendance
            rates.append(rate)
        
        return pd.Series(rates, index=dates)
    
    def _calculate_risk_level(self, predictions: Dict[str, Any]) -> str:
        """Calculate overall risk level based on predictions."""
        risk_score = 0
        
        # Score-based risk
        if 'score' in predictions:
            predicted_score = predictions['score'].get('predicted_score', 100)
            if predicted_score < 50:
                risk_score += 3
            elif predicted_score < 70:
                risk_score += 2
            elif predicted_score < 80:
                risk_score += 1
        
        # Completion probability risk
        if 'pass_fail' in predictions:
            completion_prob = predictions['pass_fail'].get('completion_probability', 1)
            if completion_prob < 0.3:
                risk_score += 3
            elif completion_prob < 0.5:
                risk_score += 2
            elif completion_prob < 0.7:
                risk_score += 1
        
        # Attendance risk
        if 'attendance' in predictions:
            attendance_rate = predictions['attendance'].get('predicted_attendance_rate', 100)
            if attendance_rate < 60:
                risk_score += 3
            elif attendance_rate < 75:
                risk_score += 2
            elif attendance_rate < 85:
                risk_score += 1
        
        # Determine risk level
        if risk_score >= 7:
            return 'critical'
        elif risk_score >= 5:
            return 'high'
        elif risk_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _get_horizon_timedelta(self, horizon: str) -> timedelta:
        """Get timedelta for prediction horizon."""
        horizon_map = {
            'week': timedelta(days=7),
            'month': timedelta(days=30),
            'quarter': timedelta(days=90)
        }
        return horizon_map.get(horizon, timedelta(days=30))
    
    def _generate_score_recommendations(self, prediction: Dict[str, Any], 
                                      beneficiary: Beneficiary) -> List[Dict[str, Any]]:
        """Generate recommendations for low predicted scores."""
        recommendations = []
        predicted_score = prediction.get('predicted_score', 0)
        
        if predicted_score < 50:
            recommendations.append({
                'type': 'score',
                'recommendation_type': 'intervention',
                'priority': 'high',
                'title': 'Intensive Support Required',
                'description': f'Predicted score of {predicted_score:.1f}% indicates significant learning challenges. Immediate intervention recommended.',
                'action_items': [
                    'Schedule one-on-one tutoring sessions',
                    'Review fundamental concepts',
                    'Provide additional practice materials',
                    'Consider alternative assessment methods'
                ],
                'resources': [
                    'Basic concept review materials',
                    'Practice question banks',
                    'Video tutorials for difficult topics'
                ]
            })
        elif predicted_score < 70:
            recommendations.append({
                'type': 'score',
                'recommendation_type': 'resource',
                'priority': 'medium',
                'title': 'Additional Learning Resources Recommended',
                'description': f'Predicted score of {predicted_score:.1f}% suggests need for supplementary materials.',
                'action_items': [
                    'Assign extra practice exercises',
                    'Encourage participation in study groups',
                    'Monitor progress weekly'
                ],
                'resources': [
                    'Supplementary reading materials',
                    'Online practice tests',
                    'Peer study group contacts'
                ]
            })
        
        return recommendations
    
    def _generate_completion_recommendations(self, prediction: Dict[str, Any],
                                           beneficiary: Beneficiary) -> List[Dict[str, Any]]:
        """Generate recommendations for at-risk beneficiaries."""
        recommendations = []
        completion_prob = prediction.get('completion_probability', 0)
        
        if completion_prob < 0.3:
            recommendations.append({
                'type': 'pass_fail',
                'recommendation_type': 'intervention',
                'priority': 'critical',
                'title': 'High Risk of Program Failure',
                'description': f'Only {completion_prob*100:.1f}% chance of completion. Urgent intervention required.',
                'action_items': [
                    'Schedule immediate counseling session',
                    'Identify and address barriers to success',
                    'Consider program modification or alternative pathways',
                    'Increase check-in frequency to daily'
                ],
                'resources': [
                    'Academic counseling services',
                    'Success coaching program',
                    'Alternative learning pathways'
                ]
            })
        elif completion_prob < 0.5:
            recommendations.append({
                'type': 'pass_fail',
                'recommendation_type': 'intervention',
                'priority': 'high',
                'title': 'At Risk of Non-Completion',
                'description': f'Completion probability of {completion_prob*100:.1f}% indicates significant risk.',
                'action_items': [
                    'Implement weekly progress reviews',
                    'Provide mentorship support',
                    'Address any personal challenges affecting performance'
                ],
                'resources': [
                    'Mentorship program enrollment',
                    'Time management workshops',
                    'Stress management resources'
                ]
            })
        
        return recommendations
    
    def _generate_attendance_recommendations(self, prediction: Dict[str, Any],
                                           beneficiary: Beneficiary) -> List[Dict[str, Any]]:
        """Generate recommendations for attendance issues."""
        recommendations = []
        predicted_rate = prediction.get('predicted_attendance_rate', 0)
        
        if predicted_rate < 60:
            recommendations.append({
                'type': 'attendance',
                'recommendation_type': 'intervention',
                'priority': 'high',
                'title': 'Severe Attendance Issues Expected',
                'description': f'Predicted attendance rate of {predicted_rate:.1f}% requires immediate action.',
                'action_items': [
                    'Contact beneficiary to understand attendance barriers',
                    'Consider flexible scheduling options',
                    'Implement attendance improvement plan',
                    'Set up automated attendance reminders'
                ],
                'resources': [
                    'Flexible learning options',
                    'Transportation assistance programs',
                    'Remote attendance technology'
                ]
            })
        elif predicted_rate < 80:
            recommendations.append({
                'type': 'attendance',
                'recommendation_type': 'schedule',
                'priority': 'medium',
                'title': 'Attendance Improvement Needed',
                'description': f'Predicted attendance of {predicted_rate:.1f}% is below minimum requirements.',
                'action_items': [
                    'Send attendance reminders before each session',
                    'Discuss importance of regular attendance',
                    'Identify and address scheduling conflicts'
                ],
                'resources': [
                    'Attendance tracking tools',
                    'Session recording for missed classes',
                    'Make-up session scheduling'
                ]
            })
        
        return recommendations
    
    def _send_risk_notifications(self, beneficiary: Beneficiary, risk_level: str,
                                predictions: Dict[str, Any], recommendations: List[Dict[str, Any]]):
        """Send notifications for high-risk beneficiaries."""
        # Notify trainer
        if beneficiary.trainer:
            self.notification_service.create_notification(
                user_id=beneficiary.trainer_id,
                type='alert',
                title=f'High Risk Alert: {beneficiary.user.first_name} {beneficiary.user.last_name}',
                message=f'Performance predictions indicate {risk_level} risk level. Immediate attention required.',
                data={
                    'beneficiary_id': beneficiary.id,
                    'risk_level': risk_level,
                    'predictions': predictions,
                    'recommendation_count': len(recommendations)
                }
            )
        
        # Notify program coordinators
        enrollments = ProgramEnrollment.query.filter_by(
            beneficiary_id=beneficiary.id,
            status='active'
        ).all()
        
        for enrollment in enrollments:
            if enrollment.program.created_by_id:
                self.notification_service.create_notification(
                    user_id=enrollment.program.created_by_id,
                    type='alert',
                    title=f'At-Risk Student Alert',
                    message=f'{beneficiary.user.first_name} {beneficiary.user.last_name} in {enrollment.program.name} needs intervention.',
                    data={
                        'beneficiary_id': beneficiary.id,
                        'program_id': enrollment.program_id,
                        'risk_level': risk_level
                    }
                )
    
    def get_prediction_history(self, beneficiary_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get prediction history for a beneficiary."""
        predictions = PerformancePrediction.query.filter_by(
            beneficiary_id=beneficiary_id
        ).order_by(PerformancePrediction.created_at.desc()).limit(limit).all()
        
        return [pred.to_dict() for pred in predictions]
    
    def evaluate_prediction_accuracy(self, model_id: int) -> Dict[str, Any]:
        """Evaluate accuracy of past predictions."""
        model = PredictionModel.query.get(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        # Get predictions with actual values
        predictions = PerformancePrediction.query.filter(
            PerformancePrediction.model_id == model_id,
            PerformancePrediction.actual_value.isnot(None)
        ).all()
        
        if not predictions:
            return {
                'model_id': model_id,
                'evaluated_predictions': 0,
                'message': 'No predictions with actual values to evaluate'
            }
        
        # Calculate accuracy metrics
        predicted_values = [p.prediction_value for p in predictions]
        actual_values = [p.actual_value for p in predictions]
        
        mae = mean_absolute_error(actual_values, predicted_values)
        rmse = np.sqrt(mean_squared_error(actual_values, predicted_values))
        
        # Update prediction errors
        for prediction in predictions:
            prediction.prediction_error = abs(prediction.prediction_value - prediction.actual_value)
        
        db.session.commit()
        
        return {
            'model_id': model_id,
            'evaluated_predictions': len(predictions),
            'mae': mae,
            'rmse': rmse,
            'avg_error_percentage': np.mean([p.prediction_error / p.actual_value * 100 
                                            for p in predictions if p.actual_value > 0])
        }
    
    def update_actual_values(self, beneficiary_id: int):
        """Update actual values for past predictions."""
        # Get recent predictions
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        predictions = PerformancePrediction.query.filter(
            PerformancePrediction.beneficiary_id == beneficiary_id,
            PerformancePrediction.prediction_date <= datetime.utcnow(),
            PerformancePrediction.actual_value.is_(None),
            PerformancePrediction.created_at >= cutoff_date
        ).all()
        
        for prediction in predictions:
            if prediction.prediction_type == 'score':
                # Get actual assessment scores
                assessments = Assessment.query.filter(
                    Assessment.beneficiary_id == beneficiary_id,
                    Assessment.graded_at >= prediction.created_at,
                    Assessment.graded_at <= prediction.prediction_date + timedelta(days=7)
                ).all()
                
                if assessments:
                    actual_score = np.mean([a.score for a in assessments if a.score is not None])
                    prediction.actual_value = actual_score
                    prediction.actual_date = datetime.utcnow()
                    
            elif prediction.prediction_type == 'attendance':
                # Get actual attendance rate
                attendance_records = SessionAttendance.query.filter(
                    SessionAttendance.beneficiary_id == beneficiary_id,
                    SessionAttendance.created_at >= prediction.created_at,
                    SessionAttendance.created_at <= prediction.prediction_date
                ).all()
                
                if attendance_records:
                    present_count = sum(1 for a in attendance_records if a.status == 'present')
                    actual_rate = (present_count / len(attendance_records) * 100) if attendance_records else 0
                    prediction.actual_value = actual_rate
                    prediction.actual_date = datetime.utcnow()
        
        db.session.commit()