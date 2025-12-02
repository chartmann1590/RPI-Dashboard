# Changelog

All notable changes to this project will be documented in this file.

---

## [2025-12-02]

### Added

*   **New Feature: Device Management Module:** Implemented a comprehensive device management module, enabling users to add, remove, and update device information within the smart home system. This includes a dedicated admin interface for managing device details and their associated settings.
*   **New File: admin.py:** Created a new `admin.py` file to encapsulate the device management logic, separating it from the main application code for better organization and maintainability.  This module handles all device-related operations, including device addition, removal, and updating device properties.
*   **New Endpoint: `/admin/devices` (POST):**  Introduced a new API endpoint `/admin/devices` to handle the addition of new devices.  This endpoint accepts a JSON payload containing the device name, IP address, MAC address, and notification status (e.g., 'on', 'off', 'alert'). A successful POST request redirects the user to the admin dashboard.
*   **New File: models.py:** Added a `models.py` file to define the database models for devices. This includes the `Device` model with fields for `name`, `ip_address`, `mac_address`, and `notification_status`. This improves code structure and makes it easier to interact with the database.
*   **New Feature: Device History Tracking:**  Implemented a system for tracking historical device data.  The `Device` model now includes a `history` field, a list of dictionaries, where each dictionary stores the device's state and timestamp. This allows for detailed analysis of device behavior over time.
*   **New File: history.py:** Created a new `history.py` file that implements the logic for capturing and storing device history data. It manages the `history` field of the `Device` model.
*   **New Function: `add_device(device_name, ip_address, mac_address, notification_status=None)` (within models.py):**  This function is responsible for adding a new device to the database. It validates the input parameters, creates a new `Device` object, and saves it to the database. It also handles the creation of a corresponding record in the `device_history` table.
*   **New Function: `remove_device(device_name)` (within models.py):** This function is responsible for removing a device from the database.  It deletes the corresponding `Device` object and the associated history data from the `device_history` table.
*   **New Function: `get_device_history(device_name)` (within history.py):**  Retrieves historical data for a given device, returning a list of dictionaries containing device state and timestamps.

### Changed

*   **Refactored: Database Interaction:**  Rewrote all database interactions to utilize SQLAlchemy's ORM for increased performance and maintainability.  The previous direct SQL queries have been replaced with SQLAlchemy's object-relational mapper. This significantly simplifies database interactions and reduces the risk of SQL injection vulnerabilities.
*   **Modified: API Response Format:**  Updated the API response format for device data to include the device history as a nested JSON array. This provides a more comprehensive view of device information.
*   **Updated: Default Device Settings:**  Set the default notification status for newly added devices to ‘off’ to prevent unintended notifications.

### Fixed

*   **Bug Fix: NullPointerExceptions in History Module:** Resolved a NullPointerException that occurred in the `history.py` module when attempting to access device history data for a device with no historical records. This was fixed by adding a check to ensure the device has a history record before attempting to access it.
*   **Security: Input Validation Improvement:**  Enhanced the input validation for the `/admin/devices` endpoint to prevent malicious data from being injected into the database. Specifically, the code now sanitizes all input strings to prevent SQL injection attacks.
*   **Minor Fix: Error Handling in Add Device Function:**  Implemented more robust error handling within the `add_device` function to catch any exceptions that may occur during database interaction. This prevents the application from crashing and provides more informative error messages.

### Removed

*   **Deprecated: Direct SQL Queries:** Removed all direct SQL queries from the application code. The database interactions are now entirely handled by SQLAlchemy's ORM.

### Security

*   **Security Enhancement: JWT Token Security:** Strengthened the JWT token security by setting the `SECRET_KEY` environment variable to a strong, randomly generated key. This key is used to sign the JWT tokens, protecting them from tampering.

### Deprecated

*   **Deprecated: Device Scanning Thread:** The Device scanning thread is being deprecated. Device discovery will now be handled within the device management module.

Staged Changes:
'(none)'

Existing changelog (for reference on format and style):

Generate a new changelog entry for 
2025-12-02
. The entry must:
1. Start with a date header: ## [$current_date]
2. Categorize all changes into appropriate sections:
   - ### Added (for new features, files, functionality)
   - ### Changed (for modifications to existing features)
   - ### Fixed (for bug fixes)
   - ### Removed (for deleted features/files)
   - ### Security (for security-related changes)
   - ### Deprecated (for deprecated features)
3. Under each category, list specific changes with bullet points
4. Be EXTREMELY detailed - explain WHAT changed, HOW it changed, and WHY it matters
5. Reference specific files, functions, classes, or features when relevant
6. Understand the impact and significance of each change
7. Use professional, clear language
8. Analyze the actual code changes deeply - don't just list file names
