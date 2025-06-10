"""
Predictive Analytics Service

Machine learning-based predictive analytics for the BDC project.
Includes models for user behavior prediction, appointment no-shows,
evaluation outcomes, and performance forecasting.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import joblib
import logging
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.appointment import Appointment
from app.models.evaluation import Evaluation
from app.models.user_activity import UserActivity
from app.extensions import db


@dataclass
class PredictionResult:
    """Prediction result structure"""
    model_name: str
    prediction: Any
    confidence: float
    features_used: List[str]
    timestamp: datetime
    explanation: str


@dataclass
class ModelPerformance:
    """Model performance metrics"""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mse: Optional[float] = None
    r2_score: Optional[float] = None


class PredictiveAnalyticsService:
    """
    Predictive analytics service using machine learning models
    for various business predictions and forecasts.
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.model_performance = {}
        self.logger = logging.getLogger(__name__)
        self.model_cache_duration = timedelta(hours=24)
        self.last_training = {}
        
    async def initialize_models(self):
        """Initialize and train all predictive models"""
        try:
            # Train appointment no-show prediction model
            await self.train_appointment_noshow_model()
            
            # Train user churn prediction model
            await self.train_user_churn_model()
            
            # Train evaluation outcome prediction model
            await self.train_evaluation_outcome_model()
            
            # Train engagement prediction model
            await self.train_engagement_prediction_model()
            
            # Train capacity forecasting model
            await self.train_capacity_forecasting_model()
            
            self.logger.info("All predictive models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing models: {str(e)}")
            raise
    
    async def train_appointment_noshow_model(self):
        """Train model to predict appointment no-shows"""
        model_name = 'appointment_noshow'
        
        try:
            # Prepare training data
            data = await self.prepare_appointment_data()
            
            if len(data) < 100:  # Minimum data requirement
                self.logger.warning("Insufficient data for appointment no-show model")
                return
            
            # Feature engineering
            features = [
                'user_age', 'days_in_advance', 'hour_of_day', 'day_of_week',
                'previous_noshow_count', 'previous_appointment_count',
                'evaluation_score_avg', 'time_since_last_appointment'
            ]
            
            X = data[features].fillna(0)
            y = data['no_show'].astype(int)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            performance = ModelPerformance(
                model_name=model_name,
                accuracy=accuracy_score(y_test, y_pred),
                precision=precision_score(y_test, y_pred, average='weighted'),
                recall=recall_score(y_test, y_pred, average='weighted'),
                f1_score=f1_score(y_test, y_pred, average='weighted')
            )
            
            # Store model and components
            self.models[model_name] = model
            self.scalers[model_name] = scaler
            self.model_performance[model_name] = performance
            self.last_training[model_name] = datetime.utcnow()
            
            self.logger.info(f"Appointment no-show model trained. Accuracy: {performance.accuracy:.3f}")
            
        except Exception as e:
            self.logger.error(f"Error training appointment no-show model: {str(e)}")
            raise
    
    async def train_user_churn_model(self):
        """Train model to predict user churn"""
        model_name = 'user_churn'
        
        try:
            # Prepare training data
            data = await self.prepare_user_churn_data()
            
            if len(data) < 100:
                self.logger.warning("Insufficient data for user churn model")
                return
            
            # Feature engineering
            features = [
                'days_since_registration', 'total_appointments', 'completed_appointments',
                'cancelled_appointments', 'avg_evaluation_score', 'days_since_last_login',
                'total_logins', 'avg_session_duration', 'feature_usage_count'
            ]
            
            X = data[features].fillna(0)
            y = data['churned'].astype(int)
            
            # Split and scale data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            y_pred_binary = (y_pred > 0.5).astype(int)
            
            performance = ModelPerformance(
                model_name=model_name,
                accuracy=accuracy_score(y_test, y_pred_binary),
                precision=precision_score(y_test, y_pred_binary, average='weighted'),
                recall=recall_score(y_test, y_pred_binary, average='weighted'),
                f1_score=f1_score(y_test, y_pred_binary, average='weighted'),
                mse=mean_squared_error(y_test, y_pred),
                r2_score=r2_score(y_test, y_pred)
            )
            
            # Store model and components
            self.models[model_name] = model
            self.scalers[model_name] = scaler
            self.model_performance[model_name] = performance
            self.last_training[model_name] = datetime.utcnow()
            
            self.logger.info(f"User churn model trained. R² Score: {performance.r2_score:.3f}")
            
        except Exception as e:
            self.logger.error(f"Error training user churn model: {str(e)}")
            raise
    
    async def train_evaluation_outcome_model(self):
        """Train model to predict evaluation outcomes"""
        model_name = 'evaluation_outcome'
        
        try:
            # Prepare training data
            data = await self.prepare_evaluation_data()
            
            if len(data) < 50:
                self.logger.warning("Insufficient data for evaluation outcome model")
                return
            
            # Feature engineering
            features = [
                'user_age', 'program_duration', 'previous_evaluation_avg',
                'appointments_completed', 'days_in_program', 'session_attendance_rate'
            ]
            
            X = data[features].fillna(0)
            y = data['score']
            
            # Split and scale data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = LinearRegression()
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            
            performance = ModelPerformance(
                model_name=model_name,
                accuracy=0.0,  # Not applicable for regression
                precision=0.0,  # Not applicable for regression
                recall=0.0,  # Not applicable for regression
                f1_score=0.0,  # Not applicable for regression
                mse=mean_squared_error(y_test, y_pred),
                r2_score=r2_score(y_test, y_pred)
            )
            
            # Store model and components
            self.models[model_name] = model
            self.scalers[model_name] = scaler
            self.model_performance[model_name] = performance
            self.last_training[model_name] = datetime.utcnow()
            
            self.logger.info(f"Evaluation outcome model trained. R² Score: {performance.r2_score:.3f}")
            
        except Exception as e:
            self.logger.error(f"Error training evaluation outcome model: {str(e)}")
            raise
    
    async def train_engagement_prediction_model(self):
        """Train model to predict user engagement levels"""
        model_name = 'engagement_prediction'
        
        try:
            # Prepare training data
            data = await self.prepare_engagement_data()
            
            if len(data) < 50:
                self.logger.warning("Insufficient data for engagement prediction model")
                return
            
            # Feature engineering
            features = [
                'total_logins', 'avg_session_duration', 'pages_visited',
                'appointments_scheduled', 'evaluations_completed',
                'days_since_registration', 'feature_interactions'
            ]
            
            X = data[features].fillna(0)
            y = data['engagement_score']
            
            # Split and scale data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = RandomForestClassifier(
                n_estimators=50,
                max_depth=8,
                random_state=42
            )
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            
            performance = ModelPerformance(
                model_name=model_name,
                accuracy=accuracy_score(y_test, y_pred),
                precision=precision_score(y_test, y_pred, average='weighted'),
                recall=recall_score(y_test, y_pred, average='weighted'),
                f1_score=f1_score(y_test, y_pred, average='weighted')
            )
            
            # Store model and components
            self.models[model_name] = model
            self.scalers[model_name] = scaler
            self.model_performance[model_name] = performance
            self.last_training[model_name] = datetime.utcnow()
            
            self.logger.info(f"Engagement prediction model trained. Accuracy: {performance.accuracy:.3f}")
            
        except Exception as e:
            self.logger.error(f"Error training engagement prediction model: {str(e)}")
            raise
    
    async def train_capacity_forecasting_model(self):
        """Train model to forecast system capacity needs"""
        model_name = 'capacity_forecasting'
        
        try:
            # Prepare training data
            data = await self.prepare_capacity_data()
            
            if len(data) < 30:
                self.logger.warning("Insufficient data for capacity forecasting model")
                return
            
            # Feature engineering for time series
            features = [
                'day_of_week', 'hour_of_day', 'month', 'is_holiday',
                'active_users_lag1', 'active_users_lag7', 'trend'
            ]
            
            X = data[features].fillna(0)
            y = data['active_users']
            
            # Split data (time series split)
            split_point = int(0.8 * len(data))
            X_train, X_test = X[:split_point], X[split_point:]
            y_train, y_test = y[:split_point], y[split_point:]
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            
            performance = ModelPerformance(
                model_name=model_name,
                accuracy=0.0,  # Not applicable for regression
                precision=0.0,  # Not applicable for regression
                recall=0.0,  # Not applicable for regression
                f1_score=0.0,  # Not applicable for regression
                mse=mean_squared_error(y_test, y_pred),
                r2_score=r2_score(y_test, y_pred)
            )
            
            # Store model and components
            self.models[model_name] = model
            self.scalers[model_name] = scaler
            self.model_performance[model_name] = performance
            self.last_training[model_name] = datetime.utcnow()
            
            self.logger.info(f"Capacity forecasting model trained. R² Score: {performance.r2_score:.3f}")
            
        except Exception as e:
            self.logger.error(f"Error training capacity forecasting model: {str(e)}")
            raise
    
    async def predict_appointment_noshow(self, appointment_id: int) -> PredictionResult:
        """Predict if an appointment will be a no-show"""
        model_name = 'appointment_noshow'
        
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found. Please train the model first.")
        
        try:
            # Get appointment data
            features = await self.get_appointment_features(appointment_id)
            
            # Scale features
            scaler = self.scalers[model_name]
            features_scaled = scaler.transform([features])
            
            # Make prediction
            model = self.models[model_name]
            prediction = model.predict(features_scaled)[0]
            confidence = np.max(model.predict_proba(features_scaled)[0])
            
            return PredictionResult(
                model_name=model_name,
                prediction=bool(prediction),
                confidence=confidence,
                features_used=list(features.keys()),
                timestamp=datetime.utcnow(),
                explanation=f"Predicted {'no-show' if prediction else 'will attend'} with {confidence:.1%} confidence"
            )
            
        except Exception as e:
            self.logger.error(f"Error predicting appointment no-show: {str(e)}")
            raise
    
    async def predict_user_churn(self, user_id: int) -> PredictionResult:
        """Predict if a user will churn"""
        model_name = 'user_churn'
        
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found. Please train the model first.")
        
        try:
            # Get user data
            features = await self.get_user_churn_features(user_id)
            
            # Scale features
            scaler = self.scalers[model_name]
            features_scaled = scaler.transform([features])
            
            # Make prediction
            model = self.models[model_name]
            prediction = model.predict(features_scaled)[0]
            confidence = abs(prediction - 0.5) * 2  # Convert to confidence score
            
            churn_probability = prediction
            will_churn = churn_probability > 0.5
            
            return PredictionResult(
                model_name=model_name,
                prediction={'will_churn': will_churn, 'probability': churn_probability},
                confidence=confidence,
                features_used=list(features.keys()),
                timestamp=datetime.utcnow(),
                explanation=f"Churn probability: {churn_probability:.1%}"
            )
            
        except Exception as e:
            self.logger.error(f"Error predicting user churn: {str(e)}")
            raise
    
    async def predict_evaluation_outcome(self, beneficiary_id: int, 
                                       evaluation_type: str) -> PredictionResult:
        """Predict evaluation outcome score"""
        model_name = 'evaluation_outcome'
        
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found. Please train the model first.")
        
        try:
            # Get beneficiary data
            features = await self.get_evaluation_features(beneficiary_id, evaluation_type)
            
            # Scale features
            scaler = self.scalers[model_name]
            features_scaled = scaler.transform([features])
            
            # Make prediction
            model = self.models[model_name]
            predicted_score = model.predict(features_scaled)[0]
            
            # Calculate confidence based on model's historical performance
            performance = self.model_performance[model_name]
            confidence = max(0.5, performance.r2_score if performance.r2_score else 0.5)
            
            return PredictionResult(
                model_name=model_name,
                prediction=max(0, min(100, predicted_score)),  # Clamp to 0-100
                confidence=confidence,
                features_used=list(features.keys()),
                timestamp=datetime.utcnow(),
                explanation=f"Predicted evaluation score: {predicted_score:.1f}"
            )
            
        except Exception as e:
            self.logger.error(f"Error predicting evaluation outcome: {str(e)}")
            raise
    
    async def forecast_capacity_needs(self, forecast_days: int = 7) -> List[PredictionResult]:
        """Forecast capacity needs for the next N days"""
        model_name = 'capacity_forecasting'
        
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found. Please train the model first.")
        
        try:
            forecasts = []
            current_date = datetime.utcnow()
            
            for days_ahead in range(1, forecast_days + 1):
                target_date = current_date + timedelta(days=days_ahead)
                
                # Get features for target date
                features = await self.get_capacity_features(target_date)
                
                # Scale features
                scaler = self.scalers[model_name]
                features_scaled = scaler.transform([features])
                
                # Make prediction
                model = self.models[model_name]
                predicted_users = model.predict(features_scaled)[0]
                
                # Calculate confidence
                performance = self.model_performance[model_name]
                confidence = max(0.5, performance.r2_score if performance.r2_score else 0.5)
                
                forecast = PredictionResult(
                    model_name=model_name,
                    prediction={
                        'date': target_date.isoformat(),
                        'predicted_active_users': max(0, int(predicted_users)),
                        'capacity_utilization': min(100, (predicted_users / 1000) * 100)  # Assuming max capacity of 1000
                    },
                    confidence=confidence,
                    features_used=list(features.keys()),
                    timestamp=datetime.utcnow(),
                    explanation=f"Predicted {int(predicted_users)} active users for {target_date.strftime('%Y-%m-%d')}"
                )
                
                forecasts.append(forecast)
            
            return forecasts
            
        except Exception as e:
            self.logger.error(f"Error forecasting capacity needs: {str(e)}")
            raise
    
    async def get_model_performance(self) -> Dict[str, ModelPerformance]:
        """Get performance metrics for all models"""
        return self.model_performance.copy()
    
    async def retrain_models_if_needed(self):
        """Retrain models if they're outdated"""
        current_time = datetime.utcnow()
        
        for model_name in self.models.keys():
            last_training_time = self.last_training.get(model_name)
            
            if (last_training_time is None or 
                current_time - last_training_time > self.model_cache_duration):
                
                self.logger.info(f"Retraining model: {model_name}")
                
                if model_name == 'appointment_noshow':
                    await self.train_appointment_noshow_model()
                elif model_name == 'user_churn':
                    await self.train_user_churn_model()
                elif model_name == 'evaluation_outcome':
                    await self.train_evaluation_outcome_model()
                elif model_name == 'engagement_prediction':
                    await self.train_engagement_prediction_model()
                elif model_name == 'capacity_forecasting':
                    await self.train_capacity_forecasting_model()
    
    # Data preparation methods
    async def prepare_appointment_data(self) -> pd.DataFrame:
        """Prepare appointment data for model training"""
        with db.session() as session:
            # Get appointment data with user and evaluation information
            appointments = session.query(Appointment).join(User).all()
            
            data = []
            for appointment in appointments:
                # Calculate features
                user_age = (datetime.utcnow() - appointment.user.created_at).days / 365.25
                days_in_advance = (appointment.scheduled_for - appointment.created_at).days
                
                # Get previous appointments for this user
                previous_appointments = session.query(Appointment).filter(
                    and_(Appointment.user_id == appointment.user_id,
                         Appointment.created_at < appointment.created_at)
                ).all()
                
                previous_noshow_count = sum(
                    1 for apt in previous_appointments if apt.status == 'no_show'
                )
                previous_appointment_count = len(previous_appointments)
                
                # Get average evaluation score
                evaluations = session.query(Evaluation).filter(
                    Evaluation.beneficiary_id == appointment.user_id
                ).all()
                
                evaluation_score_avg = np.mean([e.score for e in evaluations]) if evaluations else 0
                
                # Time since last appointment
                last_appointment = max(previous_appointments, 
                                     key=lambda x: x.created_at, 
                                     default=None)
                time_since_last = (appointment.created_at - last_appointment.created_at).days if last_appointment else 0
                
                data.append({
                    'user_age': user_age,
                    'days_in_advance': days_in_advance,
                    'hour_of_day': appointment.scheduled_for.hour,
                    'day_of_week': appointment.scheduled_for.weekday(),
                    'previous_noshow_count': previous_noshow_count,
                    'previous_appointment_count': previous_appointment_count,
                    'evaluation_score_avg': evaluation_score_avg,
                    'time_since_last_appointment': time_since_last,
                    'no_show': appointment.status == 'no_show'
                })
            
            return pd.DataFrame(data)
    
    async def prepare_user_churn_data(self) -> pd.DataFrame:
        """Prepare user churn data for model training"""
        with db.session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            users = session.query(User).filter(User.created_at <= cutoff_date).all()
            
            data = []
            for user in users:
                # Calculate churn (no activity in last 30 days)
                recent_activity = session.query(UserActivity).filter(
                    and_(UserActivity.user_id == user.id,
                         UserActivity.timestamp >= datetime.utcnow() - timedelta(days=30))
                ).first()
                
                churned = recent_activity is None
                
                # Calculate features
                days_since_registration = (datetime.utcnow() - user.created_at).days
                
                appointments = session.query(Appointment).filter(
                    Appointment.user_id == user.id
                ).all()
                
                total_appointments = len(appointments)
                completed_appointments = sum(1 for apt in appointments if apt.status == 'completed')
                cancelled_appointments = sum(1 for apt in appointments if apt.status == 'cancelled')
                
                evaluations = session.query(Evaluation).filter(
                    Evaluation.beneficiary_id == user.id
                ).all()
                
                avg_evaluation_score = np.mean([e.score for e in evaluations]) if evaluations else 0
                
                days_since_last_login = (datetime.utcnow() - user.last_login).days if user.last_login else 9999
                
                activities = session.query(UserActivity).filter(
                    UserActivity.user_id == user.id
                ).all()
                
                total_logins = len(activities)
                avg_session_duration = np.mean([
                    (activity.timestamp - activity.timestamp).seconds for activity in activities
                ]) if activities else 0
                
                feature_usage_count = len(set(activity.activity_type for activity in activities))
                
                data.append({
                    'days_since_registration': days_since_registration,
                    'total_appointments': total_appointments,
                    'completed_appointments': completed_appointments,
                    'cancelled_appointments': cancelled_appointments,
                    'avg_evaluation_score': avg_evaluation_score,
                    'days_since_last_login': days_since_last_login,
                    'total_logins': total_logins,
                    'avg_session_duration': avg_session_duration,
                    'feature_usage_count': feature_usage_count,
                    'churned': churned
                })
            
            return pd.DataFrame(data)
    
    async def prepare_evaluation_data(self) -> pd.DataFrame:
        """Prepare evaluation data for model training"""
        with db.session() as session:
            evaluations = session.query(Evaluation).join(Beneficiary).join(User).all()
            
            data = []
            for evaluation in evaluations:
                # Calculate features
                user_age = (datetime.utcnow() - evaluation.beneficiary.user.created_at).days / 365.25
                
                # Program duration (simulated)
                program_duration = 90  # days
                
                # Previous evaluations
                previous_evaluations = session.query(Evaluation).filter(
                    and_(Evaluation.beneficiary_id == evaluation.beneficiary_id,
                         Evaluation.created_at < evaluation.created_at)
                ).all()
                
                previous_evaluation_avg = np.mean([e.score for e in previous_evaluations]) if previous_evaluations else 0
                
                # Appointments completed
                appointments = session.query(Appointment).filter(
                    and_(Appointment.user_id == evaluation.beneficiary.user_id,
                         Appointment.status == 'completed')
                ).all()
                
                appointments_completed = len(appointments)
                
                days_in_program = (evaluation.created_at - evaluation.beneficiary.created_at).days
                
                # Session attendance rate (simulated)
                session_attendance_rate = 0.85  # 85% attendance
                
                data.append({
                    'user_age': user_age,
                    'program_duration': program_duration,
                    'previous_evaluation_avg': previous_evaluation_avg,
                    'appointments_completed': appointments_completed,
                    'days_in_program': days_in_program,
                    'session_attendance_rate': session_attendance_rate,
                    'score': evaluation.score or 0
                })
            
            return pd.DataFrame(data)
    
    async def prepare_engagement_data(self) -> pd.DataFrame:
        """Prepare engagement data for model training"""
        with db.session() as session:
            users = session.query(User).all()
            
            data = []
            for user in users:
                # Calculate engagement features
                activities = session.query(UserActivity).filter(
                    UserActivity.user_id == user.id
                ).all()
                
                total_logins = len([a for a in activities if a.activity_type == 'login'])
                avg_session_duration = 1200  # seconds (simulated)
                pages_visited = len([a for a in activities if a.activity_type == 'page_view'])
                
                appointments = session.query(Appointment).filter(
                    Appointment.user_id == user.id
                ).all()
                
                appointments_scheduled = len(appointments)
                
                evaluations = session.query(Evaluation).filter(
                    Evaluation.beneficiary_id == user.id
                ).all()
                
                evaluations_completed = len(evaluations)
                
                days_since_registration = (datetime.utcnow() - user.created_at).days
                feature_interactions = len(set(activity.activity_type for activity in activities))
                
                # Calculate engagement score (0-2: low, 3-4: medium, 5+: high)
                engagement_score = min(5, 
                    (total_logins // 10) +
                    (appointments_scheduled // 5) +
                    (evaluations_completed // 3) +
                    (feature_interactions // 2)
                )
                
                data.append({
                    'total_logins': total_logins,
                    'avg_session_duration': avg_session_duration,
                    'pages_visited': pages_visited,
                    'appointments_scheduled': appointments_scheduled,
                    'evaluations_completed': evaluations_completed,
                    'days_since_registration': days_since_registration,
                    'feature_interactions': feature_interactions,
                    'engagement_score': engagement_score
                })
            
            return pd.DataFrame(data)
    
    async def prepare_capacity_data(self) -> pd.DataFrame:
        """Prepare capacity data for model training"""
        # Generate time series data for capacity forecasting
        data = []
        start_date = datetime.utcnow() - timedelta(days=90)
        
        for i in range(90):
            current_date = start_date + timedelta(days=i)
            
            # Simulate active users with patterns
            base_users = 100
            daily_variation = 20 * np.sin(2 * np.pi * i / 7)  # Weekly pattern
            monthly_trend = 5 * i / 30  # Monthly growth
            random_noise = np.random.normal(0, 10)
            
            active_users = max(0, base_users + daily_variation + monthly_trend + random_noise)
            
            # Calculate lag features
            active_users_lag1 = active_users * 0.9 if i > 0 else active_users
            active_users_lag7 = active_users * 0.8 if i > 6 else active_users
            
            data.append({
                'day_of_week': current_date.weekday(),
                'hour_of_day': 12,  # Noon as default
                'month': current_date.month,
                'is_holiday': current_date.weekday() >= 5,  # Weekend as holiday
                'active_users_lag1': active_users_lag1,
                'active_users_lag7': active_users_lag7,
                'trend': i,
                'active_users': active_users
            })
        
        return pd.DataFrame(data)
    
    # Feature extraction methods
    async def get_appointment_features(self, appointment_id: int) -> Dict[str, float]:
        """Extract features for appointment prediction"""
        # This would extract real features from the database
        # For now, returning simulated features
        return {
            'user_age': 35.0,
            'days_in_advance': 7.0,
            'hour_of_day': 14.0,
            'day_of_week': 2.0,
            'previous_noshow_count': 1.0,
            'previous_appointment_count': 5.0,
            'evaluation_score_avg': 85.0,
            'time_since_last_appointment': 30.0
        }
    
    async def get_user_churn_features(self, user_id: int) -> Dict[str, float]:
        """Extract features for user churn prediction"""
        # This would extract real features from the database
        return {
            'days_since_registration': 180.0,
            'total_appointments': 8.0,
            'completed_appointments': 6.0,
            'cancelled_appointments': 1.0,
            'avg_evaluation_score': 82.0,
            'days_since_last_login': 3.0,
            'total_logins': 45.0,
            'avg_session_duration': 1800.0,
            'feature_usage_count': 8.0
        }
    
    async def get_evaluation_features(self, beneficiary_id: int, 
                                    evaluation_type: str) -> Dict[str, float]:
        """Extract features for evaluation outcome prediction"""
        return {
            'user_age': 28.0,
            'program_duration': 90.0,
            'previous_evaluation_avg': 78.0,
            'appointments_completed': 12.0,
            'days_in_program': 60.0,
            'session_attendance_rate': 0.9
        }
    
    async def get_capacity_features(self, target_date: datetime) -> Dict[str, float]:
        """Extract features for capacity forecasting"""
        return {
            'day_of_week': float(target_date.weekday()),
            'hour_of_day': 12.0,
            'month': float(target_date.month),
            'is_holiday': float(target_date.weekday() >= 5),
            'active_users_lag1': 120.0,
            'active_users_lag7': 115.0,
            'trend': 30.0
        }


# Initialize service instance
predictive_analytics_service = PredictiveAnalyticsService()