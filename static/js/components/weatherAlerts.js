// Weather Alerts Component
export async function loadWeatherAlerts() {
    try {
        const response = await fetch('/api/dashboard-data');
        const data = await response.json();
        
        const widget = document.getElementById('weather-alerts-widget');
        if (!widget) return;
        
        if (data.weather_alerts && data.weather_alerts.length > 0) {
            widget.innerHTML = '<div class="news-list">' + 
                data.weather_alerts.map(alert => {
                    const severityColor = alert.severity === 'Extreme' ? '#f44336' : 
                                         alert.severity === 'Severe' ? '#ff9800' : 
                                         alert.severity === 'Moderate' ? '#ffc107' : '#2196F3';
                    return `
                        <div class="news-item" style="border-left: 4px solid ${severityColor};">
                            <div class="news-source" style="color: ${severityColor};">${alert.severity} - ${alert.type}</div>
                            <div class="news-title">${alert.headline || 'Weather Alert'}</div>
                            <div class="news-desc">${alert.area || ''}</div>
                            <div class="news-desc" style="margin-top: 0.5rem;">${alert.description.substring(0, 300)}${alert.description.length > 300 ? '...' : ''}</div>
                        </div>
                    `;
                }).join('') + '</div>';
        } else {
            widget.innerHTML = '<div style="text-align: center; color: #666; padding: 2rem;">No weather alerts</div>';
        }
    } catch (error) {
        console.error('Error loading weather alerts:', error);
        const widget = document.getElementById('weather-alerts-widget');
        if (widget) {
            widget.innerHTML = '<div class="error">Failed to load weather alerts</div>';
        }
    }
}

