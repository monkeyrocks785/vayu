"""
NASA POWER API Weather Service for VAYU
Integrates with NASA's Prediction of Worldwide Energy Resources (POWER) API
for comprehensive meteorological data from satellite observations.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
import logging

class NASAPowerAPI:
    """
    NASA POWER API client for meteorological data
    
    The POWER API provides global meteorological data from satellite observations
    and assimilation models, perfect for weather applications and climate analysis.
    """
    
    def __init__(self):
        self.base_url = "https://power.larc.nasa.gov/api/temporal"
        self.parameters = {
            # Temperature parameters
            'T2M': 'Temperature at 2 Meters (°C)',
            'T2M_MIN': 'Minimum Temperature at 2 Meters (°C)', 
            'T2M_MAX': 'Maximum Temperature at 2 Meters (°C)',
            'T2MDEW': 'Dew Point Temperature at 2 Meters (°C)',
            
            # Humidity and Precipitation
            'RH2M': 'Relative Humidity at 2 Meters (%)',
            'QV2M': 'Specific Humidity at 2 Meters (g/kg)',
            'PRECTOTCORR': 'Precipitation Corrected (mm/day)',
            
            # Wind parameters
            'WS2M': 'Wind Speed at 2 Meters (m/s)',
            'WD2M': 'Wind Direction at 2 Meters (Degrees)',
            'WS10M': 'Wind Speed at 10 Meters (m/s)',
            
            # Pressure and Solar
            'PS': 'Surface Pressure (kPa)',
            'ALLSKY_SFC_SW_DWN': 'All Sky Surface Shortwave Downward Irradiance (kW-hr/m^2/day)',
            'CLRSKY_SFC_SW_DWN': 'Clear Sky Surface Shortwave Downward Irradiance (kW-hr/m^2/day)'
        }
        
        # Communities available in NASA POWER
        self.communities = {
            'ag': 'Agroclimatology',
            're': 'Renewable Energy', 
            'sb': 'Sustainable Buildings'
        }
    
    def get_coordinates(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get coordinates for a location using NASA's geocoding approach
        For now, we'll use a simple geocoding service, but NASA recommends
        using their coordinate validation
        """
        try:
            # Using a basic geocoding service - in production you'd want
            # to integrate with NASA's coordinate validation
            geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search"
            params = {
                'name': location,
                'count': 1,
                'language': 'en',
                'format': 'json'
            }
            
            response = requests.get(geocoding_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('results'):
                result = data['results'][0]
                return {
                    'name': result['name'],
                    'lat': result['latitude'],
                    'lon': result['longitude'],
                    'country': result.get('country', ''),
                    'timezone': result.get('timezone', 'UTC')
                }
            return None
            
        except Exception as e:
            logging.error(f"Geocoding error: {e}")
            return None
    
    def fetch_current_weather(self, lat: float, lon: float, 
                            community: str = 'ag') -> Optional[Dict[str, Any]]:
        """
        Fetch current weather data from NASA POWER API
        
        Args:
            lat: Latitude 
            lon: Longitude
            community: NASA POWER community ('ag', 're', 'sb')
            
        Returns:
            Dictionary containing current weather data
        """
        try:
            # Get recent data (NASA POWER has ~3 month delay for final data)
            end_date = datetime.now() - timedelta(days=7)  # Account for data delay
            start_date = end_date - timedelta(days=1)
            
            # NASA POWER API endpoint for daily data
            url = f"{self.base_url}/daily/point"
            
            # Essential parameters for weather comfort calculation
            parameters = [
                'T2M',           # Temperature at 2m
                'T2M_MIN',       # Minimum temperature  
                'T2M_MAX',       # Maximum temperature
                'RH2M',          # Relative humidity
                'WS2M',          # Wind speed at 2m
                'PRECTOTCORR',   # Precipitation
                'PS',            # Surface pressure
                'T2MDEW',        # Dew point
                'ALLSKY_SFC_SW_DWN'  # Solar irradiance
            ]
            
            # Build API request
            params = {
                'parameters': ','.join(parameters),
                'community': community,
                'longitude': lon,
                'latitude': lat,
                'start': start_date.strftime('%Y%m%d'),
                'end': end_date.strftime('%Y%m%d'),
                'format': 'JSON'
            }
            
            print(f"NASA POWER API Request: {url}")
            print(f"Parameters: {params}")
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'properties' not in data or 'parameter' not in data['properties']:
                print(f"Unexpected NASA POWER API response structure: {data}")
                return None
            
            # Extract the most recent day's data
            parameters_data = data['properties']['parameter']
            dates = list(parameters_data.get('T2M', {}).keys())
            
            if not dates:
                print("No temperature data available from NASA POWER")
                return None
            
            latest_date = max(dates)
            print(f"Using NASA POWER data from: {latest_date}")
            
            # Process weather data for VAYU
            weather_data = self._process_nasa_data(parameters_data, latest_date)
            
            # Add metadata
            weather_data.update({
                'source': 'NASA POWER',
                'api_version': 'v1',
                'community': community,
                'date': latest_date,
                'coordinates': {'lat': lat, 'lon': lon},
                'data_quality': 'satellite_derived'
            })
            
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logging.error(f"NASA POWER API request failed: {e}")
            return None
        except Exception as e:
            logging.error(f"NASA POWER data processing error: {e}")
            return None
    
    def _process_nasa_data(self, parameters_data: Dict, date: str) -> Dict[str, Any]:
        """
        Process NASA POWER API response into VAYU weather format
        """
        def safe_get(param: str, default: float = 0.0) -> float:
            """Safely extract parameter value"""
            try:
                value = parameters_data.get(param, {}).get(date, default)
                return float(value) if value is not None else default
            except (TypeError, ValueError):
                return default
        
        # Extract core weather parameters
        temperature = safe_get('T2M', 20.0)
        temp_min = safe_get('T2M_MIN', temperature - 5)
        temp_max = safe_get('T2M_MAX', temperature + 5)
        humidity = safe_get('RH2M', 50.0)
        wind_speed = safe_get('WS2M', 0.0)
        precipitation = safe_get('PRECTOTCORR', 0.0)  # mm/day
        pressure = safe_get('PS', 101.3)  # kPa
        dew_point = safe_get('T2MDEW', temperature - 10)
        solar_irradiance = safe_get('ALLSKY_SFC_SW_DWN', 5.0)
        
        if precipitation <= 0.1:
            precipitation_probability = 0
        elif precipitation <= 1.0:
            precipitation_probability = 15  # Light chance
        elif precipitation <= 5.0:
            precipitation_probability = 35  # Moderate chance  
        elif precipitation <= 10.0:
            precipitation_probability = 60  # High chance
        else:
            precipitation_probability = 85  # Very high chance
        
        # Calculate additional parameters
        precipitation_probability = min(precipitation * 10, 100)  # Convert to percentage
        feels_like = self._calculate_feels_like(temperature, humidity, wind_speed)
        weather_condition = self._determine_weather_condition(
            temperature, humidity, precipitation, solar_irradiance
        )
        
        # Format for VAYU compatibility
        return {
            'temperature': round(temperature, 1),
            'temp_min': round(temp_min, 1),
            'temp_max': round(temp_max, 1),
            'humidity': round(humidity, 1),
            'relativehumidity_2m': round(humidity, 1),  # VAYU compatibility
            'wind_speed': round(wind_speed, 1),
            'windspeed_10m': round(wind_speed, 1),  # VAYU compatibility  
            'precipitation': round(precipitation, 2),
            'precipitation_probability': round(precipitation_probability, 1),
            'pressure': round(pressure, 1),
            'dew_point': round(dew_point, 1),
            'feels_like': round(feels_like, 1),
            'solar_irradiance': round(solar_irradiance, 2),
            'icon': weather_condition['icon'],
            'description': weather_condition['description'],
            'condition': weather_condition['condition'],
            'data_source': 'NASA POWER Satellite Data'
        }
    
    def _calculate_feels_like(self, temp: float, humidity: float, wind_speed: float) -> float:
        """
        Calculate feels-like temperature using heat index and wind chill
        Based on meteorological formulas
        """
        if temp >= 27:  # Heat index for hot weather
            # Simplified heat index calculation
            hi = temp + (0.4 * (temp - 10) * humidity / 100)
            return hi
        elif temp <= 10 and wind_speed > 1.3:  # Wind chill for cold weather
            # Simplified wind chill calculation  
            wc = 13.12 + 0.6215 * temp - 11.37 * (wind_speed * 3.6) ** 0.16 + 0.3965 * temp * (wind_speed * 3.6) ** 0.16
            return wc
        else:
            return temp
    
    def _determine_weather_condition(self, temp: float, humidity: float, 
                                   precipitation: float, solar: float) -> Dict[str, str]:
        """
        Determine weather condition based on NASA POWER parameters
        """
        if precipitation > 5:
            if temp < 0:
                return {'condition': 'snow', 'icon': '❄️', 'description': 'Snow'}
            elif precipitation > 15:
                return {'condition': 'heavy_rain', 'icon': '🌧️', 'description': 'Heavy Rain'}
            else:
                return {'condition': 'rain', 'icon': '🌦️', 'description': 'Light Rain'}
        
        elif solar < 2:  # Low solar irradiance
            return {'condition': 'cloudy', 'icon': '☁️', 'description': 'Cloudy'}
        
        elif solar > 8:  # High solar irradiance
            return {'condition': 'sunny', 'icon': '☀️', 'description': 'Sunny'}
        
        else:  # Moderate conditions
            return {'condition': 'partly_cloudy', 'icon': '⛅', 'description': 'Partly Cloudy'}
    
    def get_hourly_forecast(self, lat: float, lon: float, days: int = 1) -> Optional[List[Dict]]:
        """
        Get hourly weather forecast (limited by NASA POWER data availability)
        Note: NASA POWER has data delay, so this provides historical hourly data
        """
        try:
            end_date = datetime.now() - timedelta(days=7)
            start_date = end_date - timedelta(days=days)
            
            url = f"{self.base_url}/hourly/point"
            
            params = {
                'parameters': 'T2M,RH2M,WS2M,PRECTOTCORR',
                'community': 'ag',
                'longitude': lon,
                'latitude': lat,
                'start': start_date.strftime('%Y%m%d'),
                'end': end_date.strftime('%Y%m%d'),
                'format': 'JSON',
                'time-standard': 'LST'  # Local Solar Time
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            parameters_data = data['properties']['parameter']
            
            # Process hourly data
            hourly_data = []
            temp_data = parameters_data.get('T2M', {})
            
            for datetime_str, temp in temp_data.items():
                try:
                    dt = datetime.strptime(datetime_str, '%Y%m%d%H')
                    hour_data = {
                        'datetime': dt.isoformat(),
                        'hour': dt.strftime('%H:00'),
                        'temperature': round(float(temp), 1),
                        'humidity': round(float(parameters_data.get('RH2M', {}).get(datetime_str, 50)), 1),
                        'wind_speed': round(float(parameters_data.get('WS2M', {}).get(datetime_str, 0)), 1),
                        'precipitation': round(float(parameters_data.get('PRECTOTCORR', {}).get(datetime_str, 0)) / 24, 2),  # Convert daily to hourly
                        'icon': self._get_hour_icon(float(temp))
                    }
                    hourly_data.append(hour_data)
                except (ValueError, TypeError):
                    continue
            
            return sorted(hourly_data, key=lambda x: x['datetime'])[:24]  # Last 24 hours
            
        except Exception as e:
            logging.error(f"NASA POWER hourly data error: {e}")
            return None
    
    def _get_hour_icon(self, temp: float) -> str:
        """Simple icon assignment based on temperature"""
        if temp < 0:
            return '❄️'
        elif temp < 10:
            return '🌤️'
        elif temp < 25:
            return '⛅'
        else:
            return '☀️'
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get information about NASA POWER API capabilities
        """
        return {
            'api_name': 'NASA POWER',
            'full_name': 'NASA Prediction of Worldwide Energy Resources',
            'description': 'Global meteorological data from satellite observations',
            'website': 'https://power.larc.nasa.gov/',
            'data_source': 'Satellite observations and assimilation models',
            'spatial_resolution': '0.5° x 0.625°',
            'temporal_coverage': '1981-present (3 month delay)',
            'update_frequency': 'Daily (with 3-month processing delay)',
            'parameters': list(self.parameters.keys()),
            'communities': self.communities,
            'advantages': [
                'Global coverage',
                'Satellite-derived accuracy',
                'Long historical record',
                'Multiple temporal resolutions',
                'Analysis-ready data',
                'No API key required',
                'NASA quality assurance'
            ]
        }