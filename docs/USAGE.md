# Usage Guide

## Getting Started

This project provides a multi-faceted application for tracking packages and displaying quotes/jokes. It combines a package tracking system with a random quote/joke display.

**Prerequisites:**

*   Python 3.7+
*   SQLite (the project uses SQLite as its database)

**Installation:**

1.  Clone the repository: `git clone [repository URL]`
2.  Navigate to the project directory: `cd [project directory]`
3.  Install the required Python packages: `pip install -r requirements.txt`

## Basic Usage

**Starting the Application:**

Run the main Python file: `python app.py`

**Accessing the Application:**

The application runs on ` by default.

**Key Features and How to Use Them:**

*   **Package Tracking:**
    *   The application periodically fetches package tracking data (placeholder functionality).  To use this feature, you need to replace the placeholder code with real API calls to a package tracking service (e.g., FedEx, UPS, USPS).
    *   View details about tracked packages on the dashboard.
*   **Quote/Joke Display:**
    *   The application displays a random quote or joke.
    *   The quotes and jokes are stored in the `quote_history` and `joke_history` tables to avoid repetition.
*   **Admin Interface:**
    *   Access the admin interface at `/admin`.
    *   Add new devices to track.
    *   View device information.
*   **Holiday Theme:**
    *   The `/api/holiday-theme` endpoint displays a holiday theme based on the current time and location.  The theme is generated using a random particle effect and special characters.
*   **Holiday Test:**
     *   The `/api/holiday-test` endpoint allows you to test the holiday theme.

## Features

### Package Tracking

*   **Tracking Data Updates:** The application periodically retrieves package tracking data.  *This functionality requires you to replace the placeholder code with API calls to a tracking service.*
*   **Package Details:** Displays information about tracked packages, including status, tracking number, carrier, last known location, and estimated delivery date.
*   **Archiving:** Automatically archives delivered packages after 24 hours.

### Quote/Joke Display

*   **Random Selection:**  Selects a random quote or joke from the `quote_history` and `joke_history` tables.
*   **No Repetition:** The same quote/joke will not be displayed twice.

### Admin Interface

*   **Device Management:**  Add new devices to track.
*   **Device Information:**  View details about existing devices.

### Holiday Theme

*   **Dynamic Theme:** The application displays a dynamically generated holiday theme based on the current time and location.
*   **Particle Effects:** Uses random particle effects to create a visually engaging theme.
*   **Special Characters:** Employs special characters to enhance the visual appearance of the theme.
*   **Gradient Backgrounds:** Uses gradient backgrounds to create a visually appealing background.

### API Endpoints

*   `/api/holiday-theme`: Returns a holiday theme based on the current time and location.
*   `/api/holiday-test`: Allows testing of the holiday theme.

## Examples

### Adding a Device (Admin Interface)

1.  Navigate to the `/admin` page in your browser.
2.  Enter the device name in the appropriate field.
3.  Click the "Add Device" button.

### Displaying a Quote

Simply navigate to the main dashboard, and the application will randomly display a quote from its history.

### Testing the Holiday Theme

Use the `/api/holiday-test` endpoint to see the dynamically generated holiday theme.

## Tips

*   **Replace Placeholder API Calls:** To enable full package tracking functionality, you *must* replace the placeholder API calls with calls to a real package tracking service.
*   **Error Handling:** Be mindful of potential API errors. Implement robust error handling to gracefully handle any issues.
*   **Database Management:**  Inspect the database tables (`devices`, `packages`, etc.) to understand the data structure and relationships.
*   **Configuration:** Customize the application's behavior by modifying the configuration settings (e.g., API endpoints, refresh intervals).
