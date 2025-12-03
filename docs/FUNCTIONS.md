# Function Reference

## app.py
### index(request)
- Description: Renders the main dashboard HTML page.
- Parameters: None
- Returns: None
- Example: `index(request)`

### fetchData()
- Description: Fetches data from the API and updates the dashboard.
- Parameters: None
- Returns: None
- Example: `fetchData()`

### updateBigClock(hour, minute)
- Description: Updates the big clock display with the given hour and minute.
- Parameters:
  - `hour` (int): The hour (0-23).
  - `minute` (int): The minute (0-59).
- Returns: None
- Example: `updateBigClock(10, 30)`

### loadHolidayTheme(holiday)
- Description: Loads the appropriate holiday theme based on the provided holiday name.
- Parameters:
  - `holiday` (str): The name of the holiday (e.g., "christmas", "halloween").
- Returns: None
- Example: `loadHolidayTheme("christmas")`

### init()
- Description: Initializes the application and sets up initial conditions.
- Parameters: None
- Returns: None
- Example: `init()`

### periodic_scan()
- Description: Regularly scans for new devices and updates their status.
- Parameters: None
- Returns: None
- Example: `periodic_scan()`

### periodic_speed_test()
- Description: Runs a speed test (likely fetches network speed data).
- Parameters: None
- Returns: None
- Example: `periodic_speed_test()`

### periodic_package_updates()
- Description: Updates package statuses, moving delivered packages to the archive table.
- Parameters: None
- Returns: None
- Example: `periodic_package_updates()`

### periodic_package_archiving()
- Description: Automatically archives delivered packages.
- Parameters: None
- Returns: None
- Example: `periodic_package_archiving()`

### run_speed_test()
- Description: Likely uses an external API to get network speed data.
- Parameters: None
- Returns: None
- Example: `run_speed_test()`

### loadHolidayTheme(holiday)
- Description: Loads the appropriate holiday theme based on the provided holiday name.
- Parameters:
  - `holiday` (str): The name of the holiday (e.g., "christmas", "halloween").
- Returns: None
- Example: `loadHolidayTheme("christmas")`

## templates/rpi_dashboard.html
### init()
- Description: Initializes the application and sets up initial conditions.
- Parameters: None
- Returns: None
- Example: `init()`

### index(request)
- Description: Renders the main dashboard HTML page.
- Parameters:
  - `request` (flask.request): The Flask request object.
- Returns: None
- Example: `index(request)`

### loadHolidayTheme(holiday)
- Description: Loads the appropriate holiday theme based on the provided holiday name.
- Parameters:
  - `holiday` (str): The name of the holiday (e.g., "christmas", "halloween").
- Returns: None
- Example: `loadHolidayTheme("christmas")`

### index(request)
- Description: Renders the main dashboard HTML page.
- Parameters:
  - `request` (flask.request): The Flask request object.
- Returns: None
- Example: `index(request)`

### loadHolidayTheme(holiday)
- Description: Loads the appropriate holiday theme based on the provided holiday name.
- Parameters:
  - `holiday` (str): The name of the holiday (e.g., "christmas", "halloween").
- Returns: None
- Example: `loadHolidayTheme("christmas")`

**New Information - Brain Function & GABA**

The formation of neural networks requires a process of synaptic plasticity, where connections between neurons are strengthened or weakened. This process is often inhibited by the presence of the neurotransmitter GABA, which is an inhibitory neurotransmitter. GABA receptors are found on many neurons, and when GABA binds to these receptors, it reduces the likelihood that the neuron will fire. This makes it more difficult for neural networks to form, which can have a wide range of effects on behavior and cognition. During early development, GABAergic inhibition is essential for sculpting the developing brain. The precise timing and location of inhibition help to refine neural circuits and establish functional connections. GABAergic dysfunction has been implicated in a number of mental health conditions, including anxiety, depression, and epilepsy. Its inhibitory effects can help to stabilize neural activity and prevent excessive excitation, which is thought to be important for cognitive processes like attention, learning, and memory.
