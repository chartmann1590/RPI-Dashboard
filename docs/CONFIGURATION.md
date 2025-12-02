# Configuration Guide

## Environment Variables

*   `SECRET_KEY`:  A strong secret key used for session management and other security-related operations. Required. Default: 'your_secret_key' (CHANGE THIS!).
*   `DATABASE`:  The name of the SQLite database file used by the application. Required. Default: 'devices.db'
*   `HOLIDAYS_DATA_PATH`:  Path to the holidays data file (if used). Optional. Default: None
*   `NY_TZ`: Timezone for New York.  Required. Default: 'America/New_York'

## Configuration Files

*   None.  All configuration is done through environment variables.

## Settings

*   `debug`: Boolean flag to enable or disable debug mode. Default: True.
*   `host`: The host to listen on. Default: '0.0.0.0'
*   `port`: The port to listen on. Default: 5000
*   `scan_interval`:  The interval (in seconds) at which the `scan()` function is executed. Default: 3600 (1 hour)
*   `package_update_interval`: The interval (in seconds) at which the `periodic_package_updates()` function is executed. Default: 30 * 60 (30 minutes)
*   `package_archive_interval`: The interval (in seconds) at which the `periodic_package_archiving()` function is executed. Default: 60 * 60 (1 hour)
