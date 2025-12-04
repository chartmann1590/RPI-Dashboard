// SwitchBot Locks Component
export async function loadSwitchbotLocks() {
    const widget = document.getElementById('switchbot-locks-widget');
    if (!widget) {
        console.warn('SwitchBot locks widget not found');
        return;
    }
    
    try {
        widget.innerHTML = '<div class="loading">Loading lock status...</div>';
        
        const response = await fetch('/api/switchbot-locks');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const locks = await response.json();
        
        if (!locks || locks.length === 0) {
            widget.innerHTML = '<div class="error">No locks configured</div>';
            return;
        }
        
        let html = '<div class="locks-list">';
        locks.forEach(lock => {
            const statusClass = lock.status === 'locked' ? 'locked' : 
                               lock.status === 'unlocked' ? 'unlocked' : 'unknown';
            const statusIcon = lock.status === 'locked' ? '🔒' : 
                              lock.status === 'unlocked' ? '🔓' : '❓';
            const statusText = lock.status.charAt(0).toUpperCase() + lock.status.slice(1);
            
            html += `
                <div class="lock-item" style="display: flex; align-items: center; justify-content: space-between; padding: 0.75rem; margin-bottom: 0.5rem; background: #f5f5f5; border-radius: 5px;">
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <span style="font-size: 1.5rem;">${statusIcon}</span>
                        <div>
                            <div style="font-weight: 600; color: #333;">${lock.name}</div>
                            <div style="font-size: 0.85rem; color: #666;">${lock.device_id}</div>
                        </div>
                    </div>
                    <div>
                        <span class="status-indicator status-${statusClass}" style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 0.5rem; background-color: ${lock.status === 'locked' ? '#28a745' : lock.status === 'unlocked' ? '#dc3545' : '#6c757d'};"></span>
                        <span style="font-weight: 500; color: ${lock.status === 'locked' ? '#28a745' : lock.status === 'unlocked' ? '#dc3545' : '#6c757d'};">${statusText}</span>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        
        widget.innerHTML = html;
    } catch (error) {
        console.error('Error loading SwitchBot locks:', error);
        widget.innerHTML = '<div class="error">Error loading lock status. Please try again later.</div>';
    }
}

