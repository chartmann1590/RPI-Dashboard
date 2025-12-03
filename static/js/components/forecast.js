// Forecast Component
export async function loadForecast() {
    try {
        const response = await fetch('/api/dashboard-data');
        const data = await response.json();
        
        const widget = document.getElementById('forecast-widget');
        if (!widget) return;
        
        if (data.forecast) {
            let forecastHTML = '<div class="forecast-container">';
            
            // Hourly forecast
            if (data.forecast.hourly && data.forecast.hourly.length > 0) {
                forecastHTML += `
                    <div class="forecast-section">
                        <h3>Hourly Forecast</h3>
                        <div class="hourly-forecast">
                `;
                
                data.forecast.hourly.forEach(hour => {
                    forecastHTML += `
                        <div class="hourly-item">
                            <div class="hourly-time">${hour.time}</div>
                            <div class="hourly-temp">${hour.temp}°F</div>
                            <div class="hourly-desc">${hour.description}</div>
                        </div>
                    `;
                });
                
                forecastHTML += '</div></div>';
            }
            
            // Daily forecast
            if (data.forecast.daily && data.forecast.daily.length > 0) {
                forecastHTML += `
                    <div class="forecast-section">
                        <h3>3-Day Forecast</h3>
                        <div class="daily-forecast">
                `;
                
                data.forecast.daily.forEach(day => {
                    forecastHTML += `
                        <div class="daily-item">
                            <div class="daily-day">${day.day}</div>
                            <div class="daily-temps">
                                <span class="daily-high">${day.high}°</span> / ${day.low}°
                            </div>
                            <div class="daily-desc">${day.description}</div>
                        </div>
                    `;
                });
                
                forecastHTML += '</div></div>';
            }
            
            forecastHTML += '</div>';
            widget.innerHTML = forecastHTML;
        } else {
            widget.innerHTML = '<div class="error">Forecast data unavailable</div>';
        }
    } catch (error) {
        console.error('Error loading forecast:', error);
        const widget = document.getElementById('forecast-widget');
        if (widget) {
            widget.innerHTML = '<div class="error">Failed to load forecast data</div>';
        }
    }
}

