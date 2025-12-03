# Usage Guide

## Getting Started

This project provides a system for monitoring packages and displaying their status. To get started, you'll need to have Python 3 installed on your system. You will also need to install the required Flask package.

1.  **Clone the Repository:** Clone the repository from its source.
2.  **Install Dependencies:** Navigate to the project directory in your terminal and run `pip install -r requirements.txt`.
3.  **Run the Application:**  Open a terminal, navigate to the project directory, and run `python app.py`. The application will start, and you should see a message indicating that it's running.
4.  **Access the Application:** Open your web browser and go to `  You should see the main dashboard.

## Basic Usage

The main dashboard displays a list of devices, showing their names, status, and last seen timestamp.

*   **Adding Devices:** To add a new device, click the "Add Device" button. You will be prompted to enter the device's name, IP address, and MAC address.  The system will automatically create a new device entry.
*   **Viewing Package Status:** Clicking on a device's name will display its package status, including the tracking number, carrier, description, status, last location, estimated delivery date, and delivery date.
*   **Real-Time Updates:** The dashboard updates in real-time, reflecting any changes in the package status.

## Features

*   **Device Monitoring:**  The system monitors and displays the status of devices.
*   **Package Tracking:**  The system tracks packages, providing information such as tracking number, carrier, and status.
*   **Real-Time Updates:**  The dashboard updates automatically, providing real-time package status information.
*   **Archiving:** The system automatically archives packages after a period of inactivity.
*   **API Integration:** The application includes an API endpoint (`/api/holiday-theme`) that can be used to retrieve the current holiday theme data.
*   **Periodic Scanning:** The system periodically scans for new packages and updates their status.
*   **Joke and Quote History:** The system maintains a history of jokes and quotes.
*   **Speed Testing:** The system performs periodic speed tests for packages.

## Examples

### Adding a New Device

1.  Open your web browser and go to `
2.  Click the "Add Device" button.
3.  Enter the device's name (e.g., "Living Room Monitor").
4.  Enter the device's IP address (e.g., "192.168.1.100").
5.  Enter the device's MAC address (e.g., "00:11:22:33:44:55").
6.  Click the "Save" button.
7.  The new device will appear in the device list on the dashboard.

### Viewing Package Status

1.  On the dashboard, click on the name of a device (e.g., "Living Room Monitor").
2.  The package status for that device will be displayed, showing the tracking number, carrier, description, status, last location, estimated delivery date, and delivery date.

### Retrieving the Holiday Theme

To retrieve the current holiday theme data, you can use the following API endpoint:

`

This will return a JSON object containing the holiday theme data.

## Tips

*   The dashboard updates automatically in real-time, so you don't need to manually refresh it.
*   If you encounter any issues, check the logs for error messages.
*   The system is designed to handle a large number of devices and packages.
*   For more advanced features, refer to the source code.
