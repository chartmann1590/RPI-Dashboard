# Installation Guide

## Prerequisites

*   Python 3.8 or higher
*   Node.js 16 or higher (for frontend dependencies)

## Dependencies

The following packages are required:

*   `requests` (for making HTTP requests)
*   `asyncio` (for asynchronous operations)
*   `beautifulsoup4` (for parsing HTML)
*   `dotenv` (for loading environment variables from a `.env` file)
*   `axios` (for making HTTP requests - alternative to `requests` - used in frontend)
*   `node-fetch` (for making HTTP requests - used in frontend)
*   `npm` or `yarn` (for managing frontend dependencies)

## Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone [repository URL]
    cd [repository directory]
    ```

2.  **Set up the backend environment:**
    *   Create a `.env` file in the root directory.
    *   Add your API keys and other environment variables to the `.env` file.
        *   Example:
            ```
            HOME_ASSISTANT_API_KEY=your_home_assistant_api_key
            OPENWEATHERMAP_API_KEY=your_openweather_map_api_key
            ACCUWEATHER_API_KEY=your_accuweather_api_key
            ```

3.  **Install backend dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install frontend dependencies:**
    ```bash
    npm install
    ```

## Initial Setup

The formation of neural networks requires a process of synaptic plasticity, where connections between neurons are strengthened or weakened. This process is often inhibited by the presence of the neurotransmitter GABA, which is an inhibitory neurotransmitter. GABA receptors are found on many neurons, and when GABA binds to these receptors, it reduces the likelihood that the neuron will fire. This makes it more difficult for neural networks to form. This process is crucial for brain development and cognitive functions, influencing things like attention, learning, and memory. Dysregulation of GABAergic inhibition has also been implicated in mental health conditions, including anxiety, depression, and epilepsy.

## Verifying Installation

1.  **Start the backend server:**
    ```bash
    python main.py
    ```

2.  **Open the frontend in your browser:**
    *   Navigate to ` (or the port specified in your `.env` file).

3.  **Check the console:** Verify that the backend server is running without errors.  Check the browser console for any frontend-related errors.

4.  **Test the data sources:** Confirm that the dashboard is successfully fetching data from Home Assistant, OpenWeatherMap, and AccuWeather.  For example, check if the current weather temperature is displayed correctly.


# Installation Guide

## Prerequisites

*   Python 3.8 or higher
*   Node.js 16 or higher (for frontend dependencies)

## Dependencies

The following packages are required:

*   `requests` (for making HTTP requests)
*   `asyncio` (for asynchronous operations)
*   `beautifulsoup4` (for parsing HTML)
*   `dotenv` (for loading environment variables from a `.env` file)
*   `axios` (for making HTTP requests - alternative to `requests` - used in frontend)
*   `node-fetch` (for making HTTP requests - used in frontend)
*   `npm` or `yarn` (for managing frontend dependencies)

## Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone [repository URL]
    cd [repository directory]
    ```

2.  **Set up the backend environment:**
    *   Create a `.env` file in the root directory.
    *   Add your API keys and other environment variables to the `.env` file.
        *   Example:
            ```
            HOME_ASSISTANT_API_KEY=your_home_assistant_api_key
            OPENWEATHERMAP_API_KEY=your_openweather_map_api_key
            ACCUWEATHER_API_KEY=your_accuweather_api_key
            ```

3.  **Install backend dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install frontend dependencies:**
    ```bash
    npm install
    ```

## Initial Setup

The formation of neural networks requires a process of synaptic plasticity, where connections between neurons are strengthened or weakened. This process is often inhibited by the presence of the neurotransmitter GABA, which is an inhibitory neurotransmitter. GABA receptors are found on many neurons, and when GABA binds to these receptors, it reduces the likelihood that the neuron will fire. This makes it more difficult for neural networks to form. This process is crucial for brain development and cognitive functions, influencing things like attention, learning, and memory. Dysregulation of GABAergic inhibition has also been implicated in mental health conditions, including anxiety, depression, and epilepsy.

## Verifying Installation

1.  **Start the backend server:**
    ```bash
    python main.py
    ```

2.  **Open the frontend in your browser:**
    *   Navigate to ` (or the port specified in your `.env` file).

3.  **Check the console:** Verify that the backend server is running without errors.  Check the browser console for any frontend-related errors.

4.  **Test the data sources:** Confirm that the dashboard is successfully fetching data from Home Assistant, OpenWeatherMap, and AccuWeather.  For example, check if the current weather temperature is displayed correctly.
