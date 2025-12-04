# Installation Guide

## Prerequisites

*   Python 3.7 or higher is required.
*   Node.js and npm (Node Package Manager) are also required to run the JavaScript components.

## Dependencies

The following Python packages are required:

*   `requests` (for making HTTP requests)
*   `jinja2` (for templating)
*   `flask` (for creating a web application)
*   `socket` (for potential future device communication)
*   `logging` (for logging events)

The following JavaScript dependencies are required:

*   `fetch` (for making HTTP requests)
*   `axios` (for making HTTP requests - alternative to `fetch`)
*   `moment` (for handling dates and times)
*   `jquery` (for DOM manipulation - to handle the HTML rendering)

## Installation Steps

1.  **Clone the Repository:**  Clone the repository from its source (e.g., GitHub).

2.  **Install Python Dependencies:**  Navigate to the project's root directory in your terminal and run the following command to install the Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3.  **Install JavaScript Dependencies:**  Navigate to the `static/js` directory and run the following command to install the JavaScript dependencies:

    ```bash
    npm install
    ```

4.  **Set up the API (if needed):**  If the API endpoints are not already configured, you'll need to set them up.  This includes defining the `/api/holiday-theme` endpoint to return JSON data and the `/api/switchbot-locks` endpoint.  You may need to set up a local server or use an existing API service.

5.  **Configure the Application:**  Set any necessary environment variables, such as API keys or URLs.

6.  **Run the Flask Application:**  Start the Flask application using the provided command (likely `python app.py`).

## Initial Setup

*   Ensure that the Flask application is running.
*   Verify that the JavaScript files are being loaded correctly in the HTML files.
*   Check that the clock is updating correctly.

## Verifying Installation

1.  **Check the Clock:**  The clock should be displaying the current time.
2.  **Verify the Holiday Theme:**  When you visit the main page, the holiday theme (e.g., Christmas) should be applied.
3.  **Confirm Particle Effects:**  The snow, confetti, and other particle effects should be running.
4.  **Check the Lock Status:**  The lock status should be displayed, showing whether the locks are locked or unlocked.
5. **Test responsiveness:** Make sure that the lock status is displayed well on different screen sizes.
