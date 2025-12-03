# Function Reference

## app.py

### add_device(name, ip_address, mac_address)
- Description: Adds a new device to the database.
- Parameters:
    - name (str): The name of the device.
    - ip_address (str): The IP address of the device.
    - mac_address (str): The MAC address of the device.
- Returns: Redirects to the admin page.
- Example:
  ```python
  add_device("MyDevice", "192.168.1.100", "00:11:22:33:44:55")
  ```

### admin(devices)
- Description: Displays a list of all devices in the database.
- Parameters:
    - devices (list): A list of device objects.
- Returns: Renders the admin.html template with the device list.
- Example:
  ```python
  admin()
  ```

### api_holiday_theme()
- Description: Retrieves the current holiday theme data.
- Parameters:
    - test_holiday (str, optional): The name of the test holiday. Defaults to None.
- Returns: Returns a JSON object containing the holiday theme data.
- Example:
  ```python
  api_holiday_theme()
  ```

### get_holiday_theme(test_holiday=None)
- Description: Retrieves the holiday theme from the database.
- Parameters:
    - test_holiday (str, optional): The name of the test holiday. Defaults to None.
- Returns: Returns a dictionary containing the holiday theme data.
- Example:
  ```python
  get_holiday_theme()
  ```

### get_package_status(tracking_number, carrier)
- Description: Retrieves the package status from the database.
- Parameters:
    - tracking_number (str): The tracking number of the package.
    - carrier (str): The carrier of the package.
- Returns: Returns a dictionary containing the package status.
- Example:
  ```python
  get_package_status("1234567890", "UPS")
  ```

### periodic_archive_package()
- Description: Moves delivered packages into the archive.
- Parameters:
    - None
- Returns: None
- Example:
  ```python
  periodic_package_archiving()
  ```

### periodic_scan()
- Description: Scans for new packages every hour.
- Parameters:
    - None
- Returns: None
- Example:
  ```python
  scan_thread = threading.Thread(target=periodic_scan)
  scan_thread.daemon = True
  scan_thread.start()
  ```

### periodic_package_archiving()
- Description: Moves delivered packages into the archive.
- Parameters:
    - None
- Returns: None
- Example:
  ```python
  package_archive_thread = threading.Thread(target=periodic_package_archiving)
  package_archive_thread.daemon = True
  package_archive_thread.start()
  ```

### periodic_speed_test()
- Description: Runs speed test for a package every hour.
- Parameters:
    - None
- Returns: None
- Example:
  ```python
  speed_test_thread = threading.Thread(target=periodic_speed_test)
  speed_test_thread.daemon = True
  speed_test_thread.start()
  ```

### periodic_package_updates()
- Description: Updates package statuses every 30 minutes.
- Parameters:
    - None
- Returns: None
- Example:
  ```python
  package_update_thread = threading.Thread(target=periodic_package_updates)
  package_update_thread.daemon = True
  package_update_thread.start()
  ```

## functions.md
- Description: This markdown file is intended to document the functions found in all the various python files.
- Parameters:
    - None
- Returns: None
- Example:
  ```python
  # Example to document another function here.
  ```
