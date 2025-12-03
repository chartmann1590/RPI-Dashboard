# Usage Guide

## Getting Started

This project provides a comprehensive dashboard integrating data from various sources, including Home Assistant, weather services, sports data, and a shopping list. To get started, you'll need a basic understanding of HTML, CSS, and JavaScript.  The primary JavaScript file, `main.js`, handles all the data fetching and dashboard logic.

## Basic Usage

The dashboard is organized into several sections, each displaying data from a different source:

*   **Home Assistant:** Displays real-time status of your Home Assistant devices, including lights, thermostats, and sensors.  This section relies on a Home Assistant instance running locally.
*   **Weather:** Shows current weather conditions and forecasts from multiple weather services (OpenWeatherMap and AccuWeather).
*   **Sports:** Displays live scores and statistics for selected sports teams. You can select your favorite teams to track.
*   **Shopping List:** Allows you to manage your shopping list. You can add items, mark them as purchased, and view your list.
*   **Calendar:** Displays your calendar events and integrates with your calendar services.

**Basic Navigation:**  You can navigate between these sections using the menu at the top of the page.

## Features

### Home Assistant

*   **Device Status:**  Shows the current status of all connected Home Assistant devices.
*   **Real-time Updates:**  The Home Assistant section is updated automatically every 5 minutes.
*   **Authentication:** This section relies on a Home Assistant instance already being set up and running. It does *not* handle user authentication for the Home Assistant instance itself.

### Weather

*   **Multi-Source Data:**  The weather information is pulled from both OpenWeatherMap and AccuWeather for redundancy.
*   **Unit Selection:** You can choose to view temperature in Celsius or Fahrenheit.
*   **Detailed Forecasts:** Displays hourly weather forecasts.

### Sports

*   **Team Selection:** Select your favorite sports teams to track their live scores.
*   **Real-time Updates:** The sports scores are updated in real-time.
*   **Data Source:** This section relies on external sports data APIs.

### Shopping List

*   **Add Items:**  Add items to your shopping list by typing them into the input field and pressing Enter.
*   **Mark as Purchased:** Mark items as purchased by clicking the checkbox next to them.  Purchased items are visually distinguished.
*   **Persistence:** The shopping list is persisted using local storage, so it will be retained across page refreshes.

### Calendar

*   **Event Management:** Add new calendar events.
*   **Feed Integration:** The calendar integrates with your calendar services.
*   **Event Deletion:** Delete calendar events.
*   **Feed Deletion:** Delete calendar feeds.
*   **Event Editing:** Edit calendar events.

### General Features

*   **Auto-Refresh:** The entire dashboard refreshes automatically every 60 seconds.
*   **Responsive Design:** The dashboard is designed to adapt to different screen sizes.

## Examples

### Adding a Shopping List Item

1.  Navigate to the Shopping List section.
2.  Enter the name of the item you want to add into the input field.
3.  Press Enter. The item will be added to the shopping list.

### Selecting a Sports Team

1.  Navigate to the Sports section.
2.  Click on the name of the team you want to track. The team's live scores will be displayed.

### Viewing Weather Forecasts

1.  Navigate to the Weather section.
2.  The current weather conditions and hourly forecast will be displayed.

## Tips

*   **Monitor Refresh Rate:** The auto-refresh feature can be beneficial for keeping the dashboard up-to-date, but it can also consume resources.
*   **Team Selection:** Carefully select your favorite sports teams to avoid overwhelming the sports section with irrelevant data.
*   **Error Handling:** If you encounter any errors, check the browser's console for debugging information.
