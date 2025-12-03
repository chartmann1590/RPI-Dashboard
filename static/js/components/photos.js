// Photos Component
export async function loadPhotos() {
    try {
        const response = await fetch('/api/photos');
        const photos = await response.json();
        
        const gallery = document.getElementById('photo-gallery');
        if (!gallery) return;
        
        if (photos && photos.length > 0) {
            gallery.innerHTML = '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1rem;">' +
                photos.map(photo => `
                    <div style="position: relative;">
                        <img src="${photo.url}" alt="${photo.filename}" style="width: 100%; height: 150px; object-fit: cover; border-radius: 8px; cursor: pointer;" onclick="deletePhoto('${photo.filename}')">
                        <button onclick="deletePhoto('${photo.filename}')" class="btn btn-secondary" style="position: absolute; top: 5px; right: 5px; padding: 0.25rem 0.5rem; font-size: 0.8rem;">×</button>
                    </div>
                `).join('') + '</div>';
        } else {
            gallery.innerHTML = '<div style="text-align: center; color: #666; padding: 2rem;">No photos uploaded yet</div>';
        }
    } catch (error) {
        console.error('Error loading photos:', error);
        const gallery = document.getElementById('photo-gallery');
        if (gallery) {
            gallery.innerHTML = '<div class="error">Failed to load photos</div>';
        }
    }
}

export async function deletePhoto(filename) {
    if (!confirm('Delete this photo?')) return;
    try {
        const response = await fetch(`/api/delete-photo/${filename}`, { method: 'DELETE' });
        if (response.ok) {
            loadPhotos();
        }
    } catch (error) {
        console.error('Error deleting photo:', error);
        alert('Error deleting photo');
    }
}

export function setupPhotoUpload() {
    const photoInput = document.getElementById('photo-input');
    if (!photoInput) return;
    
    if (photoInput.hasAttribute('data-listener-added')) return;
    photoInput.setAttribute('data-listener-added', 'true');
    
    photoInput.addEventListener('change', async (e) => {
        const files = e.target.files;
        const progressDiv = document.getElementById('upload-progress');
        if (progressDiv) {
            progressDiv.style.display = 'block';
            progressDiv.innerHTML = `Uploading ${files.length} photo(s)...`;
        }
        
        for (let file of files) {
            const formData = new FormData();
            formData.append('photo', file);
            
            try {
                const response = await fetch('/api/upload-photo', {
                    method: 'POST',
                    body: formData
                });
                if (!response.ok) throw new Error('Upload failed');
            } catch (error) {
                console.error('Error uploading photo:', error);
                alert(`Error uploading ${file.name}`);
            }
        }
        
        if (progressDiv) {
            progressDiv.innerHTML = 'Upload complete!';
            setTimeout(() => {
                progressDiv.style.display = 'none';
                loadPhotos();
            }, 2000);
        }
    });
}

// Make function available globally for onclick handlers
window.deletePhoto = deletePhoto;

