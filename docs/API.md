# API Documentation

## Endpoints

### /api/calendar-events

*   **HTTP Method:** GET
*   **Path:** /api/calendar-events
*   **Description:** Retrieves all calendar events.
*   **Parameters:** None
*   **Response Format:** JSON array
    *   Example:
        ```json
        [
          {
            "id": 1,
            "title": "Meeting with Team",
            "start_time": "2023-10-27T10:00:00Z",
            "end_time": "2023-10-27T11:00:00Z"
          },
          {
            "id": 2,
            "title": "Project Deadline",
            "start_time": "2023-10-28T09:00:00Z",
            "end_time": "2023-10-28T17:00:00Z"
          }
        ]
        ```
*   **Example Usage:** `GET /api/calendar-events`

### /api/toggle-notify

*   **HTTP Method:** POST
*   **Path:** /api/toggle-notify
*   **Description:** Toggles the notification status for a specific device.
*   **Parameters:**
    *   `device_id` (required): The ID of the device.
    *   `action` (required):  "home", "away", or "none".
*   **Response Format:** JSON
    *   Success:
        ```json
        { "status": "success", "message": "Notification status updated." }
        ```
    *   Error:
        ```json
        { "status": "error", "message": "Invalid action." }
        ```
*   **Example Usage:** `POST /api/toggle-notify?device_id=1&action=home`

### /api/speed-test

*   **HTTP Method:** GET
*   **Path:** /api/speed-test
*   **Description:** Performs a speed test.
*   **Parameters:** None
*   **Response Format:** JSON
    *   Example:
        ```json
        {
            "ping": 25,
            "download_speed": 100,
            "upload_speed": 20
        }
        ```
*   **Example Usage:** `GET /api/speed-test`

### /api/holiday-theme

*   **HTTP Method:** GET
*   **Path:** /api/holiday-theme
*   **Description:**  Loads the current holiday theme.
*   **Parameters:** None
*   **Response Format:** None (Updates the website’s appearance).
*   **Example Usage:** `GET /api/holiday-theme`

## Authentication

*   No authentication is required for any of the documented endpoints.

## Error Handling

*   **400 Bad Request:**  This error is not explicitly documented, but could be returned if the parameters in a request are invalid (e.g., invalid `action` value in `/api/toggle-notify`).
*   **500 Internal Server Error:**  This could occur if there is an error within the server-side code.
