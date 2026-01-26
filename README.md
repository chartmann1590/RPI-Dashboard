# RPI-Dashboard

## Description
A web-based dashboard that displays a variety of information, including news, weather, traffic, a photo album, calendar, shopping list, home automation status, and more. It's designed to be a central hub of information and control for a smart home environment.

## Features
*   Real-time weather updates and radar
*   Traffic information with route maps
*   News feed from multiple sources
*   Shopping list management
*   Calendar integration (Google Calendar)
*   Photo album display with rotating gallery
*   Home automation status (Home Assistant integration)
*   Smart lock control (SwitchBot locks)
*   Package tracking
*   Sports scores
*   Air quality monitoring
*   Astronomy data (sunrise/sunset, moon phase)
*   Daily quotes and jokes
*   Gaming integration (ROMM library stats, RetroAchievements)
*   Internet speed monitoring

## Dashboard Views

### RPI Dashboard (`/rpi-dashboard`)
Optimized for small screens (Raspberry Pi displays). Features rotating carousel of information screens.

### TV Dashboard (`/tv-dashboard`)
Optimized for large TV displays with two viewing modes:
- **Grid Mode**: 2x2 widget layout with multiple screens
- **Carousel Mode**: Full-screen rotating displays
- Auto-refresh every 60 seconds with last update timestamp
- Fullscreen support (F key or button)

## Quick Start
1.  Ensure you have Python 3.9+ and Flask installed
2.  Clone the repository: `git clone [repository_url]`
3.  Navigate to the project directory: `cd RPI-Dashboard`
4.  Install dependencies: `pip install -r requirements.txt`
5.  Copy `.env.example` to `.env` and configure your API keys
6.  Run the application: `python app.py`

## Configuration
See `.env.example` for all available configuration options including:
- Weather API (OpenWeatherMap)
- Google Calendar API
- Home Assistant URL and token
- SwitchBot API credentials
- ROMM server URL
- RetroAchievements API key
- News API keys

## Documentation
- [Overview](docs/OVERVIEW.md)
- [Installation](docs/INSTALLATION.md)
- [Configuration](docs/CONFIGURATION.md)
- [API Reference](docs/API.md)
- [Usage Guide](docs/USAGE.md)
- [Function Reference](docs/FUNCTIONS.md)

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute to this project.

## Security
See [SECURITY.md](SECURITY.md) for security policy and reporting vulnerabilities.

## License
This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Support
For issues or questions, please open an issue in the project repository.
