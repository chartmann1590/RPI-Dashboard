# Configuration Guide

## Environment Variables
*   `WEATHER_API_KEY`: Description: API key for the weather service. Required. Default: None
*   `NEWS_API_KEY`: Description: API key for the news service. Required. Default: None
*   `SPORT_API_KEY`: Description: API key for the sports data service. Required. Default: None
*   `iCAL_FEED_URL`: Description: URL of the iCal feed for calendar events. Optional. Default: None
*   `SWITCHBOT_API_KEY`: Description: API key for the SwitchBot integration. Required. Default: None

## Configuration Files
None.

## Settings
*   `dataFetchInterval`: Description: The interval (in minutes) at which the dashboard data is refreshed. Default: 5
*   `lock_status_refresh_interval`: Description: The interval (in minutes) at which the SwitchBot lock status is refreshed. Default: 5
*   `holiday_theme_duration`: Description: Duration (in hours) for displaying the holiday theme. Default: 12
*   `particle_count`: Description: The number of particles to use in the snow/confetti effects. Default: 50
*   `show_lock_status`: Description: A boolean value (true/false) to control whether the SwitchBot lock status is displayed. Default: True
