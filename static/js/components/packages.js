// Packages Component
let archivePage = 1;
const archivePerPage = 5;

export async function loadPackages() {
    try {
        const response = await fetch('/api/dashboard-data');
        const data = await response.json();
        
        const widget = document.getElementById('packages-widget');
        if (!widget) return;
        
        if (data.packages && data.packages.length > 0) {
            widget.innerHTML = '<div class="news-list">' + 
                data.packages.map(pkg => {
                    const statusColor = pkg.status === 'Delivered' ? '#4caf50' : 
                                       pkg.status === 'Error' ? '#f44336' : '#2196F3';
                    return `
                        <div class="news-item">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                                <div>
                                    <div class="news-source">${pkg.carrier} - ${pkg.tracking_number}</div>
                                    <div class="news-title">${pkg.description || 'Package'}</div>
                                </div>
                                <div>
                                    <button onclick="refreshPackage(${pkg.id})" class="btn btn-secondary" style="padding: 0.25rem 0.75rem; font-size: 0.9rem; margin-right: 0.5rem;">Refresh</button>
                                    <button onclick="deletePackage(${pkg.id})" class="btn btn-secondary" style="padding: 0.25rem 0.75rem; font-size: 0.9rem;">Delete</button>
                                </div>
                            </div>
                            <div class="news-desc">
                                <strong style="color: ${statusColor};">Status:</strong> ${pkg.status}
                                ${pkg.last_location ? ` • ${pkg.last_location}` : ''}
                                ${pkg.estimated_delivery ? ` • ETA: ${pkg.estimated_delivery}` : ''}
                            </div>
                        </div>
                    `;
                }).join('') + '</div>';
        } else {
            widget.innerHTML = '<div style="text-align: center; color: #666; padding: 2rem;">No packages being tracked</div>';
        }
        
        // Load archived packages
        loadPackagesArchive();
    } catch (error) {
        console.error('Error loading packages:', error);
        const widget = document.getElementById('packages-widget');
        if (widget) {
            widget.innerHTML = '<div class="error">Failed to load packages</div>';
        }
    }
}

export async function loadPackagesArchive(page = 1) {
    try {
        const response = await fetch(`/api/packages/archive?page=${page}&per_page=${archivePerPage}`);
        const data = await response.json();
        
        const archiveDiv = document.getElementById('packages-archive');
        const archiveList = document.getElementById('packages-archive-list');
        const paginationDiv = document.getElementById('packages-archive-pagination');
        const pageInfo = document.getElementById('archive-page-info');
        const prevBtn = document.getElementById('archive-prev-btn');
        const nextBtn = document.getElementById('archive-next-btn');
        
        if (!archiveDiv || !archiveList) return;
        
        if (data.packages && data.packages.length > 0) {
            archiveDiv.style.display = 'block';
            archiveList.innerHTML = data.packages.map(pkg => `
                <div class="news-item">
                    <div class="news-source">${pkg.carrier} - ${pkg.tracking_number}</div>
                    <div class="news-title">${pkg.description || 'Package'}</div>
                    <div class="news-desc">Status: ${pkg.status}${pkg.last_location ? ` • ${pkg.last_location}` : ''}</div>
                    <div class="news-desc" style="font-size: 0.85rem; color: #999;">Archived: ${pkg.archived_at}</div>
                </div>
            `).join('');
            
            if (data.total_pages > 1) {
                paginationDiv.style.display = 'flex';
                pageInfo.textContent = `Page ${data.page} of ${data.total_pages} (${data.total_count} total)`;
                prevBtn.disabled = !data.has_prev;
                nextBtn.disabled = !data.has_next;
                archivePage = data.page;
                setupArchivePagination();
            } else {
                paginationDiv.style.display = 'none';
            }
        } else if (data.total_count > 0) {
            archiveDiv.style.display = 'block';
            archiveList.innerHTML = '<div style="text-align: center; color: #666; padding: 2rem;">No packages on this page</div>';
            paginationDiv.style.display = 'flex';
            pageInfo.textContent = `Page ${data.page} of ${data.total_pages}`;
            prevBtn.disabled = !data.has_prev;
            nextBtn.disabled = !data.has_next;
            archivePage = data.page;
            setupArchivePagination();
        } else {
            archiveDiv.style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading archived packages:', error);
    }
}

export function setupArchivePagination() {
    const prevBtn = document.getElementById('archive-prev-btn');
    const nextBtn = document.getElementById('archive-next-btn');
    
    if (prevBtn && !prevBtn.hasAttribute('data-listener-added')) {
        prevBtn.setAttribute('data-listener-added', 'true');
        prevBtn.addEventListener('click', () => {
            if (archivePage > 1) {
                loadPackagesArchive(archivePage - 1);
            }
        });
    }
    
    if (nextBtn && !nextBtn.hasAttribute('data-listener-added')) {
        nextBtn.setAttribute('data-listener-added', 'true');
        nextBtn.addEventListener('click', () => {
            loadPackagesArchive(archivePage + 1);
        });
    }
}

export async function refreshPackage(packageId) {
    try {
        const response = await fetch(`/api/packages/${packageId}/refresh`, { method: 'POST' });
        if (response.ok) {
            loadPackages();
        }
    } catch (error) {
        console.error('Error refreshing package:', error);
        alert('Error refreshing package');
    }
}

export async function deletePackage(packageId) {
    if (!confirm('Delete this package?')) return;
    try {
        const response = await fetch(`/api/packages/${packageId}`, { method: 'DELETE' });
        if (response.ok) {
            loadPackages();
        }
    } catch (error) {
        console.error('Error deleting package:', error);
        alert('Error deleting package');
    }
}

export function setupPackageForm() {
    const form = document.getElementById('add-package-form');
    if (!form) return;
    
    if (form.hasAttribute('data-listener-added')) return;
    form.setAttribute('data-listener-added', 'true');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const tracking = document.getElementById('package-tracking').value.trim();
        const description = document.getElementById('package-description').value.trim();
        
        try {
            const response = await fetch('/api/packages', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tracking_number: tracking, description: description })
            });
            if (response.ok) {
                form.reset();
                loadPackages();
            } else {
                const error = await response.json();
                alert('Error adding package: ' + (error.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error adding package:', error);
            alert('Error adding package');
        }
    });
}

// Make functions available globally for onclick handlers
window.refreshPackage = refreshPackage;
window.deletePackage = deletePackage;

