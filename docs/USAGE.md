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
    *   Examples:
        *   `

**4. Data Persistence (SQLite Database):**

*   **Storage:** The discovered devices, their statuses, and historical data are stored in an SQLite database.
*   **File:** The database file is named `devices.db`.
*   **Schema:** The database schema is designed to efficiently store and retrieve device data.

**5. Alerting (Future):**

*   The project currently doesn't have alerting, but this is a planned feature.  It’s designed to trigger alerts when a device goes offline or exceeds a predefined threshold (e.g., temperature).

## Examples

**Example 1: Viewing Device Status**

When you run `python app.py`, the application will display a list of devices it has discovered, including their names, current status, and the timestamp of the last update.

**Example 2:  Holiday Theme**

The application can toggle between holiday themes.  To set a holiday, use the `test_holiday` parameter in the URL. For example, to view the application with the Christmas theme, use `

## Tips

*   Ensure that your firewall allows connections to the application on the specified port (default: 5000).
*   Monitor the application logs for any errors or warnings.
*   Consider adding more devices to the network to test the automatic discovery functionality.
*   To disable the holiday theme, simply remove the `?test_holiday=christmas` parameter from the URL.
