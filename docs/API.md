# API Documentation

## Endpoints

### /api/holiday-theme

- **HTTP Method:** GET
- **Path:** /api/holiday-theme
- **Description:** Retrieves the current holiday theme data (background gradient, particle type).
- **Parameters:** None
- **Response Format:** JSON
  ```json
  {
    "holiday": "Christmas",
    "background_gradient": "linear-gradient(to bottom, red, blue)",
    "particle_type": "snow"
  }
  ```
- **Example Usage:** `GET /api/holiday-theme`

### /api/switchbot-locks

- **HTTP Method:** GET
- **Path:** /api/switchbot-locks
- **Description:** Retrieves the status of SwitchBot locks.
- **Parameters:** None
- **Response Format:** JSON Array
  ```json
  [
    {
      "name": "Living Room Lock",
      "status": "locked"
    },
    {
      "name": "Bedroom Lock",
      "status": "unlocked"
    }
  ]
  ```
- **Example Usage:** `GET /api/switchbot-locks`

## Authentication

This project does not expose an API.

## Error Handling

Common error responses:

- **404 Not Found:** Indicates that the requested resource (e.g., `/api/holiday-theme`) does not exist.
- **500 Internal Server Error:** Indicates a problem on the server-side.
- **Generic Error Response:**  (If the fetch operation fails, it will display a generic error message).
