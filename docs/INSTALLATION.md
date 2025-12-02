# Installation Guide

## Prerequisites

*   **Python 3.9 or higher:** This application is written in Python and requires a compatible Python version.
*   **pip:**  The Python package installer is required to install the dependencies.

## Dependencies

The following Python packages are required for this application:

*   `Flask`:  A micro web framework for Python.
*   `sqlite3`:  Python's built-in SQLite database module.
*   `pytz`:  Python library for handling time zones.
*   `random`:  Python's built-in random number generator.
*   `threading`: Python's threading module.

## Installation Steps

1.  **Clone the Repository:** Clone the repository from the source (insert repository URL here).  For example: `git clone [repository URL]`

2.  **Create a Virtual Environment (Recommended):** Create a virtual environment to isolate the project's dependencies:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate  # On Windows
    ```

3.  **Install Dependencies:**  Install the required packages using pip:

    ```bash
    pip install Flask pytz random
    ```

4.  **Run the Application:**  Navigate to the project directory in your terminal and run the Flask application:

    ```bash
    python app.py
    ```

    This should start the Flask server, typically on `

## Initial Setup

*   The application will automatically create the `devices.db` SQLite database file in the project directory.
*   The application also initializes a virtual environment.

## Verifying Installation

1.  **Open a Web Browser:**  Open a web browser and navigate to the URL (usually `

2.  **Check the Interface:** The web interface should load.  Inspect the HTML and JavaScript to ensure the application is working correctly.  Specifically, look for the device list.

3.  **Verify Database Connection:** (More advanced) You could use a SQLite browser to connect to the `devices.db` file and examine its contents to confirm that data is being stored.
