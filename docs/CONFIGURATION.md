# Configuration Guide

## Environment Variables

| Name             | Description                               | Required/Optional | Default Value |
|------------------|-------------------------------------------|--------------------|---------------|
| `DATABASE_URL`   | URL for connecting to the SQLite database.  | Required           | `sqlite:///smart_home.db` |
| `DATABASE_NAME` | Name of the SQLite database file.          | Optional           | `smart_home.db` (defaults to `smart_home.db`) |
| `API_KEY_WEATHER` | API key for the Weather API (if used).      | Optional           | `None` (no API key used) |
| `API_KEY_NEWS`    | API key for the News API (if used).        | Optional           | `None` (no API key used) |
| `DATABASE_HISTORY_TABLE` | Table name for the historical device data| Required           | `device_history` |
| `DATABASE_ALERT_TABLE` | Table name for alerts| Required           | `alerts` |
| `DATABASE_QUOTE_HISTORY_TABLE` | Table name for the quote history | Required        | `quote_history` |
| `DEFAULT_DEVICE_NAME`| Default name for newly added devices | Optional | `Unknown Device` |
| `CLOCK_UPDATE_INTERVAL_SECONDS` | Interval in seconds for updating the clock | Required | `1` |
| `DATA_FETCH_INTERVAL_SECONDS` | Interval in seconds for fetching data from APIs | Required | `300` (5 minutes) |
| `HOLIDAY_THEME_UPDATE_INTERVAL_SECONDS` | Interval in seconds for updating holiday themes | Required | `3600` (1 hour) |
| `SPEED_TEST_INTERVAL_SECONDS` | Interval in seconds for running the network speed test | Required | `60` (1 minute) |

## Configuration Files

Currently, there are no explicit configuration files in the codebase. All settings are managed via environment variables.  This approach is simpler and more portable than using separate configuration files.

## Settings

| Setting Name                | Description                                 | Default Value |
|-----------------------------|---------------------------------------------|---------------|
| `clock_display_format`       | Format string for the clock display (e.g., "HH:MM:SS")| `HH:MM:SS`    |
| `weather_api_enabled`        | Boolean flag to enable/disable the Weather API. | `False`       |
| `news_api_enabled`           | Boolean flag to enable/disable the News API.      | `False`       |
| `holiday_theme`            | Default holiday theme (e.g., "christmas")     | "christmas"   |
| `show_particle_effects`     | Boolean flag to enable/disable particle effects | `True`       |
| `speed_test_type`           | Type of network speed test (e.g., "ping")      | "ping"        |
| `max_speed_test_attempts`  | Maximum number of attempts to run the speed test | `3`           |
