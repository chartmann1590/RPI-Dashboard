// Commute Component
let commuteMap = null;

export async function loadCommuteInfo() {
    try {
        const response = await fetch('/api/commute-info');
        const commute = await response.json();
        
        const widget = document.getElementById('commute-widget');
        const mapDiv = document.getElementById('commute-map');
        
        if (!widget) return;
        
        if (commute) {
            let trafficNotices = '';
            if (commute.traffic_events && commute.traffic_events.length > 0) {
                trafficNotices = '<div style="margin-top: 0.5rem; padding: 0.5rem; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px; max-height: 150px; overflow-y: auto; overflow-x: hidden;">';
                commute.traffic_events.forEach(event => {
                    const levelColor = event.traffic_level === 'heavy' ? '#f44336' : event.traffic_level === 'medium' ? '#ffc107' : '#4caf50';
                    const levelText = event.traffic_level.charAt(0).toUpperCase() + event.traffic_level.slice(1);
                    const eventIcon = event.type === 'crash' ? '🚨' : '⚠️';
                    trafficNotices += `<div style="margin-bottom: 0.4rem; font-size: 0.85rem; line-height: 1.3;">
                        ${eventIcon} <strong style="color: ${levelColor};">${levelText} Traffic</strong> at ${event.location} - ${event.description} (${event.time})
                    </div>`;
                });
                trafficNotices += '</div>';
            } else {
                trafficNotices = '<div style="margin-top: 0.5rem; padding: 0.5rem; background: #d4edda; border-left: 4px solid #4caf50; border-radius: 4px; text-align: center;">';
                trafficNotices += '<div style="font-size: 0.85rem; color: #155724;"><strong style="color: #4caf50;">✓ Light Traffic</strong> - No traffic issues detected</div>';
                trafficNotices += '</div>';
            }
            
            widget.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 2rem; font-weight: bold; color: #667eea; margin-bottom: 0.5rem;">${commute.duration_formatted}</div>
                    <div style="color: #666; margin-bottom: 0.5rem;">${commute.distance_miles} miles</div>
                    <div style="font-size: 0.9rem; color: #999;">${commute.origin} → ${commute.destination}</div>
                    <div style="font-size: 0.8rem; color: #999; margin-top: 0.5rem;">Updated: ${commute.updated}</div>
                </div>
                <div style="margin-top: 0.5rem; text-align: center; font-size: 0.75rem; color: #999;">
                    <span style="color: #4caf50;">●</span> Light Traffic &nbsp;
                    <span style="color: #ffc107;">●</span> Medium Traffic &nbsp;
                    <span style="color: #f44336;">●</span> Heavy Traffic
                </div>
                ${trafficNotices}
            `;
            
            loadTrafficHistory();
            
            if (commute.route_coordinates && commute.route_coordinates.length > 0 && mapDiv) {
                if (commuteMap) {
                    commuteMap.remove();
                    commuteMap = null;
                }
                
                mapDiv.style.display = 'block';
                
                setTimeout(() => {
                    try {
                        if (typeof L === 'undefined') {
                            console.warn('Leaflet not loaded, skipping map render');
                            return;
                        }
                        
                        const latLngs = commute.route_coordinates.map(coord => [coord[1], coord[0]]);
                        const bounds = L.latLngBounds(latLngs);
                        
                        commuteMap = L.map('commute-map', {
                            zoomControl: true,
                            preferCanvas: false
                        });
                        
                        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                            attribution: '© OpenStreetMap contributors',
                            maxZoom: 19
                        }).addTo(commuteMap);
                        
                        L.marker([commute.origin_lat, commute.origin_lon])
                            .addTo(commuteMap)
                            .bindPopup(`Origin: ${commute.origin}`);
                        
                        L.marker([commute.dest_lat, commute.dest_lon])
                            .addTo(commuteMap)
                            .bindPopup(`Destination: ${commute.destination}`);
                        
                        if (commute.route_segments && commute.route_segments.length > 0) {
                            commute.route_segments.forEach(segment => {
                                if (segment.coordinates && segment.coordinates.length > 0) {
                                    let color = '#4caf50';
                                    if (segment.traffic_level === 'medium') {
                                        color = '#ffc107';
                                    } else if (segment.traffic_level === 'heavy') {
                                        color = '#f44336';
                                    }
                                    
                                    const segmentLatLngs = segment.coordinates.map(coord => [coord[1], coord[0]]);
                                    
                                    L.polyline(segmentLatLngs, {
                                        color: color,
                                        weight: 6,
                                        opacity: 0.9
                                    }).addTo(commuteMap);
                                }
                            });
                        } else {
                            const numSegments = Math.max(1, Math.floor(latLngs.length / 10));
                            const segmentSize = Math.floor(latLngs.length / numSegments);
                            for (let i = 0; i < latLngs.length; i += segmentSize) {
                                const segment = latLngs.slice(i, i + segmentSize);
                                if (segment.length > 1) {
                                    L.polyline(segment, {
                                        color: '#4caf50',
                                        weight: 6,
                                        opacity: 0.9
                                    }).addTo(commuteMap);
                                }
                            }
                        }
                        
                        commuteMap.fitBounds(bounds, {
                            padding: [30, 30],
                            maxZoom: 15
                        });
                    } catch (error) {
                        console.error('Error rendering commute map:', error);
                        if (mapDiv) mapDiv.style.display = 'none';
                    }
                }, 200);
            } else if (mapDiv) {
                mapDiv.style.display = 'none';
            }
        } else {
            widget.innerHTML = '<div style="text-align: center; color: #666; padding: 2rem;">Configure commute route above</div>';
            if (mapDiv) mapDiv.style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading commute info:', error);
        const widget = document.getElementById('commute-widget');
        if (widget) {
            widget.innerHTML = '<div class="error">Failed to load commute info</div>';
        }
        const mapDiv = document.getElementById('commute-map');
        if (mapDiv) mapDiv.style.display = 'none';
    }
}

export async function loadTrafficHistory() {
    try {
        const response = await fetch('/api/traffic-history');
        const data = await response.json();
        
        const historyDiv = document.getElementById('traffic-history');
        const historyList = document.getElementById('traffic-history-list');
        
        if (!historyDiv || !historyList) return;
        
        if (data.events && data.events.length > 0) {
            historyDiv.style.display = 'block';
            historyList.innerHTML = data.events.map(event => {
                const levelColor = event.traffic_level === 'heavy' ? '#f44336' : event.traffic_level === 'medium' ? '#ffc107' : '#4caf50';
                const levelText = event.traffic_level.charAt(0).toUpperCase() + event.traffic_level.slice(1);
                const eventIcon = event.type === 'crash' ? '🚨' : event.type === 'heavy_traffic' ? '⚠️' : '📊';
                return `
                    <div style="padding: 0.75rem; border-bottom: 1px solid #eee; transition: background-color 0.3s ease;" onmouseover="this.style.backgroundColor='#f8f9fa'" onmouseout="this.style.backgroundColor='transparent'">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.3rem;">
                            <div>
                                <strong style="color: ${levelColor};">${eventIcon} ${levelText} Traffic</strong>
                                ${event.type === 'crash' ? '<span style="color: #f44336; font-weight: bold;"> - CRASH DETECTED</span>' : ''}
                            </div>
                            <div style="font-size: 0.85rem; color: #666;">${event.date} ${event.time}</div>
                        </div>
                        <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.3rem;">${event.location}</div>
                        <div style="font-size: 0.85rem; color: #999;">${event.description}</div>
                    </div>
                `;
            }).join('');
        } else {
            historyDiv.style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading traffic history:', error);
    }
}

export function setupCommuteForm() {
    const form = document.getElementById('commute-form');
    if (!form) return;
    
    if (form.hasAttribute('data-listener-added')) return;
    form.setAttribute('data-listener-added', 'true');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const origin = document.getElementById('commute-origin').value;
        const destination = document.getElementById('commute-destination').value;
        
        try {
            const response = await fetch('/api/settings/commute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ origin, destination })
            });
            if (response.ok) {
                loadCommuteInfo();
            }
        } catch (error) {
            console.error('Error saving commute:', error);
            alert('Error saving commute settings');
        }
    });
}

