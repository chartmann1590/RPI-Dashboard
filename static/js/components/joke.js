// Joke Component
let jokeHistoryPage = 1;
const jokeHistoryPerPage = 5;

export async function loadJoke() {
    try {
        const response = await fetch('/api/dashboard-data');
        const data = await response.json();
        
        const widget = document.getElementById('joke-widget');
        if (!widget) return;
        
        if (data.joke) {
            widget.innerHTML = `
                <div class="joke-current">
                    ${data.joke.text || 'No joke available'}
                    <div class="joke-updated">Updated: ${data.joke.updated || ''}</div>
                </div>
            `;
        } else {
            widget.innerHTML = '<div class="error">Joke data unavailable</div>';
        }
        
        // Load joke history
        loadJokeHistory();
    } catch (error) {
        console.error('Error loading joke:', error);
        const widget = document.getElementById('joke-widget');
        if (widget) {
            widget.innerHTML = '<div class="error">Failed to load joke data</div>';
        }
    }
}

export async function loadJokeHistory(page = 1) {
    try {
        const response = await fetch(`/api/joke-history?page=${page}&per_page=${jokeHistoryPerPage}`);
        const data = await response.json();
        
        const historyDiv = document.getElementById('joke-history');
        const historyList = document.getElementById('joke-history-list');
        const paginationDiv = document.getElementById('joke-history-pagination');
        const pageInfo = document.getElementById('joke-page-info');
        const prevBtn = document.getElementById('joke-prev-btn');
        const nextBtn = document.getElementById('joke-next-btn');
        
        if (!historyDiv || !historyList) return;
        
        if (data.jokes && data.jokes.length > 0) {
            historyDiv.style.display = 'block';
            historyList.innerHTML = data.jokes.map(joke => `
                <div class="joke-history-item">
                    <div class="joke-history-text">${joke.text}</div>
                    <div class="joke-history-timestamp">${joke.timestamp}</div>
                </div>
            `).join('');
            
            // Update pagination controls
            if (data.total_pages > 1) {
                paginationDiv.style.display = 'flex';
                pageInfo.textContent = `Page ${data.page} of ${data.total_pages} (${data.total_count} total)`;
                prevBtn.disabled = !data.has_prev;
                nextBtn.disabled = !data.has_next;
                jokeHistoryPage = data.page;
                setupJokePagination();
            } else {
                paginationDiv.style.display = 'none';
            }
        } else if (data.total_count > 0) {
            historyDiv.style.display = 'block';
            historyList.innerHTML = '<div style="text-align: center; color: #666; padding: 2rem;">No jokes on this page</div>';
            paginationDiv.style.display = 'flex';
            pageInfo.textContent = `Page ${data.page} of ${data.total_pages}`;
            prevBtn.disabled = !data.has_prev;
            nextBtn.disabled = !data.has_next;
            jokeHistoryPage = data.page;
            setupJokePagination();
        } else {
            historyDiv.style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading joke history:', error);
    }
}

export function setupJokePagination() {
    const jokePrevBtn = document.getElementById('joke-prev-btn');
    const jokeNextBtn = document.getElementById('joke-next-btn');
    
    if (jokePrevBtn && !jokePrevBtn.hasAttribute('data-listener-added')) {
        jokePrevBtn.setAttribute('data-listener-added', 'true');
        jokePrevBtn.addEventListener('click', () => {
            if (jokeHistoryPage > 1) {
                loadJokeHistory(jokeHistoryPage - 1);
            }
        });
    }
    
    if (jokeNextBtn && !jokeNextBtn.hasAttribute('data-listener-added')) {
        jokeNextBtn.setAttribute('data-listener-added', 'true');
        jokeNextBtn.addEventListener('click', () => {
            loadJokeHistory(jokeHistoryPage + 1);
        });
    }
}

