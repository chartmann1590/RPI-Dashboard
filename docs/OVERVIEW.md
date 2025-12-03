# Project Overview

## Introduction
This project is a web application designed to track and manage package deliveries. It provides a dashboard for viewing package statuses, running speed tests, and archiving completed deliveries. The primary goal is to offer a centralized location for monitoring package shipments and potentially identify areas for improvement in delivery times.

## Key Features
*   **Package Tracking:** Displays a list of tracked packages with their current status (e.g., 'pending', 'in transit', 'delivered'), last seen timestamp, IP address, and MAC address.
*   **Speed Testing:** Allows users to initiate speed tests for individual packages, simulating network conditions.
*   **Package Archiving:** Automatically archives completed deliveries after a defined period (24 hours), preventing the database from becoming cluttered with obsolete data.
*   **Holiday Theme Support:** Displays the application with a holiday-themed background, configurable through a query parameter in the API.
*   **Quote History:** Allows the user to view quote history.
*   **API Integration:** Provides an API endpoint to retrieve the current holiday theme.

## Architecture
The project utilizes a three-tier architecture:

1.  **Presentation Tier (Flask Web App):** This layer is implemented using Flask, a Python web framework. It handles user interface rendering, user input processing, and API requests. The main components are:
    *   `app.py`: The core Flask application, responsible for routing requests, handling database interactions, and rendering templates.
    *   Templates (e.g., `index.html`, `add_device.html`): Define the user interface elements.
2.  **Application Tier (Python Logic):** This layer consists of Python code within `app.py`, which handles business logic, such as:
    *   Database interaction using `sqlite3` for package tracking.
    *   Scheduling periodic tasks using threading.
    *   API request handling and response generation.
3.  **Data Tier (SQLite Database):**  The data is stored in an SQLite database (`packages.db`) which is a lightweight, file-based database ideal for this project. The database schema includes tables for:
    *   `devices`: Stores information about tracked devices (name, IP address, MAC address, status, last_seen, notify).
    *   `packages`:  Stores package tracking information (tracking_number, carrier, description, status, last_location, estimated_delivery, delivered_date, created_at).
    *   `packages_archive`: Stores archived packages.
    *   `joke_history`: Stores quote history.

The application utilizes threading to perform background tasks, such as running speed tests and periodically scanning for new package updates and archiving completed deliveries, without blocking the main web application thread.

## Technology Stack
*   **Python:** The primary programming language.
*   **Flask:**  A micro web framework for building the web application.
*   **SQLite:**  A lightweight, file-based relational database.
*   **pytz:**  Python library for handling time zones.
*   **Threading:**  For concurrent task execution.
*   **HTML, CSS, JavaScript:**  For the user interface.
