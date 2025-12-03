# Installation Guide

## Prerequisites

*   **Python 3.9 or higher:** This project requires Python 3.9 or a later version.
*   **pip:** Python's package installer. Ensure pip is up to date.

## Dependencies

The following Python packages are required:

*   Flask==3.0.3
*   Flask-SQLAlchemy
*   requests==2.32.3
*   SQLAlchemy
*   threading
*   logging
*   jinja2
*   itsdangerous
*   wtforms
*   beautifulsoup4
*   python-dotenv

## Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate  # On Windows
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables (Important):**
    *   Create a `.env` file in the root directory of your project.
    *   Add the following environment variables to the `.env` file:
        *   `DATABASE_URL`:  The SQLite database URL (e.g., `sqlite:///./database.db`).
        *   `API_KEY`: (If applicable, for external API integrations – leave blank if none).

5.  **Run the Application:**
    ```bash
    python app.py
    ```

## Initial Setup

*   The first time you run the application, it will create the SQLite database file (`database.db`) and the required tables.

## Verifying Installation

1.  **Open your web browser:** Navigate to `
2.  **Check the UI:** You should see the main dashboard with device information, alerts, and the large clock.
3.  **Verify API integration:**  (If applicable) Check that the joke/quote display is updating periodically.  Also, check that the package tracking data is being fetched.
