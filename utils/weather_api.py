"""
Updated WeatherAPI for VAYU with NASA POWER Integration
Provides both NASA POWER and Open-Meteo as fallback options
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
import logging
from utils.nasa_power_api import NASAPowerAPI

class WeatherAPI:
    """
    Enhanced Weather API with NASA POWER integration for VAYU competition
    
    Primary: NASA POWER API (satellite-derived meteorological data)
    Fallback: Open-Meteo API (for real-time data when NASA has delays)
    """
    
    def __init__(self):
        self.nasa_api = NASAPowerAPI()
        self.openmeteo_base = "https://api.open-meteo.com/v1"
        self.geocoding_base = "https://geocoding-api.open-meteo.com/v1"
        
        # API preference order
        self.api_providers = {
            'nasa': {
                'name': 'NASA POWER',
                'priority': 1,
                'description': 'Satellite-derived meteorological data'
            },
            'openmeteo': {
                'name': 'Open-Meteo',
                'priority': 2, 
                'description': 'Real-time weather forecasts'
            }
        }
    
    def get_coordinates(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get coordinates for a location using enhanced geocoding
        """
        try:
            # First try NASA POWER's geocoding approach
            coords = self.nasa_api.get_coordinates(location)
            if coords:
                coords['api_source'] = 'NASA POWER compatible'
                return coords
                
            # Fallback to Open-Meteo geocoding
            url = f"{self.geocoding_base}/search"
            params = {
                'name': location,
                'count': 1,
                'language': 'en',
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('results'):
                result = data['results'][0]
                return {
                    'name': result['name'],
                    'lat': result['latitude'], 
                    'lon': result['longitude'],
                    'country': result.get('country', ''),
                    'timezone': result.get('timezone', 'UTC'),
                    'api_source': 'Open-Meteo Geocoding'
                }
                
            return None
            
        except Exception as e:
            logging.error(f"Geocoding error: {e}")
            return None
    
    def fetch_weather(self, lat: float, lon: float, use_nasa: bool = True) -> Optional[Dict[str, Any]]:
        """
        Fetch weather data with NASA POWER as primary source
        
        Args:
            lat: Latitude
            lon: Longitude  
            use_nasa: Whether to try NASA POWER first (default: True)
            
        Returns:
            Comprehensive weather data dictionary
        """
        weather_data = None
        api_used = None
        
        if use_nasa:
            # Try NASA POWER API first
            print("🛰️ Fetching weather from NASA POWER API...")
            try:
                nasa_data = self.nasa_api.fetch_current_weather(lat, lon)
                if nasa_data:
                    weather_data = self._format_nasa_for_vayu(nasa_data, lat, lon)
                    api_used = 'NASA POWER'
                    print("✅ NASA POWER data retrieved successfully")
                else:
                    print("⚠️ NASA POWER data not available, trying fallback...")
            except Exception as e:
                print(f"⚠️ NASA POWER API error: {e}, trying fallback...")
                logging.error(f"NASA POWER API error: {e}")
        
        # Fallback to Open-Meteo if NASA fails or is not preferred
        if not weather_data:
            print("🌐 Fetching weather from Open-Meteo API...")
            try:
                openmeteo_data = self._fetch_openmeteo_weather(lat, lon)
                if openmeteo_data:
                    weather_data = openmeteo_data
                    api_used = 'Open-Meteo'
                    print("✅ Open-Meteo data retrieved successfully")
            except Exception as e:
                print(f"❌ Open-Meteo API error: {e}")
                logging.error(f"Open-Meteo API error: {e}")
                return None
        
        if weather_data:
            # Add API metadata
            weather_data.update({
                'api_provider': api_used,
                'data_timestamp': datetime.now().isoformat(),
                'coordinates': {'lat': lat, 'lon': lon}
            })
            
            # Get hourly forecast
            if api_used == 'NASA POWER':
                hourly = self.nasa_api.get_hourly_forecast(lat, lon)
                if hourly:
                    weather_data['hourly'] = {
                        'time': [h['datetime'] for h in hourly],
                        'temperature_2m': [h['temperature'] for h in hourly],
                        'relativehumidity_2m': [h['humidity'] for h in hourly],
                        'windspeed_10m': [h['wind_speed'] for h in hourly],
                        'precipitation_probability': [h['precipitation'] * 20 for h in hourly]  # Convert to probability
                    }
            else:
                # Add Open-Meteo hourly data (already included)
                pass
                
            print(f"🌤️ Weather data ready from {api_used}")
            return weather_data
            
        print("❌ No weather data available from any source")
        return None
    
    def _format_nasa_for_vayu(self, nasa_data: Dict, lat: float, lon: float) -> Dict[str, Any]:
        """
        Format NASA POWER data for VAYU compatibility
        """
        return {
            'current_weather': {
                'temperature': nasa_data['temperature'],
                'windspeed': nasa_data['wind_speed'],
                'winddirection': 225,  # Default direction
                'weathercode': self._get_weather_code(nasa_data['condition']),
                'is_day': 1,
                'time': datetime.now().isoformat()
            },
            'hourly': {
                # Create synthetic hourly data based on current conditions
                # NASA POWER provides daily data, so we'll interpolate
                'time': [datetime.now().strftime('%Y-%m-%dT%H:00') for h in range(24)],
                'temperature_2m': [nasa_data['temperature'] + (h % 12 - 6) * 0.5 for h in range(24)],
                'relativehumidity_2m': [nasa_data['humidity']] * 24,
                'windspeed_10m': [nasa_data['wind_speed']] * 24,
                'precipitation_probability': [nasa_data['precipitation_probability']] * 24
            },
            'daily': {
                'temperature_2m_max': [nasa_data['temp_max']],
                'temperature_2m_min': [nasa_data['temp_min']],
                'precipitation_sum': [nasa_data['precipitation']]
            },
            # VAYU-specific metadata
            'location': {'lat': lat, 'lon': lon},
            'data_source': nasa_data.get('source', 'NASA POWER'),
            'data_quality': nasa_data.get('data_quality', 'satellite_derived'),
            'feels_like': nasa_data.get('feels_like'),
            'solar_irradiance': nasa_data.get('solar_irradiance'),
            'dew_point': nasa_data.get('dew_point')
        }
    
    def _fetch_openmeteo_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """
        Fetch weather data from Open-Meteo API as fallback
        """
        try:
            url = f"{self.openmeteo_base}/forecast"
            params = {
                'latitude': lat,
                'longitude': lon,
                'current_weather': 'true',
                'hourly': 'temperature_2m,relativehumidity_2m,windspeed_10m,precipitation_probability',
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum',
                'timezone': 'auto'
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Add metadata for Open-Meteo
            data.update({
                'data_source': 'Open-Meteo',
                'data_quality': 'numerical_weather_model',
                'api_provider': 'Open-Meteo'
            })
            
            return data
            
        except Exception as e:
            logging.error(f"Open-Meteo API error: {e}")
            return None
    
    def _get_weather_code(self, condition: str) -> int:
        """
        Convert weather condition to WMO weather code
        """
        condition_codes = {
            'sunny': 0,
            'partly_cloudy': 2,
            'cloudy': 3,
            'rain': 61,
            'heavy_rain': 65,
            'snow': 71,
            'thunderstorm': 95
        }
        return condition_codes.get(condition, 1)
    
    def get_api_status(self) -> Dict[str, Any]:
        """
        Get status of all available weather APIs
        """
        return {
            'primary_api': {
                'name': 'NASA POWER',
                'status': 'active',
                'description': 'Satellite-derived meteorological data',
                'advantages': [
                    'Global satellite coverage',
                    'Research-grade accuracy',
                    'Long historical record', 
                    'Multiple parameters',
                    'NASA quality assurance'
                ],
                'limitations': [
                    '~7 day data delay',
                    'Daily resolution primary',
                    'Processing latency for real-time'
                ]
            },
            'fallback_api': {
                'name': 'Open-Meteo',
                'status': 'active',
                'description': 'Real-time numerical weather prediction',
                'advantages': [
                    'Real-time data',
                    'Hourly forecasts', 
                    'No API limits',
                    'Fast response times'
                ]
            },
            'integration_strategy': 'NASA POWER primary with Open-Meteo fallback',
            'nasa_competition_ready': True
        }
    
    def get_detailed_weather_info(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get comprehensive weather information from both APIs for comparison
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'coordinates': {'lat': lat, 'lon': lon},
            'apis_tested': {}
        }
        
        # Try NASA POWER
        try:
            nasa_data = self.nasa_api.fetch_current_weather(lat, lon)
            if nasa_data:
                result['apis_tested']['nasa_power'] = {
                    'status': 'success',
                    'data_available': True,
                    'parameters_count': len([k for k in nasa_data.keys() if k not in ['source', 'api_version']]),
                    'data_date': nasa_data.get('date'),
                    'sample_data': {
                        'temperature': nasa_data.get('temperature'),
                        'humidity': nasa_data.get('humidity'),
                        'wind_speed': nasa_data.get('wind_speed')
                    }
                }
            else:
                result['apis_tested']['nasa_power'] = {
                    'status': 'no_data',
                    'data_available': False
                }
        except Exception as e:
            result['apis_tested']['nasa_power'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # Try Open-Meteo
        try:
            openmeteo_data = self._fetch_openmeteo_weather(lat, lon)
            if openmeteo_data:
                result['apis_tested']['open_meteo'] = {
                    'status': 'success',
                    'data_available': True,
                    'current_temp': openmeteo_data.get('current_weather', {}).get('temperature'),
                    'forecast_hours': len(openmeteo_data.get('hourly', {}).get('time', []))
                }
            else:
                result['apis_tested']['open_meteo'] = {
                    'status': 'no_data',
                    'data_available': False
                }
        except Exception as e:
            result['apis_tested']['open_meteo'] = {
                'status': 'error', 
                'error': str(e)
            }
        
        return result