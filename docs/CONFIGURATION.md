# Configuration Guide

## Environment Variables

*   **WEATHER_API_KEY**: (String) - API key for the OpenWeatherMap API. Required. Default: None.
*   **NEWS_API_KEY**: (String) - API key for the NewsAPI.org API. Required. Default: None.
*   **HOME_ASSISTANT_API_ENDPOINT**: (String) - The URL of the Home Assistant API. Required. Default: `
*   **DATABASE_URL**: (String) - The connection string for the SQLite database. Required. Default: `sqlite:///packages.db`
*   **PACKAGE_TRACKING_API_ENDPOINT**: (String) - The URL of the package tracking API. Required. Default: `
*   **ALERT_SENT_TIME_DELAY**: (Integer) - Delay in seconds before sending an alert after a package is delivered.  Optional. Default: 60
*   **DATA_FETCH_INTERVAL**: (Integer) - Interval in seconds for fetching package updates. Optional. Default: 300 (5 minutes)
*   **HOLIDAY_THEME_PARTICLE_TYPE**: (String) - The type of particle effect for the holiday theme. Optional. Default: "star"
*   **HOLIDAY_THEME_BACKGROUND_COLOR**: (String) - The background color for the holiday theme. Optional. Default: "darkblue"
*   **PACKAGE_ARCHIVING_DELAY**: (Integer) - Delay in hours before archiving delivered packages. Optional. Default: 24

## Configuration Files

None. All settings are managed via environment variables.

## Settings

*   **Alerts:** The system sends notifications based on package status changes (e.g., delivered, delayed). The delay before sending alerts is configurable.
*   **Data Fetching:** The periodic data fetch interval determines how often the package tracking API is called to update package statuses.
*   **Holiday Theme:** The system displays a festive holiday theme with particle effects and background gradients. The specific particle type and background color can be customized.
*   **Package Archiving:** Delivered packages are automatically archived after a specified delay (default: 24 hours) to prevent the database from growing indefinitely.
*   **Data refresh frequency:** Allows for different refresh frequencies for various features.
