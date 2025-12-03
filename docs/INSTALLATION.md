# Installation Guide

## Prerequisites

*   Python 3.8 or higher
*   pip (Python package installer)

## Dependencies

The following Python packages are required:

*   Flask
*   sqlite3
*   pytz
*   requests  (For potential future speed testing integration)
*   beautifulsoup4 (potentially, if web scraping is added)

## Installation Steps

1.  **Clone the repository:**

    ```bash
    git clone [Repository URL]
    cd [Repository Directory]
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate  # On Windows
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**

    ```bash
    python app.py
    ```

    This will start the Flask development server, typically on `

## Initial Setup

*   The database file (`packages.db`) will be created in the same directory as the `app.py` file.
*   The first time you run the application, it will automatically create the necessary tables in the database.

## Verifying Installation

1.  **Open your web browser and navigate to `
2.  **You should see the `index.html` page**, displaying a list of devices with their status, last seen time, and other information.
3.  **Click on the "Admin" link** to access the admin interface.
4.  **Add a new device** through the admin interface to verify the device addition functionality.
