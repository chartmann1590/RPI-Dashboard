# Usage Guide

## Getting Started

To get started with this project, you need to ensure you have the necessary JavaScript files and dependencies. The main JavaScript file, `static/js/components/switchbotLocks.js`, handles the lock status data fetching and rendering.  It relies on the API endpoint `/api/switchbot-locks` to retrieve the lock data.  The HTML file `templates/rpi_dashboard.html` utilizes this component. The main dashboard utilizes all the components and features to display data and provide a single point of control.

## Basic Usage

The core functionality revolves around displaying the status of SwitchBot locks. The `switchbotLocks.js` component fetches data from the `/api/switchbot-locks` API endpoint and renders it within the `rpi_dashboard.html` page.  Each lock is displayed as a card showing its status (locked or unlocked) and a relevant icon. The locks are arranged using flexbox.

## Features

### Lock Status Display

The primary feature is the display of SwitchBot lock status.  The `switchbotLocks.js` component fetches the current state of each lock from the `/api/switchbot-locks` API endpoint. This endpoint returns an array of JSON objects, where each object represents a SwitchBot lock and contains the following key-value pairs:

*   `name`: (String) The name of the SwitchBot lock.
*   `status`: (String) The current status of the lock ("Locked" or "Unlocked").
*   `icon`: (String) The icon to display for the lock status.

### API Interaction

The project uses `fetch` to communicate with the `/api/switchbot-locks` API endpoint. The `fetch` operation attempts to retrieve the latest lock status data. The API endpoint provides a simple, JSON-based interface.

### Responsive Layout

The lock status display uses flexbox to create a responsive layout. This ensures that the lock cards adapt to different screen sizes. The layout utilizes `display: flex; align-items: center; justify-content: space-between;` to arrange the icon, status text, and name/device ID.

### Error Handling

The JavaScript code includes a `try...catch` block to handle potential errors during the `fetch` operation. If an error occurs, a generic error message is displayed to the user.

### Data Format

The `/api/switchbot-locks` API endpoint returns a JSON array like this:


[
  {
    "name": "Bedroom Lock",
    "status": "Locked",
    "icon": "🔒"
  },
  {
    "name": "Living Room Lock",
    "status": "Unlocked",
    "icon": "🔓"
  }
]

### Responsive Design Considerations

The application utilizes flexbox to create a responsive layout. The lock items are arranged with the status indicator to the right and the name/device ID to the left. This responsive layout adapts to various screen sizes, ensuring that the lock status is consistently displayed.

## Examples

### Displaying Lock Status

To display the lock status, the HTML file includes the `switchbotLocks.js` component, which fetches and renders the lock data.  This displays the locks in the rpi_dashboard.html

## Tips

*   Ensure the `/api/switchbot-locks` endpoint is running correctly and accessible.
*   Check the API response format to verify it matches the expected structure.
*   Adjust the CSS styles to customize the appearance of the lock status display.
*   Monitor the error handling mechanism to identify and resolve any issues related to the API interaction.
