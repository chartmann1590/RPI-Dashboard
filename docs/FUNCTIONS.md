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

## templates/device_history.html
### toggle_notify(device_id, action)
- Description: Updates the notification settings for a specific device.
- Parameters:
    - `device_id` (int): The ID of the device to update.
    - `action` (str): The desired notification action ('home', 'away', 'none').
- Returns: None
- Example:  `toggle_notify(123, 'home')` –  Updates the notification setting for device ID 123 to "home."

## templates/rpi_dashboard.html
### updateBigClock()
- Description: Updates the large clock display with the current time.
- Parameters: None
- Returns: None
- Example:  This function is called periodically to update the clock.

### startParticleEffect(particleType)
- Description: Creates and adds particle elements to the screen based on the `particleType`.
- Parameters:
    - `particleType` (str): The type of particle effect to create (e.g., 'snow', 'leaf', 'confetti').
- Returns: None
- Example: `startParticleEffect('snow')` – Starts a snow effect.

### createSnowParticle()
- Description: Creates a snow particle element.
- Parameters: None
- Returns: None
- Example:  This function is called to create a snow particle.

### createLeafParticle()
- Description: Creates a leaf particle element.
- Parameters: None
- Returns: None
- Example:  This function is called to create a leaf particle.

### createConfettiParticle()
- Description: Creates a confetti particle element.
- Parameters: None
- Returns: None
- Example: This function is called to create confetti particles.

### createHeartParticle()
- Description: Creates a heart particle element.
- Parameters: None
- Returns: None
- Example: This function is called to create heart particles.

### createStarParticle()
- Description: Creates a star particle element.
- Parameters: None
- Returns: None
- Example: This function is called to create star particles.

### createShamrockParticle()
- Description: Creates a shamrock particle element.
- Parameters: None
- Returns: None
- Example: This function is called to create shamrock particles.

### createEggParticle()
- Description: Creates an egg particle element.
- Parameters: None
- Returns: None
- Example: This function is called to create egg particles.

### createBatParticle()
- Description: Creates a bat particle element.
- Parameters: None
- Returns: None
- Example: This function is called to create bat particles.

## templates/device_history.html
### toggle_notify(device_id, action)
- Description: Updates the notification settings for a specific device.
- Parameters:
    - `device_id` (int): The ID of the device to update.
    - `action` (str): The desired notification action ('home', 'away', 'none').
- Returns: None
- Example:  `toggle_notify(123, 'home')` –  Updates the notification setting for device ID 123 to "home."
