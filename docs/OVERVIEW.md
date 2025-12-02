# Project Overview

## Introduction
This project is a web application designed to simulate a device monitoring and tracking system. It provides a dashboard for visualizing device status, including IP addresses, MAC addresses, and last seen timestamps.  It also includes a package tracking system with automated archiving of delivered packages after 24 hours.  The system provides a basic admin interface for adding new devices.

## Key Features
*   **Device Monitoring Dashboard:** Displays a list of connected devices, showing their status, IP addresses, MAC addresses, last seen timestamps, and notify settings.
*   **Package Tracking System:** Allows tracking of packages, including carrier, description, status, last location, and estimated/delivered dates.  Automatically archives delivered packages after 24 hours.
*   **Admin Interface:** Provides an interface to add new devices to the system.
*   **Simulated Scanning:** The application periodically scans for devices and updates their status.
*   **Periodic Speed Tests:**  Simulates speed tests for devices.
*   **Joke Retrieval:** Randomly retrieves and displays a joke.

## Architecture
The project follows a three-tier architecture:

1.  **Presentation Tier (Frontend):**  A Flask-based web application with HTML, CSS, and JavaScript for the user interface. It handles user interaction and renders the dashboard and forms.
2.  **Application Tier (Backend):** A Flask application that handles the business logic, data validation, and communication with the database.
3.  **Data Tier (Database):** An SQLite database (devices.db) to store device information and package tracking data.

The application uses Flask for routing, handling requests, and rendering templates.  The application uses a thread to continuously scan for devices and perform speed tests.  A separate thread is responsible for archiving packages.

## Technology Stack
*   **Python 3.x:** The primary programming language.
*   **Flask:** A micro web framework for building the backend application.
*   **SQLite:** A lightweight, file-based database to store data.
*   **HTML, CSS, JavaScript:** For the frontend user interface.
*   **pytz:** A library for handling timezones.
*   **random:** Python standard library for generating random values.
