# Function Reference

## requirements.txt
### purpose()
- Description: Lists the Python packages and their versions required for the project.
- Parameters: None
- Returns: None

## templates/index.html
### confirmDelete(deviceId, deviceName)
- Description: Handles the deletion of a device.
- Parameters:
    - deviceId (str): The ID of the device to delete.
    - deviceName (str): The name of the device to delete.
- Returns: None
### toggle_notify(id, action='home')
- Description: Toggles notification preferences for a device.
- Parameters:
    - id (str): The ID of the device to update.
    - action (str, optional): The action to perform (e.g., 'home', 'away', 'none'). Defaults to 'home'.
- Returns: None
### device_history(name)
- Description: Retrieves and displays the device's history.
- Parameters:
    - name (str): The name of the device.
- Returns: None
### reverse()
- Description: Reverses the order of the `history` list.
- Parameters: None
- Returns: None
### render()
- Description: Renders the HTML with data from the Flask application.
- Parameters: None
- Returns: None

## templates/device_history.html
### confirmDelete(deviceId, deviceName)
- Description: Handles the deletion of a device.
- Parameters:
    - deviceId (str): The ID of the device to delete.
    - deviceName (str): The name of the device to delete.
- Returns: None
### toggle_notify(id, action='home')
- Description: Toggles notification preferences for a device.
- Parameters:
    - id (str): The ID of the device to update.
    - action (str, optional): The action to perform (e.g., 'home', 'away', 'none'). Defaults to 'home'.
- Returns: None
### device_history(name)
- Description: Retrieves and displays the device's history.
- Parameters:
    - name (str): The name of the device.
- Returns: None
### reverse()
- Description: Reverses the order of the `history` list.
- Parameters: None
- Returns: None
### render()
- Description: Renders the HTML with data from the Flask application.
- Parameters: None
- Returns: None

## templates/rpi_dashboard.html
### dataFetchInterval
- Description: (Not a function, but represents a scheduled data fetch)
- Parameters: None
- Returns: None
### periodic_scan()
- Description: Periodically fetches package updates from an external API.
- Parameters: None
- Returns: None
### periodic_speed_test()
- Description: Executes a speed test periodically.
- Parameters: None
- Returns: None
### periodic_package_updates()
- Description: Updates package statuses based on speed test results.
- Parameters: None
- Returns: None
### periodic_package_archiving()
- Description: Automatically archives delivered packages after 24 hours.
- Parameters: None
- Returns: None

## app.py
### create_db()
- Description: Creates the SQLite database and necessary tables.
- Parameters: None
- Returns: None
### add_alert_shown_column()
- Description: Adds the `alert_shown` column to the `devices` table.
- Parameters: None
- Returns: None
### ensure_joke_history_table()
- Description: Initializes the `quote_history` table.
- Parameters: None
- Returns: None
### ensure_quote_history_table()
- Description: Initializes the `quote_history` table.
- Parameters: None
- Returns: None
### dataFetchInterval
- Description: (Not a function, but represents a scheduled data fetch)
- Parameters: None
- Returns: None
### periodic_scan()
- Description: Periodically fetches package updates from an external API.
- Parameters: None
- Returns: None
### periodic_speed_test()
- Description: Executes a speed test periodically.
- Parameters: None
- Returns: None
### periodic_package_updates()
- Description: Updates package statuses based on speed test results.
- Parameters: None
- Returns: None
### periodic_package_archiving()
- Description: Automatically archives delivered packages after 24 hours.
- Parameters: None
- Returns: None
