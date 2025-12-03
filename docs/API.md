# API Documentation

## Endpoints

### /api/data

*   **HTTP Method:** GET
*   **Path:** /api/data
*   **Description:** Returns current time and a random joke/quote.
*   **Parameters:** None
*   **Response Format:** JSON
*   **Example Usage:** `GET /api/data`

### /api/holiday-theme

*   **HTTP Method:** GET
*   **Path:** /api/holiday-theme
*   **Description:** Returns a holiday theme based on the current time and location.
*   **Parameters:** None
*   **Response Format:** JSON
*   **Example Usage:** `GET /api/holiday-theme`

### /api/holiday-test

*   **HTTP Method:** POST
*   **Path:** /api/holiday-test
*   **Description:**  Allows for testing the holiday theme from the admin interface.
*   **Parameters:** None
*   **Response Format:** JSON
*   **Example Usage:** `POST /api/holiday-test`

## Authentication

No authentication requirements found.

## Error Handling

Common error responses:

*   `400 Bad Request`: Invalid input data.
*   `500 Internal Server Error`: An unexpected error occurred on the server.
