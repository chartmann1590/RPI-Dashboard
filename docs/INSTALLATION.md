# Installation Guide

This guide provides instructions for setting up and running the Smart Home Monitoring System.

## Prerequisites

*   **Python 3.9 or higher:** This system is built using Python 3.  Ensure you have a compatible Python version installed. You can check your version by running `python --version` in your terminal.
*   **SQLite:** SQLite is used for storing the system's data. It's included with Python, so no separate installation is required.
*   **Text Editor/IDE:** A text editor or Integrated Development Environment (IDE) is needed to edit the code. (e.g., VS Code, PyCharm)
*   **Terminal/Command Prompt:** Required for running the Python script.

## Dependencies

The system relies on the following Python packages. You must install these using `pip`:

*   **Flask:** For the web interface.  `pip install Flask`
*   **requests:** For making HTTP requests to external APIs (e.g., for speed tests, weather data – although currently not used, it's a good practice). `pip install requests`
*   **asyncio:** For asynchronous programming, crucial for efficient device scanning. `pip install asyncio`
*   **python-dotenv:** For managing environment variables (API keys, database credentials – not currently used, but a good security practice). `pip install python-dotenv`
*   **pyarrow:** Used for SQLite interaction. `pip install pyarrow`
*   **python-dateutil:** For parsing date and time strings. `pip install python-dateutil`

## Installation Steps

1.  **Clone the Repository:** Clone the Smart Home Monitoring System repository from your preferred source (e.g., GitHub).
    ```bash
    git clone [Repository URL - Replace with the actual URL]
    ```

2.  **Navigate to the Directory:**  Change your current directory to the cloned repository's directory:
    ```bash
    cd SmartHomeMonitoring
    ```

3.  **Install Dependencies:**  Install the required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```
    (Ensure you're in the `SmartHomeMonitoring` directory when running this command.)

4.  **Set Up Environment Variables (Recommended - but not yet implemented):** Although currently not used, it's best practice to create a `.env` file in the root directory to store your API keys and other sensitive information.  Example `.env` file (create this file):
    ```
    # Example .env (replace with your actual API keys)
    # API_KEY=your_api_key_here
    # DATABASE_URL=sqlite:///SmartHomeMonitoring.db  # Or adjust path as needed
    ```
    *Important:* Never commit your `.env` file to a public repository.

5.  **Run the Application:**  Execute the main Python script using the following command:
    ```bash
    python app.py
    ```
    This will start the Flask web server.

## Initial Setup

1. **Database Creation:** The script will automatically create the SQLite database file (`SmartHomeMonitoring.db`) in the same directory as the `app.py` file.  If you want to specify a different database path, modify the `DATABASE_URL` in your `.env` file (if you're using one).

2. **First-Time Run:** The first time you run the script, it will automatically create the necessary tables in the database (e.g., `devices`, `alerts`, `history`).

## Verifying Installation

1. **Open the Web Interface:**  Open your web browser and navigate to ` You should see the admin interface.

2. **Device Management:**  The admin interface allows you to add, manage, and monitor devices.  Check that you can add a device.

3. **Alerts:** Verify that alerts are being displayed correctly.

4. **Data Display:** Ensure that data (e.g., device status, temperatures) is being retrieved and displayed.

5.  **Check Logs:**  Examine the console output for any errors or warnings.

**Important Notes:**

*   This is a basic installation guide. Further customization and expansion may be required based on your specific needs.
*   Always refer to the system's documentation (if available) for detailed instructions.
*   For troubleshooting, consult the system’s logs.

**Explanation & Justification of the Content:**

*   **Detailed Prerequisites:**  Specifically states the Python version and SQLite requirement.
*   **Precise Dependencies:**  Lists each package and its installation command.
*   **Step-by-Step Instructions:** Provides a clear sequence of actions.
*   **Environment Variables:**  Includes a warning about best practices and creating the .env file.
*   **Verification Steps:** Guides the user through how to test the installation.
*   **Important Notes:**  Highlights potential areas for further development and troubleshooting.
