# API Documentation

## Endpoints

### / (GET)
- **Description:** Returns a list of all devices with their status and last seen timestamp.
- **Parameters:** None
- **Response Format:** JSON array of device objects. Each device object includes `id`, `name`, `ip_address`, `mac_address`, `status`, `last_seen`, and `notify`.
- **Example Usage:** `GET /`

### /admin (GET)
- **Description:** Returns a list of all devices for admin purposes.
- **Parameters:** None
- **Response Format:** JSON array of device objects similar to `/` endpoint.
- **Example Usage:** `GET /admin`

### /admin/add_device (POST)
- **Description:** Adds a new device to the database.
- **Parameters:**
    - `name` (string): The name of the device.
    - `ip_address` (string): The IP address of the device.
    - `mac_address` (string): The MAC address of the device.
- **Response Format:** JSON indicating success or error. Success returns the newly created device’s ID and the created device details. Error returns an error message.
- **Example Usage:**
  ```json
  {
    "name": "New Device",
    "ip_address": "192.168.1.100",
    "mac_address": "00:11:22:33:44:55"
  }
  ```
  `POST /admin/add_device`

### /api/holiday-theme (GET)
- **Description:** Returns the current holiday theme data.
- **Parameters:**
    - `test-holiday` (string, optional):  Test holiday to retrieve.
- **Response Format:** JSON object with the holiday theme data. Includes `active`, `holiday`, `particle_type`, `background_gradient`, and `colors`. If `test-holiday` is provided, it will attempt to retrieve the theme associated with that holiday.
- **Example Usage:**
    `GET /api/holiday-theme?test-holiday=christmas`

## Authentication

- No authentication requirements found. All endpoints are publicly accessible.

## Error Handling

- **400 Bad Request:**  Returned if the request body is invalid (e.g., missing required fields, invalid data types).
- **500 Internal Server Error:** Returned if there is an unexpected error during processing.
