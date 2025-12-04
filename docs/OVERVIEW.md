# Project Overview

## Introduction
This project is a smart home dashboard, designed to monitor and control various smart home devices, primarily SwitchBot locks. It displays the status of these locks, allowing the user to quickly see if a door is locked or unlocked. The dashboard provides a centralized view of smart home device status, enhancing convenience and security.

## Key Features
*   **Real-time Lock Status:** Displays the current status (locked or unlocked) of all connected SwitchBot locks.
*   **Visual Status Indicators:**  Uses icons (🔒/🔓) and colored circles to visually represent the lock status.
*   **Automated Data Refresh:** The lock status is refreshed every 5 minutes, ensuring the information remains up-to-date.
*   **Holiday Theme:**  The dashboard incorporates a visually appealing holiday theme, featuring particle effects (snow, confetti, etc.) for a festive experience (specifically for Christmas).
*   **Error Handling:** Handles potential errors during data fetching and JSON parsing, providing a user-friendly error message in case of failure.
*   **Responsive Design:** The lock status display adapts to different screen sizes, providing a consistent experience across devices.

## Architecture
The project utilizes a component-based architecture, separating concerns for clarity and maintainability.  The core structure consists of:

*   **`static/js/components/switchbotLocks.js`:** This component is responsible for fetching the lock status data from the `/api/switchbot-locks` endpoint, rendering the lock status visually, and handling any potential errors.
*   **`templates/index.html`:** This HTML file is the main dashboard page. It utilizes the `switchbotLocks.js` component to display the lock status and provides the overall page structure.
*   **Backend API (`/api/switchbot-locks`):** (Implied, but crucial) This API endpoint is responsible for providing the JSON data containing the lock status. The exact implementation is not defined within the given code.

The key interaction flow is: `index.html` calls `switchbotLocks.js`, which fetches data from the API, and then renders the data in the HTML.

## Technology Stack
The project employs the following technologies:

*   **HTML5:** For structuring the web page.
*   **CSS:** For styling the dashboard and components.
*   **JavaScript:** For dynamic behavior, data fetching, rendering, and event handling.
*   **Fetch API:**  For making asynchronous HTTP requests to the `/api/switchbot-locks` endpoint.
*   **Jinja2 (likely):** A templating engine, used in `index.html` to dynamically generate HTML content from data. (This is inferred from the `{% ... %}` syntax)
*   **Leaflet.js:** A JavaScript library for creating interactive maps.  (Used to display the lock status visually and for the particle effects).
*   **Particle Effects Library:** (Unspecified, but necessary for the holiday theme).
