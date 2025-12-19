"""
VAYU Comfort Calculator
Advanced algorithm for personalized weather comfort scoring
"""

import math
from typing import Dict, Any

class ComfortCalculator:
    """Calculate personalized weather comfort scores"""
    
    def __init__(self, user_profile: Dict[str, Any]):
        self.profile = user_profile
        self.weights = self._calculate_weights()
    
    def calculate(self, weather_data: Dict[str, float]) -> Dict[str, Any]:
        """Calculate comprehensive comfort score"""
        # Extract weather parameters
        temperature = weather_data.get('temperature', 20)
        humidity = weather_data.get('relativehumidity_2m', 50)
        wind_speed = weather_data.get('windspeed_10m', 0)
        precipitation = weather_data.get('precipitation_probability', 0)
        
        # Calculate individual comfort scores
        scores = {
            'temperature': self._temperature_comfort(temperature),
            'humidity': self._humidity_comfort(humidity),
            'wind': self._wind_comfort(wind_speed),
            'precipitation': self._precipitation_comfort(precipitation)
        }
        
        # Calculate weighted overall score
        overall_score = sum(scores[param] * self.weights[param] for param in scores)
        
        # Generate comfort level and color
        comfort_level, comfort_color = self._get_comfort_classification(overall_score)
        
        # Generate personalized recommendations
        recommendations = self._generate_recommendations(
            overall_score, temperature, humidity, wind_speed, precipitation
        )
        
        return {
            'overall_score': round(overall_score),
            'comfort_level': comfort_level,
            'comfort_color': comfort_color,
            'breakdown': {k: round(v) for k, v in scores.items()},
            'recommendations': recommendations,
            'weather_data': {
                'temperature': temperature,
                'humidity': humidity,
                'wind_speed': round(wind_speed * 3.6, 1),  # Convert to km/h
                'precipitation_chance': precipitation
            }
        }
    
    def _temperature_comfort(self, temperature: float) -> float:
        """Calculate temperature comfort score"""
        temp_min = self.profile.get('temp_min', 18)
        temp_max = self.profile.get('temp_max', 26)
        
        if temp_min <= temperature <= temp_max:
            return 100
        
        # Calculate comfort decay outside preferred range
        if temperature < temp_min:
            distance = temp_min - temperature
        else:
            distance = temperature - temp_max
        
        # Exponential decay with activity level adjustment
        activity_factor = {'low': 3, 'medium': 5, 'high': 7}
        factor = activity_factor.get(self.profile.get('activity_level', 'medium'), 5)
        
        return max(0, 100 * math.exp(-distance / factor))
    
    def _humidity_comfort(self, humidity: float) -> float:
        """Calculate humidity comfort score"""
        tolerance = self.profile.get('humidity_tolerance', 'medium')
        
        comfort_ranges = {
            'low': (20, 50),      # Prefers dry conditions
            'medium': (30, 70),   # Moderate humidity
            'high': (40, 85)      # Comfortable with high humidity
        }
        
        min_comfort, max_comfort = comfort_ranges[tolerance]
        
        if min_comfort <= humidity <= max_comfort:
            return 100
        
        # Calculate distance from comfort range
        if humidity < min_comfort:
            distance = min_comfort - humidity
        else:
            distance = humidity - max_comfort
        
        return max(0, 100 - distance * 1.5)
    
    def _wind_comfort(self, wind_speed: float) -> float:
        """Calculate wind comfort score"""
        wind_kmh = wind_speed * 3.6  # Convert to km/h
        tolerance = self.profile.get('wind_tolerance', 'medium')
        
        # Wind comfort thresholds (km/h)
        thresholds = {
            'low': (0, 15),      # Prefers calm conditions
            'medium': (5, 25),   # Light breeze preferred
            'high': (10, 35)     # Enjoys stronger winds
        }
        
        min_wind, max_wind = thresholds[tolerance]
        
        if min_wind <= wind_kmh <= max_wind:
            return 100
        
        if wind_kmh < min_wind:
            return 80  # Too calm
        else:
            excess = wind_kmh - max_wind
            return max(0, 100 - excess * 2.5)
    
    def _precipitation_comfort(self, precipitation: float) -> float:
        """Calculate precipitation comfort score"""
        rain_preference = self.profile.get('rain_preference', 'neutral')
        
        if precipitation <= 20:  # Low chance of rain
            return {'dislike': 100, 'neutral': 95, 'like': 80}[rain_preference]
        elif precipitation <= 50:  # Moderate chance
            return {'dislike': 60, 'neutral': 75, 'like': 90}[rain_preference]
        else:  # High chance of rain
            return {'dislike': 20, 'neutral': 50, 'like': 85}[rain_preference]
    
    def _calculate_weights(self) -> Dict[str, float]:
        """Calculate comfort parameter weights based on activity level"""
        activity = self.profile.get('activity_level', 'medium')
        
        weight_profiles = {
            'low': {     # Indoor-focused
                'temperature': 0.4,
                'humidity': 0.3,
                'wind': 0.1,
                'precipitation': 0.2
            },
            'medium': {  # Balanced outdoor activity
                'temperature': 0.35,
                'humidity': 0.25,
                'wind': 0.15,
                'precipitation': 0.25
            },
            'high': {    # Very active outdoors
                'temperature': 0.3,
                'humidity': 0.2,
                'wind': 0.2,
                'precipitation': 0.3
            }
        }
        
        return weight_profiles[activity]
    
    def _get_comfort_classification(self, score: float) -> tuple:
        """Get comfort level description and color"""
        if score >= 80:
            return "Very Comfortable", "green"
        elif score >= 60:
            return "Comfortable", "lightgreen"
        elif score >= 40:
            return "Moderately Uncomfortable", "orange"
        elif score >= 20:
            return "Uncomfortable", "red"
        else:
            return "Very Uncomfortable", "darkred"
    
    def _generate_recommendations(self, score: float, temp: float, 
                                humidity: float, wind: float, precip: float) -> list:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Score-based general recommendations
        if score >= 80:
            recommendations.append("Perfect weather for all your planned activities!")
        elif score >= 60:
            recommendations.append("Good weather with minor adjustments needed.")
        elif score < 40:
            recommendations.append("Consider indoor activities or take extra precautions.")
        
        # Temperature-specific recommendations
        temp_min = self.profile.get('temp_min', 18)
        temp_max = self.profile.get('temp_max', 26)
        
        if temp < temp_min - 3:
            recommendations.append("Much colder than your preference. Dress warmly!")
        elif temp < temp_min:
            recommendations.append(f"Cooler than your preference ({temp}°C). Light jacket recommended.")
        elif temp > temp_max + 3:
            recommendations.append("Much hotter than your preference. Stay hydrated and seek shade!")
        elif temp > temp_max:
            recommendations.append(f"Warmer than your preference ({temp}°C). Light clothing and hydration advised.")
        
        # Humidity recommendations
        if humidity > 85:
            recommendations.append("Very high humidity. Choose breathable fabrics and stay cool.")
        elif humidity < 25:
            recommendations.append("Very dry conditions. Stay hydrated and use moisturizer.")
        
        # Wind recommendations  
        wind_kmh = wind * 3.6
        if wind_kmh > 30:
            recommendations.append(f"Very windy conditions ({wind_kmh:.0f} km/h). Secure loose items.")
        
        # Precipitation recommendations
        if precip > 70:
            recommendations.append("High chance of rain. Bring umbrella and waterproof gear.")
        elif precip > 40:
            recommendations.append("Possible rain. Consider bringing an umbrella.")
        
        return recommendations if recommendations else ["Weather conditions noted in your assessment."]