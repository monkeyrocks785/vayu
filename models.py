"""
VAYU Database Models
Clean, organized database schema for user preferences and weather data
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """User model for storing personalized weather preferences"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    location = db.Column(db.String(100), nullable=True)
    
    # Comfort preferences
    temp_min = db.Column(db.Integer, default=18)
    temp_max = db.Column(db.Integer, default=26)
    humidity_tolerance = db.Column(db.String(20), default='medium')
    wind_tolerance = db.Column(db.String(20), default='medium')
    rain_preference = db.Column(db.String(20), default='neutral')
    activity_level = db.Column(db.String(20), default='medium')
    
    # Timestamps
    browser_fingerprint = db.Column(db.String(100))
    settings_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    weather_logs = db.relationship('WeatherLog', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.session_id[:8]}...>'

class WeatherLog(db.Model):
    """Weather data logging for ML learning and analytics"""
    __tablename__ = 'weather_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    location = db.Column(db.String(100), nullable=False)
    
    # Weather data
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    precipitation = db.Column(db.Float)
    
    # VAYU data
    comfort_score = db.Column(db.Integer)
    user_feedback = db.Column(db.String(20), nullable=True)  # 'good', 'bad', 'accurate'
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<WeatherLog {self.location} - Score: {self.comfort_score}>'

class MLPrediction(db.Model):
    """ML predictions storage for performance tracking"""
    __tablename__ = 'ml_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False, index=True)
    
    # Predictions
    predicted_temp = db.Column(db.Float)
    predicted_humidity = db.Column(db.Float)
    predicted_comfort_avg = db.Column(db.Float)
    confidence_score = db.Column(db.Float)
    
    # Timestamp
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MLPrediction {self.location} - Confidence: {self.confidence_score}>'
