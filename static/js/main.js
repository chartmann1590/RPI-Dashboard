// Main JavaScript - Orchestrates all components
console.log('main.js: Starting to load modules...');

// Use dynamic imports to handle failures gracefully
let loadWeather, loadForecast, loadNews, loadJoke, loadJokeHistory, setupJokePagination;
let loadCalendarEvents, loadCalendarFeeds, loadLocalEvents, deleteFeed, deleteEvent, editEvent;
let loadCommuteInfo, loadTrafficHistory, setupCommuteForm;
let loadAirQuality;
let loadQuote, loadQuoteHistory, setupQuotePagination;
let loadAstronomy;
let loadInternetSpeed, setupSpeedTestButton;
let loadSportsTeams, loadSportsScores, removeTeam;
let loadPhotos, setupPhotoUpload, deletePhoto;
let loadPackages, loadPackagesArchive, setupPackageForm, setupArchivePagination, refreshPackage, deletePackage;
let loadShoppingList, setupShoppingListForm, toggleShoppingItem, deleteShoppingItem;
let loadHomeAssistant;
let loadWeatherAlerts;

(async () => {
    const loadModule = async (path, name) => {
        try {
            return await import(path);
        } catch (error) {
            console.error(`Failed to load ${name}:`, error);
            return null;
        }
    };
    
    try {
        const weatherModule = await loadModule('./components/weather.js', 'weather');
        if (weatherModule) loadWeather = weatherModule.loadWeather;
        
        const forecastModule = await loadModule('./components/forecast.js', 'forecast');
        if (forecastModule) loadForecast = forecastModule.loadForecast;
        
        const newsModule = await loadModule('./components/news.js', 'news');
        if (newsModule) loadNews = newsModule.loadNews;
        
        const jokeModule = await loadModule('./components/joke.js', 'joke');
        if (jokeModule) {
            loadJoke = jokeModule.loadJoke;
            loadJokeHistory = jokeModule.loadJokeHistory;
            setupJokePagination = jokeModule.setupJokePagination;
        }
        
        const calendarModule = await loadModule('./components/calendar.js', 'calendar');
        if (calendarModule) {
            loadCalendarEvents = calendarModule.loadCalendarEvents;
            loadCalendarFeeds = calendarModule.loadCalendarFeeds;
            loadLocalEvents = calendarModule.loadLocalEvents;
            deleteFeed = calendarModule.deleteFeed;
            deleteEvent = calendarModule.deleteEvent;
            editEvent = calendarModule.editEvent;
        }
        
        const commuteModule = await loadModule('./components/commute.js', 'commute');
        if (commuteModule) {
            loadCommuteInfo = commuteModule.loadCommuteInfo;
            loadTrafficHistory = commuteModule.loadTrafficHistory;
            setupCommuteForm = commuteModule.setupCommuteForm;
        }
        
        const airQualityModule = await loadModule('./components/airQuality.js', 'airQuality');
        if (airQualityModule) loadAirQuality = airQualityModule.loadAirQuality;
        
        const quoteModule = await loadModule('./components/quote.js', 'quote');
        if (quoteModule) {
            loadQuote = quoteModule.loadQuote;
            loadQuoteHistory = quoteModule.loadQuoteHistory;
            setupQuotePagination = quoteModule.setupQuotePagination;
        }
        
        const astronomyModule = await loadModule('./components/astronomy.js', 'astronomy');
        if (astronomyModule) loadAstronomy = astronomyModule.loadAstronomy;
        
        const internetSpeedModule = await loadModule('./components/internetSpeed.js', 'internetSpeed');
        if (internetSpeedModule) {
            loadInternetSpeed = internetSpeedModule.loadInternetSpeed;
            setupSpeedTestButton = internetSpeedModule.setupSpeedTestButton;
        }
        
        const sportsModule = await loadModule('./components/sports.js', 'sports');
        if (sportsModule) {
            loadSportsTeams = sportsModule.loadSportsTeams;
            loadSportsScores = sportsModule.loadSportsScores;
            removeTeam = sportsModule.removeTeam;
        }
        
        const photosModule = await loadModule('./components/photos.js', 'photos');
        if (photosModule) {
            loadPhotos = photosModule.loadPhotos;
            setupPhotoUpload = photosModule.setupPhotoUpload;
            deletePhoto = photosModule.deletePhoto;
        }
        
        const packagesModule = await loadModule('./components/packages.js', 'packages');
        if (packagesModule) {
            loadPackages = packagesModule.loadPackages;
            loadPackagesArchive = packagesModule.loadPackagesArchive;
            setupPackageForm = packagesModule.setupPackageForm;
            setupArchivePagination = packagesModule.setupArchivePagination;
            refreshPackage = packagesModule.refreshPackage;
            deletePackage = packagesModule.deletePackage;
        }
        
        const shoppingListModule = await loadModule('./components/shoppingList.js', 'shoppingList');
        if (shoppingListModule) {
            loadShoppingList = shoppingListModule.loadShoppingList;
            setupShoppingListForm = shoppingListModule.setupShoppingListForm;
            toggleShoppingItem = shoppingListModule.toggleShoppingItem;
            deleteShoppingItem = shoppingListModule.deleteShoppingItem;
        }
        
        const homeAssistantModule = await loadModule('./components/homeAssistant.js', 'homeAssistant');
        if (homeAssistantModule) loadHomeAssistant = homeAssistantModule.loadHomeAssistant;
        
        const weatherAlertsModule = await loadModule('./components/weatherAlerts.js', 'weatherAlerts');
        if (weatherAlertsModule) loadWeatherAlerts = weatherAlertsModule.loadWeatherAlerts;
        
        console.log('All modules loaded successfully');
        
        // Make functions available globally for onclick handlers
        if (deleteFeed) window.deleteFeed = deleteFeed;
        if (deleteEvent) window.deleteEvent = deleteEvent;
        if (editEvent) window.editEvent = editEvent;
        if (removeTeam) window.removeTeam = removeTeam;
        if (deletePhoto) window.deletePhoto = deletePhoto;
        if (refreshPackage) window.refreshPackage = refreshPackage;
        if (deletePackage) window.deletePackage = deletePackage;
        if (toggleShoppingItem) window.toggleShoppingItem = toggleShoppingItem;
        if (deleteShoppingItem) window.deleteShoppingItem = deleteShoppingItem;
        
        window.mainJsLoaded = true;
        
        // Initialize dashboard
        initializeDashboard();
    } catch (error) {
        console.error('Error loading modules:', error);
    }
})();

// Load all dashboard data
async function loadDashboardData() {
    // Load components that use dashboard data
    // These functions will fetch their own data
    const promises = [];
    if (loadWeather) promises.push(loadWeather().catch(e => console.error('Error loading weather:', e)));
    if (loadForecast) promises.push(loadForecast().catch(e => console.error('Error loading forecast:', e)));
    if (loadNews) promises.push(loadNews().catch(e => console.error('Error loading news:', e)));
    if (loadJoke) promises.push(loadJoke().catch(e => console.error('Error loading joke:', e)));
    if (loadJokeHistory) promises.push(loadJokeHistory().catch(e => console.error('Error loading joke history:', e)));
    if (loadWeatherAlerts) promises.push(loadWeatherAlerts().catch(e => console.error('Error loading weather alerts:', e)));
    if (loadPackages) promises.push(loadPackages().catch(e => console.error('Error loading packages:', e)));
    
    await Promise.all(promises);
}

// Setup all form handlers
function setupForms() {
    // Calendar forms
    const addFeedForm = document.getElementById('add-feed-form');
    if (addFeedForm && !addFeedForm.hasAttribute('data-listener-added')) {
        addFeedForm.setAttribute('data-listener-added', 'true');
        addFeedForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('feed-name').value;
            const url = document.getElementById('feed-url').value;
            
            try {
                const response = await fetch('/api/calendar-feeds', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, url })
                });
                if (response.ok) {
                    document.getElementById('feed-name').value = '';
                    document.getElementById('feed-url').value = '';
                    loadCalendarFeeds();
                    loadCalendarEvents();
                }
            } catch (error) {
                console.error('Error adding feed:', error);
                alert('Error adding feed');
            }
        });
    }
    
    const addEventForm = document.getElementById('add-event-form');
    if (addEventForm && !addEventForm.hasAttribute('data-listener-added')) {
        addEventForm.setAttribute('data-listener-added', 'true');
        addEventForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const title = document.getElementById('event-title').value;
            const start_time = document.getElementById('event-start').value.replace('T', ' ') + ':00';
            const end_time = document.getElementById('event-end').value ? document.getElementById('event-end').value.replace('T', ' ') + ':00' : null;
            const location = document.getElementById('event-location').value;
            const description = document.getElementById('event-description').value;
            
            try {
                const response = await fetch('/api/calendar-events/local', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, start_time, end_time, location, description })
                });
                if (response.ok) {
                    addEventForm.reset();
                    loadLocalEvents();
                    loadCalendarEvents();
                }
            } catch (error) {
                console.error('Error adding event:', error);
                alert('Error adding event');
            }
        });
    }
    
    // Commute form
    if (setupCommuteForm) setupCommuteForm();
    
    // Sports form
    const sportsForm = document.getElementById('sports-form');
    if (sportsForm && !sportsForm.hasAttribute('data-listener-added')) {
        sportsForm.setAttribute('data-listener-added', 'true');
        sportsForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const teamInput = document.getElementById('sports-team-input');
            const sportSelect = document.getElementById('sports-sport-select');
            const newTeamName = teamInput.value.trim();
            const newTeamSport = sportSelect.value;
            
            if (!newTeamName) {
                alert('Please enter a team name');
                return;
            }
            
            try {
                // Get current teams
                const getResponse = await fetch('/api/settings/sports');
                const data = await getResponse.json();
                let teams = data.teams || [];
                
                // Normalize teams to object format for comparison
                const normalizedTeams = teams.map(t => {
                    if (typeof t === 'string') {
                        return { name: t, sport: 'Unknown' };
                    }
                    return t;
                });
                
                // Check if team already exists
                const teamExists = normalizedTeams.some(t => t.name.toLowerCase() === newTeamName.toLowerCase());
                if (teamExists) {
                    alert('This team is already in your list');
                    teamInput.value = '';
                    return;
                }
                
                // Add new team as object with name and sport
                teams.push({ name: newTeamName, sport: newTeamSport });
                
                // Save updated teams
                const saveResponse = await fetch('/api/settings/sports', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ teams })
                });
                
                if (saveResponse.ok) {
                    teamInput.value = '';
                    loadSportsTeams();
                    loadSportsScores();
                } else {
                    alert('Error adding team');
                }
            } catch (error) {
                console.error('Error adding team:', error);
                alert('Error adding team');
            }
        });
    }
    
    // Package form
    if (setupPackageForm) setupPackageForm();
    
    // Shopping list form
    if (setupShoppingListForm) setupShoppingListForm();
    
    // Photo upload
    if (setupPhotoUpload) setupPhotoUpload();
    
    // Speed test button
    if (setupSpeedTestButton) setupSpeedTestButton();
}

// Initialize everything when DOM is ready
function initializeDashboard() {
    if (!loadWeather || !loadForecast) {
        console.error('Modules not loaded yet, waiting...');
        setTimeout(initializeDashboard, 100);
        return;
    }
    console.log('DOM loaded, initializing dashboard...');
    
    // Load all data
    loadDashboardData().catch(err => console.error('Error in loadDashboardData:', err));
    if (loadJokeHistory) loadJokeHistory().catch(err => console.error('Error in loadJokeHistory:', err));
    if (setupJokePagination) setupJokePagination();
    
    const componentPromises = [];
    if (loadCalendarEvents) componentPromises.push(loadCalendarEvents().catch(e => console.error('Error loading calendar events:', e)));
    if (loadCalendarFeeds) componentPromises.push(loadCalendarFeeds().catch(e => console.error('Error loading calendar feeds:', e)));
    if (loadLocalEvents) componentPromises.push(loadLocalEvents().catch(e => console.error('Error loading local events:', e)));
    if (loadCommuteInfo) componentPromises.push(loadCommuteInfo().catch(e => console.error('Error loading commute:', e)));
    if (loadAirQuality) componentPromises.push(loadAirQuality().catch(e => console.error('Error loading air quality:', e)));
    if (loadQuote) componentPromises.push(loadQuote().catch(e => console.error('Error loading quote:', e)));
    if (loadQuoteHistory) componentPromises.push(loadQuoteHistory().catch(e => console.error('Error loading quote history:', e)));
    if (loadAstronomy) componentPromises.push(loadAstronomy().catch(e => console.error('Error loading astronomy:', e)));
    if (loadInternetSpeed) componentPromises.push(loadInternetSpeed().catch(e => console.error('Error loading internet speed:', e)));
    if (loadSportsTeams) componentPromises.push(loadSportsTeams().catch(e => console.error('Error loading sports teams:', e)));
    if (loadSportsScores) componentPromises.push(loadSportsScores().catch(e => console.error('Error loading sports scores:', e)));
    if (loadPhotos) componentPromises.push(loadPhotos().catch(e => console.error('Error loading photos:', e)));
    if (loadShoppingList) componentPromises.push(loadShoppingList().catch(e => console.error('Error loading shopping list:', e)));
    if (loadHomeAssistant) componentPromises.push(loadHomeAssistant().catch(e => console.error('Error loading home assistant:', e)));
    if (loadPackagesArchive) componentPromises.push(loadPackagesArchive().catch(e => console.error('Error loading packages archive:', e)));
    
    Promise.all(componentPromises);
    
    if (setupQuotePagination) setupQuotePagination();
    if (setupArchivePagination) setupArchivePagination();
    
    // Setup all form handlers
    setupForms();
    
    // Refresh data every 5 minutes
    setInterval(() => {
        loadDashboardData();
        if (loadCalendarEvents) loadCalendarEvents();
        if (loadCommuteInfo) loadCommuteInfo();
        if (loadAirQuality) loadAirQuality();
        if (loadQuote) loadQuote();
        if (loadAstronomy) loadAstronomy();
        if (loadInternetSpeed) loadInternetSpeed();
        if (loadSportsScores) loadSportsScores();
        if (loadTrafficHistory) loadTrafficHistory();
        if (loadHomeAssistant) loadHomeAssistant();
    }, 300000); // 5 minutes
    
    // Auto-refresh page every 60 seconds for device status
    setTimeout(() => {
        location.reload();
    }, 60000);
}

console.log('main.js: Module setup complete');

