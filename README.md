# VAYU 🌬️
## Very Adaptive Your Unique Weather Comfort System

> *Master your weather comfort like the wind god masters the atmosphere*

**VAYU** is a personalized weather comfort application that transforms generic weather forecasts into deeply personal comfort insights, inspired by the Hindu god of wind and weather elements.

## 🌟 What Makes VAYU Special

Unlike traditional weather apps that show the same information to everyone, VAYU:
- **Learns your personal comfort preferences** through a smart onboarding quiz
- **Calculates personalized comfort scores** (0-100) based on your unique thresholds
- **Provides actionable recommendations** tailored to your comfort needs
- **Uses color-coded visual system** for instant comfort assessment
- **Adapts to your activity levels** and health considerations

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip (Python package installer)

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd VAYU

# Create and activate virtual environment
python -m venv venv --clear

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Visit `http://localhost:5000` in your browser and start your personalized weather journey!

## 🌤️ How It Works

1. **Onboarding Quiz** - Tell VAYU about your weather preferences
2. **Location Input** - Enter your city or let us detect your location
3. **Comfort Analysis** - Our algorithm calculates your personal comfort score
4. **Smart Dashboard** - Get color-coded comfort levels and personalized recommendations

## 🎯 Comfort Scoring System

- 🟢 **Very Comfortable (80-100)** - Perfect conditions for you!
- 🟡 **Comfortable (60-79)** - Minor adjustments recommended
- 🟠 **Moderately Uncomfortable (40-59)** - Preparation advised
- 🔴 **Uncomfortable (20-39)** - Significant precautions needed
- ⚫ **Very Uncomfortable (0-19)** - Avoid prolonged exposure

## 🛠️ Technology Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap
- **Weather API:** Open-Meteo (free, no API key required)
- **Storage:** Session-based (upgradeable to database)

## 📁 Project Structure

```
VAYU/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── PROJECT_OVERVIEW.md    # Detailed project documentation
├── README.md             # This file
├── templates/            # HTML templates
├── static/              # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
└── utils/               # Helper modules
    ├── weather_api.py
    ├── comfort_calculator.py
    └── database.py
```

## 🔮 Features

### Current Features
- ✅ Personalized comfort profiling
- ✅ Real-time weather data integration
- ✅ Advanced comfort scoring algorithm
- ✅ Color-coded dashboard interface
- ✅ Personalized recommendations
- ✅ Mobile-responsive design

### Coming Soon
- 🔄 Machine learning for improved predictions
- 📱 Mobile app (PWA/React Native)
- 🌡️ Health condition considerations
- 📍 Multi-location support
- 📊 Historical comfort analytics

## 🤝 Contributing

This project is made by team - CosmoCatalysts (Mayank Garg, Varuchi Maurya, Aryan Shekhawat, Muskan Bajetha, Shivansh Gaur, Vedant Rana)

## 📜 License

Any kind of reproduction of this code is strictly prohibited.

## 🙏 Acknowledgments

- Inspired by **Vayu (वायु)**, the Hindu god of wind and weather
- Weather data provided by [Open-Meteo](https://open-meteo.com/)
- Built with ❤️ for personalized weather experiences

---

**VAYU** - *Where ancient wisdom meets modern weather intelligence* 🌬️