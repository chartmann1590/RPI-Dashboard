# Usage Guide

## Getting Started

This project provides a smart home monitoring system, allowing you to monitor the status of various devices on your network. It’s designed to be relatively straightforward to set up and use.

**Prerequisites:**

*   **Python 3.7+:** This project is built using Python 3. Ensure you have a compatible version installed.
*   **SQLite:** The project utilizes SQLite for storing device data.  No separate database installation is required.
*   **Basic Command Line Familiarity:** You'll need to be comfortable using the command line to run the application.

**Installation:**

1.  **Clone the Repository:**  Clone the project repository from your preferred source (e.g., GitHub).
2.  **Install Dependencies:** Navigate to the project directory and run: `pip install -r requirements.txt`
3.  **Run the Application:** Execute the main Python script: `python app.py`

## Basic Usage

The core functionality of this project revolves around monitoring your devices. The application automatically discovers devices on your network and displays their status.

**Default Operation:**

When you run `python app.py`, the application will automatically start scanning for devices.  It then displays a list of the discovered devices, their current status (e.g., "Online", "Offline", "Temperature: 25°C"), and the timestamp of the last status update.

**Command-Line Options (Future Enhancements - Not currently implemented):**

While currently there are no command-line options, future enhancements would likely include options to:

*   Set the scan interval.
*   Configure alert thresholds.
*   Filter device displays.

## Features

This project offers several key features:

**1. Automatic Device Discovery:**

*   **Functionality:** The `periodic_scan()` function regularly discovers devices on your local network.
*   **How it Works:**  It uses network scanning techniques (details in the `app.py` file – primarily ARP scanning) to identify devices.
*   **Key Metrics:** The application displays the following metrics for each device:
    *   Device Name
    *   Status (e.g., Online, Offline)
    *   Last Update Timestamp

**2. Real-Time Status Monitoring:**

*   **Functionality:** The application continuously monitors the status of the discovered devices.
*   **Update Frequency:** The status updates are performed periodically (configurable in the future).

**3. Holiday Theme Integration:**

*   **Functionality:**  The system supports dynamic holiday themes.
*   **How it Works:**
    *   The `run_holiday_theme()` function loads a relevant theme based on the current date.
    *   Visual effects are used to enhance the visual experience (snow, confetti, etc.).
    *   The `test_holiday` parameter can be set in the URL to choose the theme.
*   **Examples:**
    *   `
    *   `

**4. Data Persistence (SQLite Database):**

*   **Storage:** The discovered devices, their statuses, and historical data are stored in an SQLite database.
*   **File:** The database file is named `devices.db`.
*   **Schema:** The database schema is designed to efficiently store and retrieve device data.

**5. Alerting (Future):**

*   The project currently doesn't have alerting, but this is a planned feature.  It's designed to trigger alerts when a device goes offline or exceeds a predefined threshold (temperature, etc.).

## Examples

**1. Basic Monitoring:**

Run `python app.py`.  You will see a list of devices that are discovered on your network and their current status.

**2. Running a Holiday Theme:**

Visit ` in your web browser.  You'll see the weather displayed with a Christmas-themed visual effect.  Try other holiday themes as well.

**3. Examining Device Data:**

The application saves the state of each device to the database, `devices.db`. This allows you to examine the history of the device's status.

## Tips

*   **Network Configuration:** Ensure your firewall allows the application to scan your network.
*   **Device Discovery Issues:** If devices aren't being discovered, double-check your network configuration and firewall settings.
*   **Database Inspection:** You can use a SQLite browser to explore and query the `devices.db` database.
*   **Future Enhancements:**  The project is a prototype, and the core features are designed to be extended and improved upon. This is a great starting point for contributing to the development of this system.

---

**Important Note:** This usage guide is based on the information provided in the code analysis. Since the project is a prototype, some features may be incomplete or require further development.  This is primarily a conceptual guide, reflecting the project’s current state.  The development team continues to work on enhancements, so expect updates to this documentation.
