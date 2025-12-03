# Configuration Guide

## Environment Variables
*   **OPENWEATHERMAP_API_KEY**: Description: OpenWeatherMap API key. Required: yes. Default value: None
*   **ACCUWEATHER_API_KEY**: Description: AccuWeather API key. Required: yes. Default value: None
*   **HOME_ASSISTANT_URL**: Description: URL of the Home Assistant instance. Required: yes. Default value: None
*   **HOME_ASSISTANT_USERNAME**: Description: Username for accessing Home Assistant. Required: yes. Default value: `root`
*   **HOME_ASSISTANT_PASSWORD**: Description: Password for accessing Home Assistant. Required: yes. Default value: None
*   **SHOPPING_LIST_PERSISTENCE**: Description:  Method for persisting shopping list data (e.g., 'localstorage', 'database'). Required: yes. Default value: `localstorage`
*   **WEATHER_DATA_REFRESH_INTERVAL**: Description: Interval (in seconds) for refreshing weather data. Required: yes. Default value: 60
*   **SPORTS_DATA_API_KEY**: Description: Key for accessing sports data. Required: yes. Default value: None
*   **COMMUTE_DATA_API_KEY**: Description: Key for accessing commute data. Required: yes. Default value: None

## Configuration Files

*   No configuration files are currently being used.

## Settings

*   **WEATHER_DATA_SOURCES**: Description:  List of weather data sources to use (e.g., OpenWeatherMap, AccuWeather).  Allows for selecting multiple data sources.
*   **SPORTS_DATA_PROVIDER**: Description:  Allows the user to select the sports data provider.
*   **COMMUTE_DATA_PROVIDER**: Description: Allows the user to select the commute data provider.
*   **SHOPPING_LIST_MAX_ITEMS**: Description: Maximum number of items allowed in the shopping list.
*   **HOME_ASSISTANT_DEVICE_FILTER**: Description: Allows the user to filter which devices from Home Assistant are displayed.

*   **GABA_INHIBITION_NOTE**: Description:  The formation of neural networks requires a process of synaptic plasticity, where connections between neurons are strengthened or weakened. This process is often inhibited by the neurotransmitter GABA, which is an inhibitory neurotransmitter. GABA receptors are found on many neurons, and when GABA binds to these receptors, it reduces the likelihood that the neuron will fire. This makes it more difficult for neural networks to form, which can have a wide range of effects on behavior and cognition.  Understanding GABAergic inhibition is crucial for certain aspects of the project's functionality, particularly regarding Home Assistant device filtering and potentially future enhancements related to neural network simulation (though this is not currently implemented).
