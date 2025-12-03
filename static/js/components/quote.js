// Quote Component
let quoteHistoryPage = 1;
const quoteHistoryPerPage = 5;

export async function loadQuote() {
    try {
        const response = await fetch('/api/daily-quote');
        const quote = await response.json();
        
        const widget = document.getElementById('quote-widget');
        if (!widget) return;
        
        if (quote) {
            widget.innerHTML = `
                <div style="padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px;">
                    <div style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 0.5rem;">"${quote.text}"</div>
                    <div style="text-align: right; font-style: italic;">— ${quote.author}</div>
                </div>
            `;
        } else {
            widget.innerHTML = '<div class="error">Quote unavailable</div>';
        }
        
        // Load quote history
        loadQuoteHistory();
    } catch (error) {
        console.error('Error loading quote:', error);
        const widget = document.getElementById('quote-widget');
        if (widget) {
            widget.innerHTML = '<div class="error">Failed to load quote</div>';
        }
    }
}

export async function loadQuoteHistory(page = 1) {
    try {
        const response = await fetch(`/api/quote-history?page=${page}&per_page=${quoteHistoryPerPage}`);
        const data = await response.json();
        
        const historyDiv = document.getElementById('quote-history');
        const historyList = document.getElementById('quote-history-list');
        const paginationDiv = document.getElementById('quote-history-pagination');
        const pageInfo = document.getElementById('quote-page-info');
        const prevBtn = document.getElementById('quote-prev-btn');
        const nextBtn = document.getElementById('quote-next-btn');
        
        if (!historyDiv || !historyList) return;
        
        if (data.quotes && data.quotes.length > 0) {
            historyDiv.style.display = 'block';
            historyList.innerHTML = data.quotes.map(quote => `
                <div class="quote-history-item">
                    <div class="quote-history-text">"${quote.text}"</div>
                    <div class="quote-history-author">— ${quote.author}</div>
                    <div class="quote-history-timestamp">${quote.timestamp}</div>
                </div>
            `).join('');
            
            // Update pagination controls
            if (data.total_pages > 1) {
                paginationDiv.style.display = 'flex';
                pageInfo.textContent = `Page ${data.page} of ${data.total_pages} (${data.total_count} total)`;
                prevBtn.disabled = !data.has_prev;
                nextBtn.disabled = !data.has_next;
                quoteHistoryPage = data.page;
                setupQuotePagination();
            } else {
                paginationDiv.style.display = 'none';
            }
        } else if (data.total_count > 0) {
            historyDiv.style.display = 'block';
            historyList.innerHTML = '<div style="text-align: center; color: #666; padding: 2rem;">No quotes on this page</div>';
            paginationDiv.style.display = 'flex';
            pageInfo.textContent = `Page ${data.page} of ${data.total_pages}`;
            prevBtn.disabled = !data.has_prev;
            nextBtn.disabled = !data.has_next;
            quoteHistoryPage = data.page;
            setupQuotePagination();
        } else {
            historyDiv.style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading quote history:', error);
    }
}

export function setupQuotePagination() {
    const quotePrevBtn = document.getElementById('quote-prev-btn');
    const quoteNextBtn = document.getElementById('quote-next-btn');
    
    if (quotePrevBtn && !quotePrevBtn.hasAttribute('data-listener-added')) {
        quotePrevBtn.setAttribute('data-listener-added', 'true');
        quotePrevBtn.addEventListener('click', () => {
            if (quoteHistoryPage > 1) {
                loadQuoteHistory(quoteHistoryPage - 1);
            }
        });
    }
    
    if (quoteNextBtn && !quoteNextBtn.hasAttribute('data-listener-added')) {
        quoteNextBtn.setAttribute('data-listener-added', 'true');
        quoteNextBtn.addEventListener('click', () => {
            loadQuoteHistory(quoteHistoryPage + 1);
        });
    }
}

