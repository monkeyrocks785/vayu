"""
VAYU - NASA Competition Ready Weather App
Enhanced with NASA POWER API Integration for Satellite-Derived Weather Data
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import os
from dotenv import load_dotenv
from models import db, User, WeatherLog
from utils.weather_api import WeatherAPI  # Updated to use NASA integration
from utils.comfort_calculator import ComfortCalculator
from utils.ml_engine import MLEngine
import uuid
from datetime import datetime
import logging

# Configure logging for NASA API
logging.basicConfig(level=logging.INFO)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'vayu-nasa-competition-2025')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, 'database')
os.makedirs(DB_DIR, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(DB_DIR, 'vayu.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_or_create_user():
    if 'user_session_id' not in session:
        session['user_session_id'] = str(uuid.uuid4())
        logger.info(f"New session created")
    
    user = User.query.filter_by(session_id=session['user_session_id']).first()
    if not user:
        browser_id = request.headers.get('User-Agent', '')[:50]
        user = User(
            session_id=session['user_session_id'],
            browser_fingerprint=browser_id
        )
        db.session.add(user)
        logger.info(f"Created new user")
    
    user.last_active = datetime.utcnow()
    
    try:
        db.session.commit()
        logger.info(f"User data saved successfully")
    except Exception as e:
        logger.error(f"Database commit error: {e}")
        db.session.rollback()
    
    return user

@app.route('/')
def index():
    """
    Main weather dashboard with NASA POWER API integration
    Enhanced for NASA competition with satellite-derived weather data
    """
    user = get_or_create_user()
    location = request.args.get('location') or user.location or 'New Delhi'
    
    # Update user's preferred location
    if request.args.get('location'):
        user.location = request.args.get('location')
        db.session.commit()
    
    try:
        # Initialize enhanced weather API with NASA POWER
        weather_api = WeatherAPI()
        
        # Get coordinates
        coords = weather_api.get_coordinates(location)
        if not coords:
            return render_template('index.html', 
                                 error=f"Location '{location}' not found", 
                                 user=user,
                                 api_info=weather_api.get_api_status())
        
        # Fetch weather data (NASA POWER primary, Open-Meteo fallback)
        print(f"🌍 Fetching weather for {coords['name']} ({coords['lat']}, {coords['lon']})")
        weather_data = weather_api.fetch_weather(coords['lat'], coords['lon'], use_nasa=True)
        
        if not weather_data:
            return render_template('index.html', 
                                 error="Weather data temporarily unavailable", 
                                 user=user, 
                                 location=location,
                                 api_info=weather_api.get_api_status())
        
        # Process current weather for VAYU compatibility
        current_weather = {
            'temperature': weather_data['current_weather']['temperature'],
            'windspeed_10m': weather_data['current_weather']['windspeed'],
            'relativehumidity_2m': weather_data['hourly']['relativehumidity_2m'][0] if weather_data.get('hourly') else 50,
            'precipitation_probability': weather_data['hourly']['precipitation_probability'][0] if weather_data.get('hourly') else 0,
            'icon': '🛰️',  # NASA satellite icon
            'description': f"NASA {weather_data.get('api_provider', 'Weather')} Data"
        }
        
        print(f"🌡️ Current weather: {current_weather['temperature']}°C, {current_weather['relativehumidity_2m']}% humidity")
        
        # Calculate comfort score using VAYU algorithm
        comfort_calc = ComfortCalculator(user.__dict__)
        formula_comfort_result = comfort_calc.calculate(current_weather)

        def get_enhanced_precipitation(nasa_data, lat, lon):
            """Combine NASA data with real-time precipitation"""
            
            # Try to get NASA precipitation first
            nasa_precip = 0
            if nasa_data.get('hourly', {}).get('precipitation_probability'):
                nasa_precip = nasa_data['hourly']['precipitation_probability'][0]
            
            # If NASA has no rain data, get real-time
            if nasa_precip == 0:
                try:
                    import requests
                    url = "https://api.open-meteo.com/v1/forecast"
                    params = {
                        'latitude': lat,
                        'longitude': lon,
                        'hourly': 'precipitation_probability',
                        'forecast_days': 1
                    }
                    
                    response = requests.get(url, params=params, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        realtime_precip = data.get('hourly', {}).get('precipitation_probability', [0])[0]
                        print(f"🌧️ Using real-time precipitation: {realtime_precip}%")
                        return realtime_precip
                except:
                    pass
            
            print(f"🌧️ Using NASA precipitation: {nasa_precip}%")
            return nasa_precip

        real_precipitation = get_enhanced_precipitation(weather_data, coords['lat'], coords['lon'])
        current_weather['precipitation_probability'] = real_precipitation

        # Log weather and comfort data for ML learning
        weather_log = WeatherLog(
            user_id=user.id,
            location=coords['name'],
            temperature=current_weather['temperature'],
            humidity=current_weather['relativehumidity_2m'],
            wind_speed=current_weather['windspeed_10m'],
            precipitation=current_weather['precipitation_probability'],
            comfort_score=formula_comfort_result['overall_score']
        )

        db.session.add(weather_log)
        db.session.commit()
        logger.info(f"Weather data logged successfully")
        
        # NASA-enhanced ML prediction
        print("🤖 Training ML model on NASA weather data...")
        ml_engine = MLEngine()
        ml_engine.train_on_all(coords['name'])
        
        ml_predicted = ml_engine.predict_and_store(coords['name'], {
            'temperature': current_weather['temperature'],
            'humidity': current_weather['relativehumidity_2m'],
            'wind_speed': current_weather['windspeed_10m'],
            'precipitation': current_weather['precipitation_probability']
        })
        
        if weather_data.get('api_provider') == 'NASA POWER':
            beta = 0.4  # Higher ML weight for NASA's high-quality satellite data
        else:
            beta = 0.3  # Standard blending for fallback data
            
        final_score = round(beta * ml_predicted + (1 - beta) * formula_comfort_result['overall_score'])
        
        # Enhanced comfort classification
        def classify_comfort_nasa(score):
            """NASA-enhanced comfort classification"""
            if score >= 85:
                return "Excellent Conditions", "green"
            elif score >= 70:
                return "Very Comfortable", "lightgreen"
            elif score >= 55:
                return "Comfortable", "orange"
            elif score >= 35:
                return "Uncomfortable", "red"
            else:
                return "Poor Conditions", "darkred"
        
        comfort_level, comfort_color = classify_comfort_nasa(final_score)
        
        # Update comfort result with NASA-enhanced data
        formula_comfort_result.update({
            'overall_score': final_score,
            'comfort_level': comfort_level,
            'comfort_color': comfort_color,
            'nasa_enhanced': weather_data.get('api_provider') == 'NASA POWER',
            'data_quality': weather_data.get('data_quality', 'standard'),
            'satellite_derived': weather_data.get('data_source') == 'NASA POWER'
        })
        
        # Enhanced weather data for template
        if weather_data.get('api_provider') == 'NASA POWER':
            current_weather.update({
                'feels_like': weather_data.get('feels_like'),
                'solar_irradiance': weather_data.get('solar_irradiance'),
                'dew_point': weather_data.get('dew_point'),
                'icon': '🌤️',
                'description': 'Current conditions' 
            })
        
        print(f"✅ VAYU analysis complete: {final_score}% comfort (NASA-enhanced)")
        
        return render_template('index.html',
                               user=user,
                               location=coords['name'],
                               weather=current_weather,
                               comfort=formula_comfort_result,
                               ml_predicted=ml_predicted,
                               api_info=weather_api.get_api_status(),
                               nasa_enhanced=True)
    
    except Exception as e:
        app.logger.error(f"NASA Weather API Error: {e}", exc_info=True)
        return render_template('index.html', 
                               error="Weather service temporarily unavailable", 
                               user=user, 
                               location=location,
                               api_info={'error': str(e)})

@app.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    user = get_or_create_user()
    
    if request.method == 'POST':
        # TRY-CATCH AROUND SETTINGS SAVE:
        try:
            user.temp_min = int(request.form.get('temp_min', 18))
            user.temp_max = int(request.form.get('temp_max', 26))
            user.humidity_tolerance = request.form.get('humidity_tolerance', 'medium')
            user.wind_tolerance = request.form.get('wind_tolerance', 'medium')
            user.rain_preference = request.form.get('rain_preference', 'neutral')
            user.activity_level = request.form.get('activity_level', 'medium')
            user.settings_completed = True
            
            db.session.commit()
            logger.info(f"Settings saved successfully")
            return redirect(url_for('index'))
            
        except Exception as e:
            logger.error(f"Settings save error: {e}")
            db.session.rollback()
            return render_template('onboarding.html', user=user, error="Failed to save settings")
    
    return render_template('onboarding.html', user=user)


@app.route('/feedback', methods=['POST'])
def feedback():
    user = get_or_create_user()
    feedback_type = request.form.get('feedback')
    
    # ADD TRY-CATCH:
    try:
        recent_log = WeatherLog.query.filter_by(user_id=user.id).order_by(WeatherLog.timestamp.desc()).first()
        
        if recent_log:
            recent_log.user_feedback = feedback_type
            recent_log.feedback_timestamp = datetime.utcnow()
            db.session.commit()
            logger.info(f"Feedback saved: {feedback_type}")
            
            return jsonify({
                'status': 'success',
                'message': 'Thank you! VAYU is learning from your feedback.',
                'nasa_enhanced': True
            })
        
        return jsonify({'status': 'error', 'message': 'No recent weather data found'})
        
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to save feedback'})

@app.route('/api/status')
def api_status():
    """NASA API status endpoint for competition monitoring"""
    weather_api = WeatherAPI()
    return jsonify({
        'vayu_version': '2.0-NASA-Competition',
        'timestamp': datetime.now().isoformat(),
        'apis': weather_api.get_api_status(),
        'nasa_integration': 'active',
        'competition_ready': True
    })

@app.route('/api/test/<location>')
def test_apis(location):
    """Test endpoint to compare NASA vs fallback API data"""
    try:
        weather_api = WeatherAPI()
        coords = weather_api.get_coordinates(location)
        
        if not coords:
            return jsonify({'error': 'Location not found'})
        
        detailed_info = weather_api.get_detailed_weather_info(coords['lat'], coords['lon'])
        
        return jsonify({
            'location': coords,
            'api_comparison': detailed_info,
            'nasa_competition': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

# NASA Competition Enhancement Routes
@app.route('/nasa-info')
def nasa_info():
    """Information page about NASA POWER integration"""
    weather_api = WeatherAPI()
    nasa_api_info = weather_api.nasa_api.get_api_info()
    
    return render_template('nasa_info.html', 
                           api_info=nasa_api_info,
                           competition_info={
                               'vayu_version': '2.0-NASA-Competition',
                               'integration_date': datetime.now().strftime('%Y-%m-%d'),
                               'features': [
                                   'Satellite-derived meteorological data',
                                   'NASA POWER API integration',
                                   'Enhanced comfort predictions',
                                   'ML training on NASA data',
                                   'Global weather coverage',
                                   'Research-grade data quality'
                               ]
                           })

# Initialize database and run app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("🚀 VAYU NASA Competition App Starting...")
        print("🛰️ NASA POWER API Integration: ACTIVE")
        print("🌍 Global Weather Coverage: ENABLED")
        print("🤖 ML Training on NASA Data: READY")
    
    app.run(debug=True, port=5000)