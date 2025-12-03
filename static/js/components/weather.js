// Weather Component
export async function loadWeather() {
    try {
        const response = await fetch('/api/dashboard-data');
        const data = await response.json();
        
        const widget = document.getElementById('weather-widget');
        if (!widget) return;
        
        if (data.weather) {
            widget.innerHTML = `
                <div class="weather-widget">
                    <div class="weather-main">
                        <div class="weather-temp">${data.weather.temp}°F</div>
                        <div class="weather-desc">${data.weather.description}</div>
                    </div>
                    <div class="weather-details">
                        <div class="weather-detail">
                            <span>Feels Like</span>
                            <span>${data.weather.feels_like}°F</span>
                        </div>
                        <div class="weather-detail">
                            <span>Humidity</span>
                            <span>${data.weather.humidity}%</span>
                        </div>
                        <div class="weather-detail">
                            <span>Wind</span>
                            <span>${data.weather.wind_speed} mph</span>
                        </div>
                    </div>
                </div>
            `;
        } else {
            widget.innerHTML = '<div class="error">Weather data unavailable</div>';
        }
    } catch (error) {
        console.error('Error loading weather:', error);
        const widget = document.getElementById('weather-widget');
        if (widget) {
            widget.innerHTML = '<div class="error">Failed to load weather data</div>';
        }
    }
}

