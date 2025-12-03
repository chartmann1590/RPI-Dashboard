// Calendar Component
export async function loadCalendarEvents() {
    try {
        const response = await fetch('/api/calendar-events');
        const events = await response.json();
        
        const widget = document.getElementById('calendar-widget');
        if (!widget) return;
        
        if (events && events.length > 0) {
            widget.innerHTML = '<div class="news-list">' + 
                events.slice(0, 5).map(event => `
                    <div class="news-item">
                        <div class="news-source">${event.source}</div>
                        <div class="news-title">${event.title}</div>
                        <div class="news-desc">${event.date} at ${event.time}${event.location ? ' • ' + event.location : ''}</div>
                    </div>
                `).join('') + '</div>';
        } else {
            widget.innerHTML = '<div style="text-align: center; color: #666; padding: 2rem;">No upcoming events</div>';
        }
    } catch (error) {
        console.error('Error loading calendar events:', error);
        const widget = document.getElementById('calendar-widget');
        if (widget) {
            widget.innerHTML = '<div class="error">Failed to load calendar events</div>';
        }
    }
}

export async function loadCalendarFeeds() {
    try {
        const response = await fetch('/api/calendar-feeds');
        const feeds = await response.json();
        
        const list = document.getElementById('feeds-list');
        if (!list) return;
        
        if (feeds && feeds.length > 0) {
            list.innerHTML = '<h4 style="margin-bottom: 0.5rem;">Existing Feeds:</h4>' +
                feeds.map(feed => `
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: #f8f9fa; border-radius: 5px; margin-bottom: 0.5rem;">
                        <span><strong>${feed.name || 'Unnamed'}</strong>: ${feed.url.substring(0, 50)}...</span>
                        <button onclick="deleteFeed(${feed.id})" class="btn btn-secondary" style="padding: 0.25rem 0.75rem; font-size: 0.9rem;">Delete</button>
                    </div>
                `).join('');
        } else {
            list.innerHTML = '<p style="color: #666;">No calendar feeds added yet.</p>';
        }
    } catch (error) {
        console.error('Error loading feeds:', error);
    }
}

export async function deleteFeed(feedId) {
    if (!confirm('Delete this calendar feed?')) return;
    try {
        const response = await fetch(`/api/calendar-feeds/${feedId}`, { method: 'DELETE' });
        if (response.ok) {
            loadCalendarFeeds();
            loadCalendarEvents();
        }
    } catch (error) {
        console.error('Error deleting feed:', error);
        alert('Error deleting feed');
    }
}

export async function loadLocalEvents() {
    try {
        const response = await fetch('/api/calendar-events/local');
        const events = await response.json();
        
        const list = document.getElementById('local-events-list');
        if (!list) return;
        
        if (events && events.length > 0) {
            list.innerHTML = events.map(event => `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; background: #f8f9fa; border-radius: 5px; margin-bottom: 0.5rem;">
                    <div>
                        <strong>${event.title}</strong><br>
                        <small style="color: #666;">${event.start_time}${event.location ? ' • ' + event.location : ''}</small>
                    </div>
                    <div>
                        <button onclick="editEvent(${event.id})" class="btn btn-secondary" style="padding: 0.25rem 0.75rem; font-size: 0.9rem; margin-right: 0.5rem;">Edit</button>
                        <button onclick="deleteEvent(${event.id})" class="btn btn-secondary" style="padding: 0.25rem 0.75rem; font-size: 0.9rem;">Delete</button>
                    </div>
                </div>
            `).join('');
        } else {
            list.innerHTML = '<p style="color: #666;">No local events added yet.</p>';
        }
    } catch (error) {
        console.error('Error loading local events:', error);
    }
}

export async function deleteEvent(eventId) {
    if (!confirm('Delete this event?')) return;
    try {
        const response = await fetch(`/api/calendar-events/local/${eventId}`, { method: 'DELETE' });
        if (response.ok) {
            loadLocalEvents();
            loadCalendarEvents();
        }
    } catch (error) {
        console.error('Error deleting event:', error);
        alert('Error deleting event');
    }
}

export function editEvent(eventId) {
    // Simple edit - reload and populate form
    loadLocalEvents();
    alert('Edit functionality - populate form with event data');
}

// Make functions available globally for onclick handlers
window.deleteFeed = deleteFeed;
window.deleteEvent = deleteEvent;
window.editEvent = editEvent;

