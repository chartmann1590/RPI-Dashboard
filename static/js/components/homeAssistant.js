// Home Assistant Component
const domainIcons = {
    'light': '💡',
    'switch': '🔌',
    'binary_sensor': '📡',
    'fan': '🌀',
    'climate': '🌡️',
    'media_player': '📺',
    'cover': '🪟',
    'lock': '🔐',
    'sensor': '📊',
    'other': '⚙️'
};

export async function loadHomeAssistant() {
    try {
        const response = await fetch('/api/home-assistant');
        const data = await response.json();
        
        const widget = document.getElementById('ha-widget');
        if (!widget) return;
        
        if (data.error) {
            widget.innerHTML = `<div class="error">Error loading Home Assistant data: ${data.error}</div>`;
            return;
        }
        
        let html = '';
        
        // Group devices by domain
        const devicesByDomain = {};
        let totalDevices = 0;
        let devicesOn = 0;
        
        if (data.devices && data.devices.length > 0) {
            data.devices.forEach(device => {
                const entityId = device.entity_id || '';
                const domain = entityId.split('.')[0] || 'other';
                if (!devicesByDomain[domain]) {
                    devicesByDomain[domain] = [];
                }
                devicesByDomain[domain].push(device);
                totalDevices++;
                if (device.state?.toLowerCase() === 'on') devicesOn++;
            });
        }
        
        // Count battery sensors
        const batteryCount = data.battery_sensors?.length || 0;
        const lowBatteryCount = data.battery_sensors?.filter(s => s.battery_level < 25).length || 0;
        
        // Stats bar
        if (totalDevices > 0 || batteryCount > 0) {
            html += `
                <div class="ha-stats-bar">
                    <div class="ha-stat-item">
                        <div class="ha-stat-value">${totalDevices}</div>
                        <div class="ha-stat-label">Total Devices</div>
                    </div>
                    <div class="ha-stat-divider"></div>
                    <div class="ha-stat-item">
                        <div class="ha-stat-value">${devicesOn}</div>
                        <div class="ha-stat-label">Currently On</div>
                    </div>
                    <div class="ha-stat-divider"></div>
                    <div class="ha-stat-item">
                        <div class="ha-stat-value">${batteryCount}</div>
                        <div class="ha-stat-label">Battery Sensors</div>
                    </div>
                    ${lowBatteryCount > 0 ? `
                        <div class="ha-stat-divider"></div>
                        <div class="ha-stat-item">
                            <div class="ha-stat-value" style="color: #ffcdd2;">${lowBatteryCount}</div>
                            <div class="ha-stat-label">Low Battery</div>
                        </div>
                    ` : ''}
                </div>
            `;
        }
        
        // Display devices grouped by domain
        if (Object.keys(devicesByDomain).length > 0) {
            html += '<div class="ha-section">';
            html += `
                <div class="ha-section-header">
                    <div class="ha-section-icon">⚡</div>
                    <h3 class="ha-section-title">Devices</h3>
                    <span class="ha-section-count">${totalDevices} devices</span>
                </div>
            `;
            
            // Sort domains with priority for common ones
            const domainOrder = ['switch', 'light', 'fan', 'climate', 'media_player', 'cover', 'lock', 'binary_sensor'];
            const sortedDomains = Object.keys(devicesByDomain).sort((a, b) => {
                const aIndex = domainOrder.indexOf(a);
                const bIndex = domainOrder.indexOf(b);
                if (aIndex === -1 && bIndex === -1) return a.localeCompare(b);
                if (aIndex === -1) return 1;
                if (bIndex === -1) return -1;
                return aIndex - bIndex;
            });
            
            sortedDomains.forEach(domain => {
                const domainDevices = devicesByDomain[domain];
                const icon = domainIcons[domain] || domainIcons['other'];
                
                html += `<div class="ha-domain-group">`;
                html += `<div class="ha-domain-header">
                    <span class="ha-domain-icon">${icon}</span>
                    <span>${domain.replace('_', ' ')}</span>
                </div>`;
                html += '<div class="ha-devices-grid">';
                
                domainDevices.forEach(device => {
                    const friendlyName = device.attributes?.friendly_name || device.entity_id;
                    const state = device.state || 'unknown';
                    const isOn = state.toLowerCase() === 'on';
                    
                    html += `
                        <div class="ha-device-card ${isOn ? 'device-on' : ''}">
                            <div class="ha-device-icon">${icon}</div>
                            <div class="ha-device-info">
                                <div class="ha-device-name">${friendlyName}</div>
                                <div class="ha-device-entity">${device.entity_id}</div>
                            </div>
                            <div class="ha-device-status">
                                <span class="ha-status-indicator ${isOn ? 'status-on' : ''}"></span>
                                <span class="ha-status-text ${isOn ? 'status-on' : 'status-off'}">${state}</span>
                            </div>
                        </div>
                    `;
                });
                
                html += '</div></div>';
            });
            
            html += '</div>';
        } else {
            html += `
                <div class="ha-empty-state">
                    <div class="ha-empty-state-icon">🏠</div>
                    <div class="ha-empty-state-text">No devices found</div>
                </div>
            `;
        }
        
        // Display battery sensors
        if (data.battery_sensors && data.battery_sensors.length > 0) {
            html += '<div class="ha-section">';
            html += `
                <div class="ha-section-header">
                    <div class="ha-section-icon">🔋</div>
                    <h3 class="ha-section-title">Battery Sensors</h3>
                    <span class="ha-section-count">${batteryCount} sensors</span>
                </div>
            `;
            html += '<div class="ha-battery-grid">';
            
            // Sort by battery level (lowest first)
            const sortedBatteries = [...data.battery_sensors].sort((a, b) => 
                (a.battery_level || 0) - (b.battery_level || 0)
            );
            
            sortedBatteries.forEach(sensor => {
                const friendlyName = sensor.attributes?.friendly_name || sensor.entity_id;
                const batteryLevel = sensor.battery_level || 0;
                const levelClass = batteryLevel < 25 ? 'level-low' : batteryLevel < 50 ? 'level-medium' : 'level-high';
                const cardClass = batteryLevel < 25 ? 'battery-low' : batteryLevel < 50 ? 'battery-medium' : '';
                
                html += `
                    <div class="ha-battery-card ${cardClass}">
                        <div class="ha-battery-header">
                            <div class="ha-battery-name">${friendlyName}</div>
                            <div class="ha-battery-percent ${levelClass}">${batteryLevel}%</div>
                        </div>
                        <div class="ha-battery-bar-container">
                            <div class="ha-battery-bar ${levelClass}" style="width: ${batteryLevel}%;"></div>
                        </div>
                        <div class="ha-battery-entity">${sensor.entity_id}</div>
                    </div>
                `;
            });
            
            html += '</div></div>';
        }
        
        if (html === '') {
            html = `
                <div class="ha-empty-state">
                    <div class="ha-empty-state-icon">🏠</div>
                    <div class="ha-empty-state-text">No Home Assistant data available.<br>Check your configuration.</div>
                </div>
            `;
        }
        
        widget.innerHTML = html;
    } catch (error) {
        console.error('Error loading Home Assistant data:', error);
        const widget = document.getElementById('ha-widget');
        if (widget) {
            widget.innerHTML = `
                <div class="ha-empty-state">
                    <div class="ha-empty-state-icon">❌</div>
                    <div class="ha-empty-state-text">Failed to load Home Assistant data</div>
                </div>
            `;
        }
    }
}

