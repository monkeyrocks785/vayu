<<<<<<< HEAD
import pickle, os
from sklearn.linear_model import LinearRegression
from models import WeatherLog, MLPrediction, db

MODEL_PATH = 'comfort_model.pkl'

class MLEngine:
    def __init__(self):
        # Always create a fresh LinearRegression instance
        self.model = LinearRegression()

    def train_on_all(self, location):
        """Retrain on all logged feedback for this location."""
        # Fetch all logs with user_feedback
        logs = WeatherLog.query.filter(
            WeatherLog.location == location,
            WeatherLog.user_feedback.isnot(None)
        ).all()
        
        if not logs:
            return  # No data yet
        
        X = [[log.temperature, log.humidity, log.wind_speed, log.precipitation] for log in logs]
        y = [log.comfort_score for log in logs]

        # Fit the model on the full dataset
        self.model.fit(X, y)

        # Persist model to disk
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(self.model, f)

    def predict_and_store(self, location, weather_conditions):
        """Predict comfort and save to MLPrediction."""
        X_pred = [[
            weather_conditions['temperature'],
            weather_conditions['humidity'],
            weather_conditions['wind_speed'],
            weather_conditions['precipitation']
        ]]
        
        # Load persisted model if exists
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                self.model = pickle.load(f)
        
        # Perform prediction
        pred_score = round(self.model.predict(X_pred)[0])
        # Clamp prediction to [0, 100]
        pred_score = max(0, min(100, pred_score))

        # Save to database
        mlp = MLPrediction(
            location=location,
            predicted_temp=weather_conditions['temperature'],
            predicted_humidity=weather_conditions['humidity'],
            predicted_comfort_avg=pred_score,
            confidence_score=0.0  # You can compute R² or error metrics here
        )
        db.session.add(mlp)
        db.session.commit()

        return pred_score
=======
import pickle, os
from sklearn.linear_model import LinearRegression
from models import WeatherLog, MLPrediction, db

MODEL_PATH = 'comfort_model.pkl'

class MLEngine:
    def __init__(self):
        # Always create a fresh LinearRegression instance
        self.model = LinearRegression()

    def train_on_all(self, location):
        """Retrain on all logged feedback for this location."""
        # Fetch all logs with user_feedback
        logs = WeatherLog.query.filter(
            WeatherLog.location == location,
            WeatherLog.user_feedback.isnot(None)
        ).all()
        
        if not logs:
            return  # No data yet
        
        X = [[log.temperature, log.humidity, log.wind_speed, log.precipitation] for log in logs]
        y = [log.comfort_score for log in logs]

        # Fit the model on the full dataset
        self.model.fit(X, y)

        # Persist model to disk
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(self.model, f)

    def predict_and_store(self, location, weather_conditions):
        """Predict comfort and save to MLPrediction."""
        X_pred = [[
            weather_conditions['temperature'],
            weather_conditions['humidity'],
            weather_conditions['wind_speed'],
            weather_conditions['precipitation']
        ]]
        
        # Load persisted model if exists
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                self.model = pickle.load(f)
        
        # Perform prediction
        pred_score = round(self.model.predict(X_pred)[0])
        # Clamp prediction to [0, 100]
        pred_score = max(0, min(100, pred_score))

        # Save to database
        mlp = MLPrediction(
            location=location,
            predicted_temp=weather_conditions['temperature'],
            predicted_humidity=weather_conditions['humidity'],
            predicted_comfort_avg=pred_score,
            confidence_score=0.0  # You can compute R² or error metrics here
        )
        db.session.add(mlp)
        db.session.commit()

        return pred_score
>>>>>>> 4e64647e8d487574b60f65888c9d2c47f4ce8cd4
