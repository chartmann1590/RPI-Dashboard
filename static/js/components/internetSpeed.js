// Internet Speed Component
export async function loadInternetSpeed() {
    try {
        const response = await fetch('/api/internet-speed');
        const speed = await response.json();
        
        const widget = document.getElementById('speed-widget');
        if (!widget) return;
        
        if (speed) {
            widget.innerHTML = `
                <div style="text-align: center;">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem;">
                        <div>
                            <div style="font-size: 0.9rem; color: #666;">Download</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: #667eea;">${speed.download_mbps} Mbps</div>
                        </div>
                        <div>
                            <div style="font-size: 0.9rem; color: #666;">Upload</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: #667eea;">${speed.upload_mbps} Mbps</div>
                        </div>
                        <div>
                            <div style="font-size: 0.9rem; color: #666;">Ping</div>
                            <div style="font-size: 1.5rem; font-weight: bold; color: #667eea;">${speed.ping_ms} ms</div>
                        </div>
                    </div>
                    <div style="font-size: 0.8rem; color: #999;">Last test: ${speed.last_test}</div>
                </div>
            `;
        } else {
            widget.innerHTML = '<div style="text-align: center; color: #666; padding: 2rem;">No speed test data. Click "Run Speed Test" to start.</div>';
        }
    } catch (error) {
        console.error('Error loading speed:', error);
        const widget = document.getElementById('speed-widget');
        if (widget) {
            widget.innerHTML = '<div class="error">Failed to load speed data</div>';
        }
    }
}

export function setupSpeedTestButton() {
    const btn = document.getElementById('run-speed-test');
    if (!btn) return;
    
    if (btn.hasAttribute('data-listener-added')) return;
    btn.setAttribute('data-listener-added', 'true');
    
    btn.addEventListener('click', async () => {
        btn.disabled = true;
        btn.textContent = 'Running...';
        
        try {
            const response = await fetch('/api/internet-speed/run', { method: 'POST' });
            if (response.ok) {
                setTimeout(() => {
                    loadInternetSpeed();
                    btn.disabled = false;
                    btn.textContent = 'Run Speed Test';
                }, 30000); // Wait 30 seconds for test to complete
            }
        } catch (error) {
            console.error('Error starting speed test:', error);
            btn.disabled = false;
            btn.textContent = 'Run Speed Test';
        }
    });
}

