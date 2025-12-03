// Shopping List Component
export async function loadShoppingList() {
    try {
        const response = await fetch('/api/shopping-list');
        const items = await response.json();
        
        const widget = document.getElementById('shopping-list-widget');
        if (!widget) return;
        
        if (items && items.length > 0) {
            widget.innerHTML = '<div class="news-list">' + 
                items.map(item => {
                    const completedStyle = item.completed ? 
                        'text-decoration: line-through; opacity: 0.6; color: #999;' : '';
                    return `
                        <div class="news-item" style="${completedStyle}">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="display: flex; align-items: center; gap: 0.5rem; flex: 1;">
                                    <input type="checkbox" ${item.completed ? 'checked' : ''} 
                                           onchange="toggleShoppingItem(${item.id}, ${!item.completed})" 
                                           style="cursor: pointer;">
                                    <span style="flex: 1;">${item.item_name}</span>
                                </div>
                                <button onclick="deleteShoppingItem(${item.id})" 
                                        class="btn btn-secondary" 
                                        style="padding: 0.25rem 0.75rem; font-size: 0.9rem; margin-left: 0.5rem;">
                                    Delete
                                </button>
                            </div>
                        </div>
                    `;
                }).join('') + '</div>';
        } else {
            widget.innerHTML = '<div style="text-align: center; color: #666; padding: 2rem;">No items in shopping list</div>';
        }
    } catch (error) {
        console.error('Error loading shopping list:', error);
        const widget = document.getElementById('shopping-list-widget');
        if (widget) {
            widget.innerHTML = '<div class="error">Failed to load shopping list</div>';
        }
    }
}

export async function addShoppingItem() {
    const itemName = document.getElementById('shopping-item-name');
    if (!itemName) return;
    
    const name = itemName.value.trim();
    if (!name) {
        alert('Please enter an item name');
        return;
    }
    
    try {
        const response = await fetch('/api/shopping-list', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_name: name })
        });
        if (response.ok) {
            itemName.value = '';
            loadShoppingList();
        } else {
            const error = await response.json();
            alert('Error adding item: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error adding shopping item:', error);
        alert('Error adding item');
    }
}

export async function toggleShoppingItem(itemId, completed) {
    try {
        const response = await fetch(`/api/shopping-list/${itemId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ completed: completed })
        });
        if (response.ok) {
            loadShoppingList();
        } else {
            const error = await response.json();
            alert('Error updating item: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error toggling shopping item:', error);
        alert('Error updating item');
    }
}

export async function deleteShoppingItem(itemId) {
    if (!confirm('Delete this item?')) return;
    try {
        const response = await fetch(`/api/shopping-list/${itemId}`, { method: 'DELETE' });
        if (response.ok) {
            loadShoppingList();
        } else {
            const error = await response.json();
            alert('Error deleting item: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error deleting shopping item:', error);
        alert('Error deleting item');
    }
}

export function setupShoppingListForm() {
    const form = document.getElementById('add-shopping-item-form');
    if (!form) return;
    
    if (form.hasAttribute('data-listener-added')) return;
    form.setAttribute('data-listener-added', 'true');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await addShoppingItem();
    });
}

// Make functions available globally for onclick handlers
window.toggleShoppingItem = toggleShoppingItem;
window.deleteShoppingItem = deleteShoppingItem;

