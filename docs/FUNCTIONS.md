# Function Reference

## weather.py
### load_weather()
- Description: Fetches weather data from multiple APIs (OpenWeatherMap, AccuWeather) and combines the results.
- Parameters: None
- Returns: A dictionary containing weather data (temperature, description, feels like temperature, humidity, wind speed) from the combined APIs.  Returns None if there's an error fetching data.
- Example: `weather_data = load_weather()`

### get_open_weather_map_data(api_key, location)
- Description: Fetches weather data from OpenWeatherMap.
- Parameters:
  - `api_key` (str): Your OpenWeatherMap API key.
  - `location` (str): The location (city name) to fetch weather data for.
- Returns: A dictionary containing weather data from OpenWeatherMap, or None if there’s an error.
- Example: `open_weather_data = get_open_weather_map_data("YOUR_API_KEY", "London")`

### get_accuweather_data(api_key, location)
- Description: Fetches weather data from AccuWeather.
- Parameters:
  - `api_key` (str): Your AccuWeather API key.
  - `location` (str): The location (city name) to fetch weather data for.
- Returns: A dictionary containing weather data from AccuWeather, or None if there’s an error.
- Example: `accuweather_data = get_accuweather_data("YOUR_API_KEY", "London")`

### combine_weather_data(open_weather_data, accuweather_data)
- Description: Combines weather data from OpenWeatherMap and AccuWeather.  Handles cases where one API might be unavailable.
- Parameters:
  - `open_weather_data` (dict):  Weather data from OpenWeatherMap.
  - `accuweather_data` (dict): Weather data from AccuWeather.
- Returns: A dictionary containing combined weather data, or None if there was an error combining the data.
- Example: `combined_data = combine_weather_data(open_weather_data, accuweather_data)`

## forecast.py
### load_forecast()
- Description: Fetches weather forecast data from OpenWeatherMap.
- Parameters:
  - `api_key` (str): Your OpenWeatherMap API key.
  - `location` (str): The location (city name) to fetch weather forecast data for.
- Returns: A dictionary containing weather forecast data from OpenWeatherMap, or None if there’s an error.
- Example: `forecast_data = load_forecast("YOUR_API_KEY", "London")`

### get_open_weather_map_forecast_data(api_key, location)
- Description: Fetches weather forecast data from OpenWeatherMap.
- Parameters:
  - `api_key` (str): Your OpenWeatherMap API key.
  - `location` (str): The location (city name) to fetch weather forecast data for.
- Returns: A dictionary containing weather forecast data from OpenWeatherMap, or None if there’s an error.
- Example: `open_weather_forecast_data = get_open_weather_map_forecast_data("YOUR_API_KEY", "London")`

## news.py
### load_news()
- Description: Fetches news headlines from various sources (NewsAPI).
- Parameters:
  - `api_key` (str): Your NewsAPI API key.
  - `category` (str, optional): The category of news to fetch (e.g., "world", "sports"). Defaults to "world".
- Returns: A list of dictionaries, where each dictionary represents a news article with its title, description, and link. Returns an empty list if there’s an error.
- Example: `news_articles = load_news()`

### get_newsapi_articles(api_key, category)
- Description: Retrieves news articles from NewsAPI based on the specified category.
- Parameters:
    - `api_key` (str): Your NewsAPI API key.
    - `category` (str): The news category.
- Returns: A list of dictionaries containing news articles, or an empty list in case of errors.
- Example: `news_articles = get_newsapi_articles("YOUR_API_KEY", "sports")`

## joke.py
### load_joke()
- Description: Fetches a random joke.
- Parameters: None
- Returns: A string containing the joke.  Returns None if there’s an error.
- Example: `joke = load_joke()`

### load_joke_history()
- Description: Retrieves a history of previously fetched jokes.
- Parameters: None
- Returns: A list of strings, where each string is a previously fetched joke. Returns an empty list if there’s an error.
- Example: `joke_history = load_joke_history()`

## calendar.py
### load_calendar_events()
- Description: Fetches calendar events.
- Parameters: None
- Returns: A list of dictionaries, where each dictionary represents a calendar event with its title, description, and date. Returns an empty list if there’s an error.
- Example: `calendar_events = load_calendar_events()`

### get_open_weather_map_calendar_events(api_key, start_date, end_date)
- Description: Retrieves calendar events based on a specified date range.
- Parameters:
  - `api_key` (str): Your OpenWeatherMap API key.
  - `start_date` (str): The start date of the period
  - `end_date` (str): The end date of the period
- Returns: A list of dictionaries containing calendar events, or an empty list if there’s an error.
- Example: `calendar_events = get_open_weather_map_calendar_events("YOUR_API_KEY", "2023-10-26", "2023-10-27")`

### get_open_weather_map_calendar_feeds(api_key)
- Description: Retrieves calendar feeds.
- Parameters:
    - `api_key` (str): Your OpenWeatherMap API key.
- Returns: A list of calendar feeds, or an empty list if there’s an error.
- Example: `calendar_feeds = get_open_weather_map_calendar_feeds("YOUR_API_KEY")`

### load_local_events()
- Description:  Loads calendar events from the system.
- Parameters: None
- Returns: A list of events.

### get_open_weather_map_calendar_events(api_key, start_date, end_date)
- Description: Fetches calendar events based on a specified date range.
- Parameters:
  - `api_key` (str): Your OpenWeatherMap API key.
  - `start_date` (str): The start date of the period
  - `end_date` (str): The end date of the period
- Returns: A list of dictionaries containing calendar events, or an empty list if there’s an error.
- Example: `calendar_events = get_open_weather_map_calendar_events("YOUR_API_KEY", "2023-10-26", "2023-10-27")`

### delete_feed()
- Description: Deletes calendar feed.
- Parameters: None
- Returns: None

### delete_event()
- Description: Deletes a calendar event
- Parameters: None
- Returns: None

### edit_event()
- Description: Edits a calendar event.
- Parameters: None
- Returns: None

## commute.py
### load_commute_info()
- Description: Fetches commute information.
- Parameters: None
- Returns: A dictionary containing commute information (e.g., traffic conditions, estimated travel time). Returns None if there's an error.
- Example: `commute_data = load_commute_info()`

### load_traffic_history()
- Description: Retrieves traffic history data.
- Parameters: None
- Returns: A list of dictionaries containing traffic data.
- Example: `traffic_history = load_traffic_history()`

### setup_commute_form()
- Description: Sets up the commute form.
- Parameters: None
- Returns: None

## airQuality.py
### load_air_quality()
- Description: Fetches air quality data.
- Parameters: None
- Returns: A dictionary containing air quality data. Returns None if there’s an error.
- Example: `air_quality_data = load_air_quality()`

## homeAssistant.py
### load_homeAssistant_data()
- Description: Fetches data from Home Assistant.
- Parameters: None
- Returns: A dictionary containing Home Assistant data. Returns None if there’s an error.
- Example: `home_assistant_data = load_homeAssistant_data()`

## weatherAlerts.py
### load_weather_alerts()
- Description: Fetches weather alerts.
- Parameters: None
- Returns: A list of dictionaries containing weather alerts.  Returns an empty list if there’s an error.
- Example: `weather_alerts = load_weather_alerts()`

## shoppingList.py
### load_shopping_list()
- Description: Loads shopping list
- Parameters: None
- Returns: A list of items on the shopping list.
- Example: `shopping_list = load_shopping_list()`

### toggle_shopping_item()
- Description: Adds or removes items from the shopping list.
- Parameters: None
- Returns: None

### delete_shopping_item()
- Description: Deletes an item from the shopping list
- Parameters: None
- Returns: None

## package.py
### load_packages()
- Description: Loads a list of packages.
- Parameters: None
- Returns: A list of packages.
- Example: `package_list = load_packages()`

## homeAssistant.py
### load_homeAssistant_data()
- Description: Fetches data from Home Assistant.
- Parameters: None
- Returns: A dictionary containing Home Assistant data. Returns None if there’s an error.
- Example: `home_assistant_data = load_homeAssistant_data()`

## weatherAlerts.py
### load_weather_alerts()
- Description: Fetches weather alerts.
- Parameters: None
- Returns: A list of dictionaries containing weather alerts.  Returns an empty list if there’s an error.
- Example: `weather_alerts = load_weather_alerts()`

## package.py
### load_packages()
- Description: Loads a list of packages.
- Parameters: None
- Returns: A list of packages.
- Example: `package_list = load_packages()`

## weatherAlerts.py
### load_weather_alerts()
- Description: Fetches weather alerts.
- Parameters: None
- Returns: A list of dictionaries containing weather alerts.  Returns an empty list if there’s an error.
- Example: `weather_alerts = load_weather_alerts()`

## package.py
### load_packages()
- Description: Loads a list of packages.
- Parameters: None
- Returns: A list of packages.
- Example: `package_list = load_packages()`
