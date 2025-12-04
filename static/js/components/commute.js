// Commute Component - Real-time Traffic Display
let commuteMap = null;

// Traffic level colors - NEVER blue
const TRAFFIC_COLORS = {
    light: '#4caf50',   // Green
    medium: '#ffc107',  // Yellow/Amber
    heavy: '#f44336'    // Red
};

export async function loadCommuteInfo(forceRefresh = false) {
    try {
        // Request fresh data - use refresh=true to bypass backend cache
        const url = forceRefresh 
            ? '/api/commute-info?refresh=true&t=' + Date.now()
            : '/api/commute-info?t=' + Date.now();
        const response = await fetch(url);
        const commute = await response.json();
        
        // Debug: Log the full response to see what we're getting
        console.log('Commute API response:', commute);
        console.log('Traffic events:', commute?.traffic_events);
        console.log('Route segments:', commute?.route_segments);
        
        const widget = document.getElementById('commute-widget');
        const mapDiv = document.getElementById('commute-map');
        
        if (!widget) return;
        
        // Handle error responses
        if (commute && commute.error) {
            widget.innerHTML = `<div style="text-align: center; color: #d32f2f; padding: 1rem;">
                <div style="font-weight: bold; margin-bottom: 0.5rem;">⚠️ ${commute.error}</div>
                <div style="font-size: 0.9rem; color: #666;">Please check your addresses above and try again.</div>
            </div>`;
            if (mapDiv) mapDiv.style.display = 'none';
            return;
        }
        
        if (commute && !commute.error) {
            // Calculate overall traffic condition ONLY from route segments (actual traffic flow on YOUR route)
            // Incidents are shown for awareness but don't affect the overall status
            let overallTraffic = 'light';
            let heavyCount = 0, mediumCount = 0, lightCount = 0;
            
            // Check route segments for traffic levels - this is the ACTUAL traffic on your route
            if (commute.route_segments && commute.route_segments.length > 0) {
                commute.route_segments.forEach(seg => {
                    if (seg.traffic_level === 'heavy') heavyCount++;
                    else if (seg.traffic_level === 'medium') mediumCount++;
                    else lightCount++;
                });
                
                const totalSegments = heavyCount + mediumCount + lightCount;
                // Only mark as heavy if significant portion of route has heavy traffic
                if (heavyCount / totalSegments > 0.2) overallTraffic = 'heavy';
                else if ((heavyCount + mediumCount) / totalSegments > 0.3) overallTraffic = 'medium';
            }
            
            // Get traffic events (shown for awareness, but don't affect overall status)
            const trafficEvents = commute.traffic_events || [];
            
            console.log('Route traffic level:', overallTraffic, '| Segments:', heavyCount, 'heavy,', mediumCount, 'medium,', lightCount, 'light | Nearby incidents:', trafficEvents.length);
            
            // Build traffic notices - match RPi dashboard style
            // Always show overall traffic status first (based on actual route traffic flow)
            const statusColor = TRAFFIC_COLORS[overallTraffic];
            const statusText = overallTraffic === 'heavy' ? 'Heavy Traffic on Route' : 
                               overallTraffic === 'medium' ? 'Moderate Traffic on Route' : 'Route is Clear';
            const statusIcon = overallTraffic === 'heavy' ? '🚨' : 
                              overallTraffic === 'medium' ? '⚠️' : '✓';
            const statusBgColor = overallTraffic === 'heavy' ? 'rgba(244, 67, 54, 0.15)' : 
                                 overallTraffic === 'medium' ? 'rgba(255, 193, 7, 0.15)' : 'rgba(76, 175, 80, 0.15)';
            
            // Subtext changes based on whether there are nearby incidents
            let statusSubtext = '';
            if (overallTraffic === 'light') {
                statusSubtext = trafficEvents.length > 0 
                    ? 'Your route is clear - incidents shown below are nearby'
                    : 'No traffic issues on your route';
            } else if (overallTraffic === 'medium') {
                statusSubtext = 'Some slowdowns on your route';
            } else {
                statusSubtext = 'Significant delays on your route';
            }
            
            let trafficNotices = `
                <div style="margin-top: 0.5rem; padding: 0.6rem; background: ${statusBgColor}; border-left: 4px solid ${statusColor}; border-radius: 4px; text-align: center; margin-bottom: 0.5rem;">
                    <div style="font-size: 1rem; font-weight: bold; color: ${statusColor};">${statusIcon} ${statusText}</div>
                    <div style="font-size: 0.8rem; color: #666; margin-top: 0.2rem;">${statusSubtext}</div>
                </div>
            `;
            
            if (trafficEvents.length > 0) {
                console.log('Displaying', trafficEvents.length, 'traffic events');
                trafficNotices += '<div style="max-height: 180px; overflow-y: auto; overflow-x: hidden;">';
                trafficEvents.forEach(event => {
                    const levelColor = TRAFFIC_COLORS[event.traffic_level] || TRAFFIC_COLORS.light;
                    const levelText = (event.traffic_level || 'unknown').charAt(0).toUpperCase() + (event.traffic_level || 'unknown').slice(1);
                    
                    // Get icon based on incident type - same as map markers and RPi dashboard
                    let eventIcon = '⚠️';
                    let alertClass = 'alert-light';
                    switch (event.type) {
                        case 'crash':
                            eventIcon = '🚨';
                            alertClass = 'alert-crash';
                            break;
                        case 'closure':
                            eventIcon = '🚫';
                            alertClass = 'alert-heavy';
                            break;
                        case 'construction':
                            eventIcon = '🚧';
                            alertClass = 'alert-medium';
                            break;
                        case 'weather':
                            eventIcon = '🌧️';
                            alertClass = 'alert-medium';
                            break;
                        case 'incident':
                            eventIcon = '⚠️';
                            alertClass = event.traffic_level === 'heavy' ? 'alert-heavy' : 'alert-medium';
                            break;
                        case 'traffic':
                            eventIcon = '🚗';
                            alertClass = event.traffic_level === 'heavy' ? 'alert-heavy' : 'alert-medium';
                            break;
                        default:
                            eventIcon = event.traffic_level === 'heavy' ? '🚧' : '⚠️';
                            alertClass = event.traffic_level === 'heavy' ? 'alert-heavy' : 'alert-medium';
                    }
                    
                    // Background color based on severity
                    const bgColor = event.type === 'crash' || event.traffic_level === 'heavy' ? 'rgba(244, 67, 54, 0.1)' :
                                   event.traffic_level === 'medium' ? 'rgba(255, 193, 7, 0.1)' : 'rgba(76, 175, 80, 0.1)';
                    const borderColor = event.type === 'crash' || event.traffic_level === 'heavy' ? '#f44336' :
                                       event.traffic_level === 'medium' ? '#ffc107' : '#4caf50';
                    
                    const eventTitle = event.type ? event.type.charAt(0).toUpperCase() + event.type.slice(1) : 'Traffic';
                    
                    trafficNotices += `
                        <div style="margin-bottom: 0.5rem; padding: 0.6rem; background: ${bgColor}; border-left: 4px solid ${borderColor}; border-radius: 4px;">
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem;">
                                <span style="font-size: 1.1rem;">${eventIcon}</span>
                                <strong style="color: ${levelColor};">${eventTitle}${event.type === 'crash' ? ' - CRASH' : ''}</strong>
                                ${event.time ? `<span style="margin-left: auto; font-size: 0.75rem; color: #999;">${event.time}</span>` : ''}
                            </div>
                            ${event.location ? `<div style="font-size: 0.8rem; color: #666; margin-bottom: 0.2rem;">📍 ${event.location}</div>` : ''}
                            <div style="font-size: 0.85rem; color: #555;">${event.description || ''}</div>
                        </div>
                    `;
                });
                trafficNotices += '</div>';
            }
            // No else needed - overall status is always shown at top
            
            // Traffic delay info
            let delayInfo = '';
            if (commute.traffic_delay_min && commute.traffic_delay_min > 0) {
                delayInfo = `<div style="font-size: 0.85rem; color: #f44336; margin-top: 0.3rem;">+${commute.traffic_delay_min} min due to traffic</div>`;
            }
            
            // Traffic source badge
            const trafficSource = commute.traffic_source || 'Estimated';
            const isRealTime = trafficSource.includes('TomTom') || trafficSource.includes('Real-time');
            const sourceBadge = isRealTime 
                ? `<span style="background: #4caf50; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; margin-left: 0.5rem;">🔴 LIVE</span>`
                : `<span style="background: #999; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; margin-left: 0.5rem;">Estimated</span>`;
            
            // Duration color based on overall traffic
            const durationColor = overallTraffic === 'heavy' ? TRAFFIC_COLORS.heavy : 
                                 overallTraffic === 'medium' ? TRAFFIC_COLORS.medium : '#667eea';
            
            widget.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 2rem; font-weight: bold; color: ${durationColor}; margin-bottom: 0.5rem;">
                        ${commute.duration_formatted}${sourceBadge}
                    </div>
                    <div style="color: #666; margin-bottom: 0.5rem;">${commute.distance_miles} miles</div>
                    ${delayInfo}
                    <div style="font-size: 0.9rem; color: #999;">${commute.origin} → ${commute.destination}</div>
                    <div style="display: flex; justify-content: center; align-items: center; gap: 0.5rem; margin-top: 0.5rem;">
                        <span style="font-size: 0.8rem; color: #999;">Updated: ${commute.updated}</span>
                        <button onclick="window.refreshCommuteData()" style="background: none; border: none; cursor: pointer; font-size: 1rem; padding: 2px;" title="Refresh">🔄</button>
                    </div>
                </div>
                <div style="margin-top: 0.5rem; text-align: center; font-size: 0.75rem; color: #999; background: #f5f5f5; padding: 0.5rem; border-radius: 4px;">
                    <span style="display: inline-block; width: 12px; height: 12px; background: ${TRAFFIC_COLORS.light}; border-radius: 50%; margin-right: 3px;"></span> Light &nbsp;
                    <span style="display: inline-block; width: 12px; height: 12px; background: ${TRAFFIC_COLORS.medium}; border-radius: 50%; margin-right: 3px;"></span> Medium &nbsp;
                    <span style="display: inline-block; width: 12px; height: 12px; background: ${TRAFFIC_COLORS.heavy}; border-radius: 50%; margin-right: 3px;"></span> Heavy
                </div>
                ${trafficNotices}
            `;
            
            // Expose refresh function globally for the button
            window.refreshCommuteData = () => {
                loadCommuteInfo(true);
            };
            
            loadTrafficHistory();
            
            // Render the map with traffic-colored segments
            if (commute.route_coordinates && commute.route_coordinates.length > 0 && mapDiv) {
                renderCommuteMap(commute, mapDiv);
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

function renderCommuteMap(commute, mapDiv) {
    // Clean up existing map
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
            
            // Origin marker with always-visible tooltip (matches RPi dashboard)
            L.marker([commute.origin_lat, commute.origin_lon])
                .addTo(commuteMap)
                .bindTooltip(`<strong>📍 Start</strong><br>${commute.origin}`, {
                    permanent: true,
                    direction: 'top',
                    className: 'marker-tooltip marker-tooltip-start',
                    offset: [0, -10]
                })
                .openTooltip();
            
            // Destination marker with always-visible tooltip (matches RPi dashboard)
            L.marker([commute.dest_lat, commute.dest_lon])
                .addTo(commuteMap)
                .bindTooltip(`<strong>🏁 Finish</strong><br>${commute.destination}`, {
                    permanent: true,
                    direction: 'top',
                    className: 'marker-tooltip marker-tooltip-finish',
                    offset: [0, -10]
                })
                .openTooltip();
            
            // Draw route with traffic-colored segments
            if (commute.route_segments && commute.route_segments.length > 0) {
                console.log(`Rendering ${commute.route_segments.length} traffic segments`);
                
                commute.route_segments.forEach((segment, idx) => {
                    if (segment.coordinates && segment.coordinates.length > 1) {
                        // Get traffic color - NEVER use blue
                        const color = TRAFFIC_COLORS[segment.traffic_level] || TRAFFIC_COLORS.light;
                        
                        const segmentLatLngs = segment.coordinates.map(coord => [coord[1], coord[0]]);
                        
                        // Draw with traffic color
                        const polyline = L.polyline(segmentLatLngs, {
                            color: color,
                            weight: 7,
                            opacity: 0.9,
                            lineCap: 'round',
                            lineJoin: 'round'
                        }).addTo(commuteMap);
                        
                        // Add popup with traffic info
                        const levelText = (segment.traffic_level || 'light').charAt(0).toUpperCase() + (segment.traffic_level || 'light').slice(1);
                        polyline.bindPopup(`<strong style="color: ${color};">${levelText} Traffic</strong>`);
                        
                        console.log(`Segment ${idx + 1}: ${segment.traffic_level} (${color}), ${segment.coordinates.length} points`);
                    }
                });
            } else {
                // Fallback: render entire route as green (light traffic)
                console.log('No segments, rendering full route as light traffic');
                L.polyline(latLngs, {
                    color: TRAFFIC_COLORS.light,
                    weight: 7,
                    opacity: 0.9,
                    lineCap: 'round',
                    lineJoin: 'round'
                }).addTo(commuteMap);
            }
            
            // Add traffic incident markers with type-specific icons
            if (commute.traffic_events && commute.traffic_events.length > 0) {
                console.log(`Rendering ${commute.traffic_events.length} traffic incidents`);
                
                commute.traffic_events.forEach(event => {
                    if (event.lat && event.lon) {
                        const eventColor = TRAFFIC_COLORS[event.traffic_level] || TRAFFIC_COLORS.medium;
                        
                        // Get icon based on incident type
                        let emoji = '⚠️';
                        let pulseAnimation = '';
                        
                        switch (event.type) {
                            case 'crash':
                                emoji = '🚨';
                                pulseAnimation = 'animation: pulse 1.5s infinite;';
                                break;
                            case 'closure':
                                emoji = '🚫';
                                pulseAnimation = 'animation: pulse 2s infinite;';
                                break;
                            case 'construction':
                                emoji = '🚧';
                                break;
                            case 'weather':
                                emoji = '🌧️';
                                break;
                            case 'incident':
                                emoji = '⚠️';
                                break;
                            case 'traffic':
                                emoji = '🚗';
                                break;
                            default:
                                emoji = '⚠️';
                        }
                        
                        const markerSize = event.type === 'crash' || event.type === 'closure' ? 28 : 24;
                        
                        const eventIcon = L.divIcon({
                            className: 'traffic-incident-marker',
                            html: `<div style="background-color: ${eventColor}; width: ${markerSize}px; height: ${markerSize}px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; font-size: ${markerSize * 0.5}px; ${pulseAnimation}">${emoji}</div>`,
                            iconSize: [markerSize, markerSize],
                            iconAnchor: [markerSize / 2, markerSize / 2]
                        });
                        
                        const popupContent = `
                            <div style="min-width: 150px;">
                                <strong style="color: ${eventColor}; font-size: 14px;">${emoji} ${event.type ? event.type.toUpperCase() : 'INCIDENT'}</strong><br>
                                <span style="font-size: 12px;">${event.description || ''}</span><br>
                                ${event.location ? `<small style="color: #666;">📍 ${event.location}</small><br>` : ''}
                                ${event.time ? `<small style="color: #999;">${event.time}</small>` : ''}
                            </div>
                        `;
                        
                        L.marker([event.lat, event.lon], { icon: eventIcon })
                            .addTo(commuteMap)
                            .bindPopup(popupContent);
                        
                        console.log(`Incident marker: ${event.type} at ${event.lat}, ${event.lon}`);
                    }
                });
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

