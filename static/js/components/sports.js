// Sports Component
export async function loadSportsTeams() {
    try {
        const response = await fetch('/api/settings/sports');
        const data = await response.json();
        const teams = data.teams || [];
        
        const teamsList = document.getElementById('sports-teams-list');
        if (!teamsList) return;
        
        if (teams.length > 0) {
            teamsList.innerHTML = '';
            teams.forEach(team => {
                // Handle both old format (string) and new format (object)
                const teamName = typeof team === 'string' ? team : (team.name || team);
                const teamSport = typeof team === 'object' ? (team.sport || 'Unknown') : 'Unknown';
                
                const teamDiv = document.createElement('div');
                teamDiv.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; background: #f8f9fa; border-radius: 5px; margin-bottom: 0.5rem;';
                
                const teamSpan = document.createElement('span');
                teamSpan.style.fontWeight = '500';
                teamSpan.textContent = `${teamName} (${teamSport})`;
                teamDiv.appendChild(teamSpan);
                
                const removeBtn = document.createElement('button');
                removeBtn.className = 'btn btn-secondary';
                removeBtn.style.cssText = 'padding: 0.25rem 0.75rem; font-size: 0.9rem;';
                removeBtn.textContent = 'Remove';
                removeBtn.onclick = () => removeTeam(teamName, teamSport);
                teamDiv.appendChild(removeBtn);
                
                teamsList.appendChild(teamDiv);
            });
        } else {
            teamsList.innerHTML = '<div style="text-align: center; color: #666; padding: 1rem;">No teams added yet. Add a team above to get started.</div>';
        }
    } catch (error) {
        console.error('Error loading sports teams:', error);
        const teamsList = document.getElementById('sports-teams-list');
        if (teamsList) {
            teamsList.innerHTML = '<div class="error">Failed to load teams</div>';
        }
    }
}

export async function removeTeam(teamName, teamSport) {
    if (!confirm(`Remove "${teamName}" from your teams?`)) return;
    
    try {
        const response = await fetch('/api/settings/sports');
        const data = await response.json();
        let teams = data.teams || [];
        
        // Remove the team (handle both old string format and new object format)
        teams = teams.filter(t => {
            if (typeof t === 'string') {
                return t !== teamName;
            } else {
                return t.name !== teamName || t.sport !== teamSport;
            }
        });
        
        // Save updated teams
        const saveResponse = await fetch('/api/settings/sports', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ teams })
        });
        
        if (saveResponse.ok) {
            loadSportsTeams();
            loadSportsScores();
        } else {
            alert('Error removing team');
        }
    } catch (error) {
        console.error('Error removing team:', error);
        alert('Error removing team');
    }
}

export async function loadSportsScores() {
    try {
        const response = await fetch('/api/sports-scores');
        const scores = await response.json();
        
        const widget = document.getElementById('sports-widget');
        if (!widget) return;
        
        if (scores && scores.length > 0) {
            widget.innerHTML = '<div class="news-list">' + 
                scores.map(score => `
                    <div class="news-item">
                        <div class="news-source">${score.team}</div>
                        <div class="news-title">${score.event}</div>
                        <div class="news-desc">${score.status}${score.score ? ' • ' + score.score : ''}${score.date ? ' • ' + score.date : ''}</div>
                    </div>
                `).join('') + '</div>';
        } else {
            widget.innerHTML = '<div style="text-align: center; color: #666; padding: 2rem;">Add teams above to see scores</div>';
        }
    } catch (error) {
        console.error('Error loading sports scores:', error);
        const widget = document.getElementById('sports-widget');
        if (widget) {
            widget.innerHTML = '<div class="error">Failed to load sports scores</div>';
        }
    }
}

// Make function available globally for onclick handlers
window.removeTeam = removeTeam;

