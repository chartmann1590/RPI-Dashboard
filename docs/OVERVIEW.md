# Project Overview

## Introduction

This project is a smart home monitoring system designed to provide real-time data and control over various smart home devices. It aims to create a centralized platform for monitoring device status, triggering alerts based on predefined rules, and potentially controlling devices remotely.  The system utilizes a Python application (`app.py`) with a SQLite database to store device information, historical data, and alert configurations. The system’s core functionality centers around automatically discovering devices on a local network, continuously monitoring their status, and alerting the user to any anomalies or critical events.

## Key Features

Based on the analysis of the codebase, the key features of this project are:

*   **Device Discovery:** Automatically scans the local network using ARP (Address Resolution Protocol) to discover connected smart home devices.
*   **Device Management:** Enables the user to add, view, and manage device information, including device type, name, and other relevant details.  A basic admin interface is included.
*   **Real-time Monitoring:** Continuously monitors the status of discovered devices.
*   **Alerting:** Triggers alerts based on predefined rules (e.g., temperature exceeding a threshold, device offline).
*   **Historical Data Logging:** Stores historical data for each device, including status changes, temperature readings (if applicable), and other relevant metrics.  This enables trend analysis and debugging.
*   **Speed Test:** Performs periodic network speed tests to monitor network performance.
*   **Holiday Theme Support:** Implements interactive holiday themes (Christmas, Valentine's Day, Thanksgiving, St. Patrick’s Day) with special character animations and visual effects.  This includes a "test-holiday" parameter.
*   **User Interface:** Provides a basic web interface for viewing device status, managing device settings, and viewing historical data.

## Architecture

The project employs a layered architecture:

1.  **Presentation Layer (Flask/Jinja):** The web interface is built using Flask for routing and handling requests, and Jinja2 for rendering HTML templates. This layer interacts with the user.
2.  **Application Layer (app.py):** This is the core logic of the system.  It handles device discovery, data fetching, alert triggering, and database interactions. This is where the majority of the code resides.
3.  **Data Layer (SQLite Database):**  The data is stored in an SQLite database.  The database schema includes tables for:
    *   `devices`: Stores information about each device.
    *   `alerts`: Stores alert rules and configurations.
    *   `history`: Stores historical data for each device.
4.  **Background Processes (Threads):**  Several threads are used to perform background tasks, such as device scanning and periodic speed tests, ensuring that the web interface remains responsive.

The application utilizes threading to execute tasks asynchronously, preventing the main web application thread from being blocked. Device scanning is performed in a separate thread. Data fetching and alert triggering also occur asynchronously.

## Technology Stack

The project utilizes the following technologies and frameworks:

*   **Python:** The primary programming language.
*   **Flask:** A micro web framework for building the web interface and handling HTTP requests.
*   **Jinja2:** A templating engine for rendering HTML templates.
*   **SQLite:** A lightweight, file-based database engine.
*   **ARP (Address Resolution Protocol):** Used for device discovery on the local network.  Implemented through a library call.
*   **Threading:** For asynchronous execution of background tasks.
*   **NumPy:** (Potentially - not explicitly listed but likely used internally for numerical data) - A library for numerical computing, probably used for temperature calculations or data analysis.
*   **Nmap:** (Potentially - library call, but not explicitly listed) – A network scanning tool, likely used by a library call to perform more detailed network discovery.
