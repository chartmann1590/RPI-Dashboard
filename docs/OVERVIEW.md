# Project Overview

## Introduction
This project is a comprehensive web application designed to track packages and provide related information, including weather data, air quality readings, quotes, and sports data. It combines package tracking functionality with a range of informational displays, offering a unified platform for monitoring various data sources. The project aims to create a dynamic and informative dashboard.

## Key Features
*   **Package Tracking:**  Allows users to track packages using tracking numbers, retrieving status updates from external APIs.
*   **Real-time Weather Data:** Displays current weather conditions from an external source.
*   **Air Quality Monitoring:** Presents air quality readings.
*   **Quote and Joke Display:** Randomly displays quotes and jokes.
*   **Sports Data Integration:**  Provides sports data updates.
*   **Periodic Data Updates:** Automatically updates package statuses, weather data, and other information at specified intervals.
*   **Holiday Theme Display:**  Displays a holiday theme with particle effects and background gradients.
*   **Admin Interface:**  Provides an interface for adding devices and viewing device information.
*   **SQLite Database:** Utilizes SQLite for persistent storage of package and device data.
*   **Background Threads:** Employs background threads to handle periodic tasks such as data updates and API calls.

## Architecture
The project adopts a multi-layered architecture:

1.  **Web Interface (Flask):** A Flask web application serves as the front-end, handling user interactions and rendering HTML pages. It interacts with the background threads to fetch and display data.
2.  **Background Threads:**  Multiple background threads perform asynchronous tasks:
    *   `periodic_scan()`: Fetches package updates from an external package tracking API.
    *   `periodic_speed_test()`: Executes a speed test periodically.
    *   `periodic_package_updates()`: Updates package statuses based on speed test results.
    *   `periodic_package_archiving()`: Automatically archives delivered packages after 24 hours.
3.  **Data Layer (SQLite):**  An SQLite database stores package information, device data, and other persistent data.
4.  **External APIs:** The application relies on external APIs for package tracking, weather data, air quality data, sports data, and potentially other data sources.

The web interface interacts with the background threads to fetch and display data. The background threads manage the asynchronous data updates and API calls.

## Technology Stack
*   **Python 3.x:** Programming Language
*   **Flask:** Web Framework
*   **Flask-SQLAlchemy:** ORM (Object-Relational Mapper) for interacting with the SQLite database
*   **SQLite:** Database
*   **threading:** For creating and managing background threads
*   **logging:** For logging events and errors
*   **requests:** For making HTTP requests to external APIs
*   **potentially:** Weather API (e.g., OpenWeatherMap), Air Quality API (e.g., AirVisual), Sports Data API (e.g., ESPN)
