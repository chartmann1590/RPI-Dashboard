# Function Reference

## app.py
### run_app()
- Description: Initializes and runs the main smart home monitoring application. This function sets up the database connection, starts the device scanning thread, and runs the Flask web server.
- Parameters: None
- Returns: None
- Example:  `run_app()` – Simply call this to start the entire application.

### add_device(device_name, device_type, ip_address=None)
- Description: Adds a new device to the monitoring system.  Stores device information in the database.
- Parameters:
    - `device_name` (str):  The name of the device.
    - `device_type` (str):  The type of device (e.g., 'temperature sensor', 'smart bulb').
    - `ip_address` (str, optional): The IP address of the device.  If not provided, the system will attempt to discover it.  Defaults to None.
- Returns: None
- Example: `add_device("Living Room Thermostat", "temperature sensor")`

### remove_device(device_name)
- Description: Removes a device from the monitoring system.  Deletes the corresponding record from the database.
- Parameters:
    - `device_name` (str): The name of the device to remove.
- Returns: None
- Example: `remove_device("Living Room Thermostat")`

### main()
- Description: The main entry point of the application. Initializes the database connection, sets up the device scanning thread, and starts the Flask web server.
- Parameters: None
- Returns: None
- Example: `main()` – To start the app, just call this function.

### scan_thread()
- Description: Periodically scans for devices and updates their last seen status.
- Parameters: None
- Returns: None
- Example: `scan_thread()` – To scan for devices, simply call this function.

### scan_devices()
- Description: Scans for devices and updates their last seen status.
- Parameters: None
- Returns: None
- Example: `scan_devices()` – To scan for devices, simply call this function.

### run_speed_test()
- Description: Simulates running a speed test.
- Parameters: None
- Returns: None
- Example: `run_speed_test()` – To run a speed test, simply call this function.

### get_device_data()
- Description: Gets data from the database.
- Parameters: None
- Returns: list of dictionaries, each dictionary contains device information
- Example: `get_device_data()` – To get data about devices, simply call this function.

### add_new_device(device_name, ip_address, mac_address)
- Description: Adds a new device to the monitoring system.
- Parameters:
    - `device_name` (str): The name of the device.
    - `ip_address` (str): The IP address of the device.
    - `mac_address` (str): The MAC address of the device.
- Returns: None
- Example: `add_new_device("New Device", "192.168.1.100", "AA:BB:CC:DD:EE:FF")`

### update_device_status(device_id, new_status)
- Description: Updates the status of a device.
- Parameters:
    - `device_id` (int): The ID of the device to update.
    - `new_status` (str): The new status of the device.
- Returns: None
- Example: `update_device_status(1, "Online")`

### remove_device(device_name)
- Description: Removes a device from the monitoring system.
- Parameters:
    - `device_name` (str): The name of the device to remove.
- Returns: None
- Example: `remove_device("Living Room Thermostat")`

## templates/rpi_dashboard.html
### updateBigClock(clockData)
- Description: Updates a large clock element on the page with data from clockData.
- Parameters:
    - `clockData` (dict): Dictionary containing time information
- Returns: None
- Example: `updateBigClock({hour: 14, minute: 30, second: 0})`

### updateWeatherData(weatherData)
- Description: Updates the weather information on the page with data from weatherData.
- Parameters:
    - `weatherData` (dict): Dictionary containing weather information
- Returns: None
- Example: `updateWeatherData({temperature: 25, condition: "Sunny"})`

### updateEvents(eventsData)
- Description: Updates the event information on the page with data from eventsData.
- Parameters:
    - `eventsData` (dict): Dictionary containing event information
- Returns: None
- Example: `updateEvents({event_name: "Meeting", time: "10:00 AM"})`

### clearParticles()
- Description: Clears all particle effects from the page.
- Parameters: None
- Returns: None
- Example: `clearParticles()`

### clearSpecialCharacters()
- Description: Clears all special character animations from the page.
- Parameters: None
- Returns: None
- Example: `clearSpecialCharacters()`

### startParticleEffect(effectName, options)
- Description: Starts a particle effect on the page with the given name and options.
- Parameters:
    - `effectName` (str): The name of the particle effect to start.
    - `options` (dict): Dictionary containing options for the particle effect.
- Returns: None
- Example: `startParticleEffect("snow", {"speed": 0.5})`

### startSpecialCharacterAnimation(animationName, options)
- Description: Starts a special character animation on the page with the given name and options.
- Parameters:
    - `animationName` (str): The name of the special character animation to start.
    - `options` (dict): Dictionary containing options for the animation.
- Returns: None
- Example: `startSpecialCharacterAnimation("leaf", {"direction": "left"})`
