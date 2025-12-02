# API Documentation

## Endpoints

### / (GET)
- **Description:** Returns a list of all devices currently monitored.
- **Parameters:** None
- **Response format:** JSON
- **Example usage:** `GET /`

### /admin (GET)
- **Description:** Returns a list of all devices, accessible only to administrators.
- **Parameters:** None
- **Response format:** JSON
- **Example usage:** `GET /admin`

### /admin/add_device (GET, POST)
- **Description:** Allows adding a new device to the monitoring system.
- **Parameters:**
    - `name` (POST): The name of the device.
    - `ip_address` (POST): The IP address of the device.
    - `mac_address` (POST): The MAC address of the device.
    - `notify` (POST): The notification type for this device.
- **Response format:** JSON (on success), error message (on failure)
- **Example usage:**
    - `GET /admin/add_device` (to display the form)
    - `POST /admin/add_device` (to submit the form)

###  /api/data (GET)
- **Description:** Returns a list of all devices.
- **Parameters:** None
- **Response format:** JSON
- **Example usage:** `GET /api/data`

## Authentication

None. All endpoints are publicly accessible.

## Error Handling

- **400 Bad Request:**  Returned if the request is malformed (e.g., missing required parameters).  The response body will contain an error message explaining the issue.
- **500 Internal Server Error:** Returned if an unexpected error occurs on the server.  The response body will contain a generic error message.
