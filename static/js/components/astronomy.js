// Astronomy Component
export async function loadAstronomy() {
    try {
        const response = await fetch('/api/astronomy');
        const astro = await response.json();
        
        const widget = document.getElementById('astronomy-widget');
        if (!widget) return;
        
        if (astro) {
            widget.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 4rem; margin-bottom: 0.5rem;">${astro.moon_icon}</div>
                    <div style="font-size: 1.2rem; font-weight: bold; margin-bottom: 1rem;">${astro.moon_phase_name}</div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                        <div>
                            <div style="font-size: 0.9rem; color: #666;">Sunrise</div>
                            <div style="font-size: 1.2rem; font-weight: bold;">${astro.sunrise}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.9rem; color: #666;">Sunset</div>
                            <div style="font-size: 1.2rem; font-weight: bold;">${astro.sunset}</div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            widget.innerHTML = '<div class="error">Astronomy data unavailable</div>';
        }
    } catch (error) {
        console.error('Error loading astronomy:', error);
        const widget = document.getElementById('astronomy-widget');
        if (widget) {
            widget.innerHTML = '<div class="error">Failed to load astronomy data</div>';
        }
    }
}

