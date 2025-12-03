// Air Quality Component
export async function loadAirQuality() {
    try {
        const response = await fetch('/api/air-quality');
        const aq = await response.json();
        
        const widget = document.getElementById('air-quality-widget');
        if (!widget) return;
        
        if (aq) {
            widget.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 3rem; font-weight: bold; color: ${aq.color}; margin-bottom: 0.5rem;">${aq.aqi}</div>
                    <div style="font-size: 1.2rem; margin-bottom: 1rem;">${aq.level}</div>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; font-size: 0.9rem;">
                        <div>PM2.5: ${aq.pm25} µg/m³</div>
                        <div>PM10: ${aq.pm10} µg/m³</div>
                        <div>NO₂: ${aq.no2} µg/m³</div>
                        <div>O₃: ${aq.o3} µg/m³</div>
                    </div>
                    <div style="font-size: 0.8rem; color: #999; margin-top: 0.5rem;">Updated: ${aq.updated}</div>
                </div>
            `;
        } else {
            widget.innerHTML = '<div class="error">Air quality data unavailable</div>';
        }
    } catch (error) {
        console.error('Error loading air quality:', error);
        const widget = document.getElementById('air-quality-widget');
        if (widget) {
            widget.innerHTML = '<div class="error">Failed to load air quality</div>';
        }
    }
}

