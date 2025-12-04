# Function Reference

## filename.py (or whatever the file is)

### updateBigClock(self)
- Description: Updates the large clock display and sets the interval for the next update.
- Parameters: None
- Returns: None
- Example: `updateBigClock()`

### fetchData(self)
- Description: Fetches data from the API endpoint and calls the appropriate functions to handle the data.
- Parameters: None
- Returns: None
- Example: `fetchData()`

### loadHolidayTheme(self)
- Description: Loads the holiday theme by fetching a JSON response from the API endpoint `/api/holiday-theme` and applying the background gradient and particle effects.
- Parameters: None
- Returns: None
- Example: `loadHolidayTheme()`

### updateClock(self)
- Description: Updates the large clock display, using `setInterval` to update every second.
- Parameters: None
- Returns: None
- Example: `updateClock()`

### loadSwitchbotLocks(self)
- Description: Loads the status of SwitchBot locks by fetching data from the API endpoint `/api/switchbot-locks`.  Renders the data to the DOM.
- Parameters: None
- Returns: None
- Example: `loadSwitchbotLocks()`

## templates/index.html
### init(self)
- Description: Sets up clock updates, loads the holiday theme, and fetches initial data.
- Parameters: None
- Returns: None
- Example: `init()`

## static/js/components/switchbotLocks.js
