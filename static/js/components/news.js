// News Component
export async function loadNews() {
    try {
        const response = await fetch('/api/dashboard-data');
        const data = await response.json();
        
        const widget = document.getElementById('news-widget');
        if (!widget) return;
        
        if (data.news && data.news.length > 0) {
            // Get the news type from the first article
            const newsType = data.news[0].news_type || 'News';
            
            // Update the news header to show what type of news we're displaying
            const newsHeader = document.querySelector('.card h2');
            if (newsHeader && newsHeader.textContent.includes('News')) {
                newsHeader.innerHTML = `📰 ${newsType}`;
            }
            
            widget.innerHTML = '<div class="news-list">' + 
                data.news.map(article => `
                    <div class="news-item">
                        <div class="news-source">${article.source}</div>
                        <div class="news-title">${article.title}</div>
                        ${article.description ? `<div class="news-desc">${article.description}</div>` : ''}
                    </div>
                `).join('') + '</div>';
        } else {
            widget.innerHTML = '<div class="error">News data unavailable</div>';
        }
    } catch (error) {
        console.error('Error loading news:', error);
        const widget = document.getElementById('news-widget');
        if (widget) {
            widget.innerHTML = '<div class="error">Failed to load news data</div>';
        }
    }
}

