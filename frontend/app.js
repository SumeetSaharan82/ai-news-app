// API Configuration
const API_BASE_URL = (window.location.hostname === 'localhost' || window.location.protocol === 'file:')
    ? 'http://localhost:8000/api/v1'
    : 'https://your-railway-app.railway.app/api/v1';

// State
let selectedCategories = [];
let selectedRegion = 'global';
let authToken = localStorage.getItem('authToken');
let currentUser = null;
let preferenceCategories = [];
let preferenceRegion = 'global';
let profileCategories = [];
let profileRegion = 'global';

// News cache for efficient loading
const newsCache = new Map(); // Key: category-region, Value: {articles, timestamp}
const CACHE_EXPIRY = 5 * 60 * 1000; // 5 minutes

// Category Icons
const categoryIcons = {
    'general': '📰',
    'technology': '💻',
    'business': '💼',
    'sports': '⚽',
    'entertainment': '🎬',
    'health': '🏥',
    'science': '🔬',
    'politics': '🏛️'
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkAuthStatus();
});

// Load Categories for Preference Modal
async function loadPreferenceCategories() {
    try {
        const response = await fetch(`${API_BASE_URL}/categories`);
        const data = await response.json();
        
        const categoryGrid = document.getElementById('preferenceCategoryGrid');
        const profileCategoryGrid = document.getElementById('profileCategoryGrid');
        
        if (!categoryGrid || !profileCategoryGrid) {
            console.error('Preference category grids not found!');
            return;
        }
        
        categoryGrid.innerHTML = '';
        profileCategoryGrid.innerHTML = '';
        
        const categories = Array.isArray(data) ? data : (data.categories || []);
        
        categories.forEach(category => {
            // For preference modal
            const prefItem = document.createElement('div');
            prefItem.className = 'category-item';
            prefItem.dataset.category = category;
            prefItem.innerHTML = `
                <div class="icon">${categoryIcons[category] || '📰'}</div>
                <div class="name">${category.charAt(0).toUpperCase() + category.slice(1)}</div>
            `;
            prefItem.addEventListener('click', () => togglePreferenceCategory(category, prefItem));
            categoryGrid.appendChild(prefItem);
            
            // For profile modal
            const profileItem = document.createElement('div');
            profileItem.className = 'category-item';
            profileItem.dataset.category = category;
            profileItem.innerHTML = `
                <div class="icon">${categoryIcons[category] || '📰'}</div>
                <div class="name">${category.charAt(0).toUpperCase() + category.slice(1)}</div>
            `;
            profileItem.addEventListener('click', () => toggleProfileCategory(category, profileItem));
            profileCategoryGrid.appendChild(profileItem);
        });
    } catch (error) {
        console.error('Error loading preference categories:', error);
    }
}

// Load Regions for Preference Modal
async function loadPreferenceRegions() {
    try {
        const response = await fetch(`${API_BASE_URL}/regions`);
        const data = await response.json();
        
        const regionGrid = document.getElementById('preferenceRegionGrid');
        const profileRegionGrid = document.getElementById('profileRegionGrid');
        
        if (!regionGrid || !profileRegionGrid) {
            console.error('Preference region grids not found!');
            return;
        }
        
        regionGrid.innerHTML = '';
        profileRegionGrid.innerHTML = '';
        
        const regions = Array.isArray(data) ? data : (data.regions || []);
        
        regions.forEach(region => {
            // For preference modal
            const prefItem = document.createElement('div');
            prefItem.className = 'region-item';
            prefItem.dataset.region = region;
            prefItem.innerHTML = `
                <div class="name">${getRegionName(region)}</div>
            `;
            prefItem.addEventListener('click', () => selectPreferenceRegion(region, prefItem));
            regionGrid.appendChild(prefItem);
            
            // For profile modal
            const profileItem = document.createElement('div');
            profileItem.className = 'region-item';
            profileItem.dataset.region = region;
            profileItem.innerHTML = `
                <div class="name">${getRegionName(region)}</div>
            `;
            profileItem.addEventListener('click', () => selectProfileRegion(region, profileItem));
            profileRegionGrid.appendChild(profileItem);
        });
    } catch (error) {
        console.error('Error loading preference regions:', error);
    }
}

// Toggle Preference Category Selection
function togglePreferenceCategory(category, element) {
    const index = preferenceCategories.indexOf(category);
    
    if (index > -1) {
        preferenceCategories.splice(index, 1);
        element.classList.remove('selected');
    } else {
        preferenceCategories.push(category);
        element.classList.add('selected');
    }
}

// Toggle Profile Category Selection
function toggleProfileCategory(category, element) {
    const index = profileCategories.indexOf(category);
    
    if (index > -1) {
        profileCategories.splice(index, 1);
        element.classList.remove('selected');
    } else {
        profileCategories.push(category);
        element.classList.add('selected');
    }
}

// Select Preference Region
function selectPreferenceRegion(region, element) {
    preferenceRegion = region;
    
    document.querySelectorAll('#preferenceRegionGrid .region-item').forEach(item => {
        item.classList.remove('selected');
    });
    element.classList.add('selected');
}

// Select Profile Region
function selectProfileRegion(region, element) {
    profileRegion = region;
    
    document.querySelectorAll('#profileRegionGrid .region-item').forEach(item => {
        item.classList.remove('selected');
    });
    element.classList.add('selected');
}

// Load News for all selected categories
async function loadNews() {
    if (selectedCategories.length === 0) {
        showError('Please select at least one category');
        return;
    }
    
    showLoading(true);
    hideError();
    
    // Map region codes to full names
    const regionMap = {
        'in': 'india',
        'us': 'us',
        'gb': 'gb',
        'global': 'global'
    };
    const region = regionMap[selectedRegion] || selectedRegion;
    
    console.log('Loading news for all categories - Categories:', selectedCategories, 'Region:', region);
    
    try {
        // Fetch news for each category
        const newsPromises = selectedCategories.map(async (category) => {
            const cacheKey = `${category}-${region}`;
            
            // Check cache first
            const cached = newsCache.get(cacheKey);
            if (cached && (Date.now() - cached.timestamp) < CACHE_EXPIRY) {
                console.log(`Using cached news for ${category}`);
                return { category, articles: cached.articles };
            }
            
            // Fetch from API
            console.log(`Fetching news for ${category} from API`);
            const response = await fetch(
                `${API_BASE_URL}/news?category=${category}&region=${region}&limit=12`
            );
            const data = await response.json();
            
            // Cache the results
            newsCache.set(cacheKey, {
                articles: data.articles || [],
                timestamp: Date.now()
            });
            
            return { category, articles: data.articles || [] };
        });
        
        const results = await Promise.all(newsPromises);
        
        // Display news in category sections
        displayNewsByCategory(results);
        
        // Update header
        const categoryNames = selectedCategories.map(cat => 
            cat.charAt(0).toUpperCase() + cat.slice(1)
        ).join(', ');
        document.getElementById('newsTitle').textContent = 
            `${categoryNames} News - ${getRegionName(selectedRegion)}`;
        
    } catch (error) {
        console.error('Error loading news:', error);
        showError('Failed to load news. Please try again.');
    } finally {
        showLoading(false);
    }
}

// Display News by Category
function displayNewsByCategory(results) {
    console.log('Displaying news by category:', results);
    const newsContainer = document.getElementById('newsContainer');
    if (!newsContainer) {
        console.error('newsContainer element not found!');
        return;
    }
    newsContainer.innerHTML = '';
    
    results.forEach(({ category, articles }) => {
        // Create category section
        const categorySection = document.createElement('div');
        categorySection.className = 'category-section';
        
        const categoryTitle = document.createElement('h3');
        categoryTitle.className = 'category-title';
        categoryTitle.innerHTML = `${categoryIcons[category] || '📰'} ${category.charAt(0).toUpperCase() + category.slice(1)}`;
        categorySection.appendChild(categoryTitle);
        
        if (articles.length === 0) {
            const noArticles = document.createElement('p');
            noArticles.className = 'no-articles';
            noArticles.textContent = 'No articles found';
            categorySection.appendChild(noArticles);
        } else {
            const categoryGrid = document.createElement('div');
            categoryGrid.className = 'category-grid';
            
            articles.forEach(article => {
                const newsCard = document.createElement('div');
                newsCard.className = 'news-card';
                newsCard.innerHTML = `
                    ${article.image_url ? `<img src="${article.image_url}" alt="${article.title}" onerror="this.style.display='none'">` : ''}
                    <div class="news-card-content">
                        <span class="category">${article.category}</span>
                        <h3 class="title">${article.title}</h3>
                        <p class="description">${article.description || 'No description available'}</p>
                        <div class="meta">
                            <span class="source">${article.source}</span>
                            <span class="date">${formatDate(article.published_at)}</span>
                        </div>
                    </div>
                `;
                newsCard.addEventListener('click', () => window.open(article.url, '_blank'));
                categoryGrid.appendChild(newsCard);
            });
            
            categorySection.appendChild(categoryGrid);
        }
        
        newsContainer.appendChild(categorySection);
    });
    
    console.log('News displayed by category successfully');
}

// Display News (legacy function for single category)
function displayNews(articles) {
    console.log('Displaying articles:', articles);
    const newsGrid = document.getElementById('newsGrid');
    if (!newsGrid) {
        console.error('newsGrid element not found!');
        return;
    }
    newsGrid.innerHTML = '';
    
    if (articles.length === 0) {
        newsGrid.innerHTML = '<p style="text-align: center; color: #666;">No articles found</p>';
        return;
    }
    
    articles.forEach(article => {
        const newsCard = document.createElement('div');
        newsCard.className = 'news-card';
        newsCard.innerHTML = `
            ${article.image_url ? `<img src="${article.image_url}" alt="${article.title}" onerror="this.style.display='none'">` : ''}
            <div class="news-card-content">
                <span class="category">${article.category}</span>
                <h3 class="title">${article.title}</h3>
                <p class="description">${article.description || 'No description available'}</p>
                <div class="meta">
                    <span class="source">${article.source}</span>
                    <span class="date">${formatDate(article.published_at)}</span>
                </div>
            </div>
        `;
        newsCard.addEventListener('click', () => window.open(article.url, '_blank'));
        newsGrid.appendChild(newsCard);
    });
    
    console.log('News cards rendered successfully');
}

// Format Date
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);
    
    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
}

// Get proper region name for display
function getRegionName(regionCode) {
    const regionNames = {
        'us': 'United States',
        'gb': 'United Kingdom',
        'ca': 'Canada',
        'au': 'Australia',
        'in': 'India',
        'de': 'Germany',
        'fr': 'France',
        'it': 'Italy',
        'es': 'Spain',
        'nl': 'Netherlands',
        'global': 'Global'
    };
    return regionNames[regionCode] || regionCode.toUpperCase();
}

// Authentication
function checkAuthStatus() {
    if (authToken) {
        document.getElementById('loginBtn').classList.add('hidden');
        document.getElementById('registerBtn').classList.add('hidden');
        document.getElementById('profileBtn').classList.remove('hidden');
        document.getElementById('logoutBtn').classList.remove('hidden');
        document.getElementById('welcomeSection').classList.add('hidden');
        loadCurrentUser();
    } else {
        document.getElementById('loginBtn').classList.remove('hidden');
        document.getElementById('registerBtn').classList.remove('hidden');
        document.getElementById('profileBtn').classList.add('hidden');
        document.getElementById('logoutBtn').classList.add('hidden');
        document.getElementById('welcomeSection').classList.remove('hidden');
        document.getElementById('newsSection').classList.add('hidden');
        document.getElementById('analysisSection').classList.add('hidden');
    }
}

async function loadCurrentUser() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            console.log('Current user preferences:', currentUser.preferences);
            
            // Check if user has preferences set
            if (currentUser.preferences && currentUser.preferences.categories && currentUser.preferences.categories.length > 0) {
                // User has preferences, load news directly
                selectedCategories = currentUser.preferences.categories;
                selectedRegion = currentUser.preferences.region || 'global';
                console.log('Loaded preferences - Categories:', selectedCategories, 'Region:', selectedRegion);
                document.getElementById('newsSection').classList.remove('hidden');
                document.getElementById('analysisSection').classList.remove('hidden');
                loadNews();
            } else {
                // User needs to set preferences
                console.log('No preferences found, showing preference modal');
                showPreferenceModal();
            }
        }
    } catch (error) {
        console.error('Error loading user:', error);
    }
}

// Show Preference Modal
function showPreferenceModal() {
    loadPreferenceCategories();
    loadPreferenceRegions();
    document.getElementById('preferenceModal').classList.remove('hidden');
}

// Close Preference Modal
function closePreferenceModal() {
    document.getElementById('preferenceModal').classList.add('hidden');
    preferenceCategories = [];
    preferenceRegion = 'global';
}

// Save Preferences
async function savePreferences() {
    if (preferenceCategories.length === 0) {
        alert('Please select at least one category');
        return;
    }
    
    console.log('Saving preferences - Categories:', preferenceCategories, 'Region:', preferenceRegion);
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/preferences`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                categories: preferenceCategories,
                region: preferenceRegion
            })
        });
        
        console.log('Save response status:', response.status);
        
        if (response.ok) {
            selectedCategories = preferenceCategories;
            selectedRegion = preferenceRegion;
            
            // Clear cache when preferences change
            newsCache.clear();
            console.log('Cache cleared due to preference change');
            
            closePreferenceModal();
            document.getElementById('newsSection').classList.remove('hidden');
            document.getElementById('analysisSection').classList.remove('hidden');
            
            // Force news reload with new preferences
            console.log('Triggering news reload with new preferences...');
            await loadNews();
            
            alert('Preferences saved successfully!');
        } else {
            console.error('Failed to save preferences - Response:', await response.text());
            alert('Failed to save preferences');
        }
    } catch (error) {
        console.error('Error saving preferences:', error);
        alert('Failed to save preferences');
    }
}

// Show Profile Modal
function showProfileModal() {
    loadPreferenceCategories();
    loadPreferenceRegions();
    
    // Load current user preferences
    if (currentUser && currentUser.preferences) {
        profileCategories = currentUser.preferences.categories || [];
        profileRegion = currentUser.preferences.region || 'global';
        
        // Select current categories in profile modal
        setTimeout(() => {
            document.querySelectorAll('#profileCategoryGrid .category-item').forEach(item => {
                const category = item.dataset.category;
                if (profileCategories.includes(category)) {
                    item.classList.add('selected');
                }
            });
            
            // Select current region in profile modal
            document.querySelectorAll('#profileRegionGrid .region-item').forEach(item => {
                const region = item.dataset.region;
                if (region === profileRegion) {
                    item.classList.add('selected');
                }
            });
        }, 100);
    }
    
    // Display user info
    const profileInfo = document.getElementById('profileInfo');
    profileInfo.innerHTML = `
        <p><strong>Name:</strong> ${currentUser ? currentUser.name : 'N/A'}</p>
        <p><strong>Email:</strong> ${currentUser ? currentUser.email : 'N/A'}</p>
        <p><strong>Current Categories:</strong> ${profileCategories.join(', ')}</p>
        <p><strong>Current Region:</strong> ${getRegionName(profileRegion)}</p>
    `;
    
    document.getElementById('profileModal').classList.remove('hidden');
}

// Close Profile Modal
function closeProfileModal() {
    document.getElementById('profileModal').classList.add('hidden');
    profileCategories = [];
    profileRegion = 'global';
}

// Update Preferences from Profile
async function updatePreferences() {
    if (profileCategories.length === 0) {
        alert('Please select at least one category');
        return;
    }
    
    console.log('Updating preferences - Categories:', profileCategories, 'Region:', profileRegion);
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/preferences`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                categories: profileCategories,
                region: profileRegion
            })
        });
        
        console.log('Update response status:', response.status);
        
        if (response.ok) {
            selectedCategories = profileCategories;
            selectedRegion = profileRegion;
            currentUser.preferences.categories = profileCategories;
            currentUser.preferences.region = profileRegion;
            
            // Clear cache when preferences change
            newsCache.clear();
            console.log('Cache cleared due to preference change');
            
            console.log('Preferences updated successfully - Selected Region:', selectedRegion);
            closeProfileModal();
            
            // Force news reload with new preferences
            console.log('Triggering news reload with new preferences...');
            await loadNews();
            
            alert('Preferences updated successfully!');
        } else {
            console.error('Failed to update preferences - Response:', await response.text());
            alert('Failed to update preferences');
        }
    } catch (error) {
        console.error('Error updating preferences:', error);
        alert('Failed to update preferences');
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Auth buttons
    document.getElementById('loginBtn').addEventListener('click', () => openAuthModal('login'));
    document.getElementById('registerBtn').addEventListener('click', () => openAuthModal('register'));
    document.getElementById('logoutBtn').addEventListener('click', logout);
    document.getElementById('profileBtn').addEventListener('click', showProfileModal);
    
    // Modal close
    document.querySelector('.close').addEventListener('click', closeAuthModal);
    document.getElementById('authModal').addEventListener('click', (e) => {
        if (e.target.id === 'authModal') closeAuthModal();
    });
    
    // Preference modal close
    document.querySelectorAll('#preferenceModal .close, #profileModal .close').forEach(closeBtn => {
        closeBtn.addEventListener('click', (e) => {
            if (e.target.closest('#preferenceModal')) closePreferenceModal();
            if (e.target.closest('#profileModal')) closeProfileModal();
        });
    });
    
    document.getElementById('preferenceModal').addEventListener('click', (e) => {
        if (e.target.id === 'preferenceModal') closePreferenceModal();
    });
    
    document.getElementById('profileModal').addEventListener('click', (e) => {
        if (e.target.id === 'profileModal') closeProfileModal();
    });
    
    // Auth form
    document.getElementById('authForm').addEventListener('submit', handleAuth);
    
    // Save preferences button
    document.getElementById('savePreferencesBtn').addEventListener('click', savePreferences);
    
    // Update preferences button
    document.getElementById('updatePreferencesBtn').addEventListener('click', updatePreferences);
    
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', loadNews);
    
    // Analysis buttons
    document.getElementById('trendsBtn').addEventListener('click', loadTrends);
    document.getElementById('keywordsBtn').addEventListener('click', loadKeywords);
}

// Load Trends (placeholder - to be implemented)
async function loadTrends() {
    const analysisResults = document.getElementById('analysisResults');
    analysisResults.innerHTML = '<p>Trends feature coming soon...</p>';
}

// Load Keywords (placeholder - to be implemented)
async function loadKeywords() {
    const analysisResults = document.getElementById('analysisResults');
    analysisResults.innerHTML = '<p>Keywords feature coming soon...</p>';
}

// Auth Modal
let authMode = 'login';

function openAuthModal(mode) {
    authMode = mode;
    document.getElementById('authModalTitle').textContent = mode === 'login' ? 'Login' : 'Register';
    document.getElementById('nameGroup').classList.toggle('hidden', mode === 'login');
    document.getElementById('authModal').classList.remove('hidden');
}

function closeAuthModal() {
    document.getElementById('authModal').classList.add('hidden');
    document.getElementById('authForm').reset();
}

async function handleAuth(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const name = document.getElementById('name').value;
    
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    if (name && authMode === 'register') {
        formData.append('scope', name);  // Use scope to pass name for registration
    }
    
    const endpoint = authMode === 'login' ? '/auth/login' : '/auth/register';
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });
        
        const data = await response.json();
        
        console.log('Auth response:', response.status, data);
        
        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            closeAuthModal();
            checkAuthStatus();
            alert(authMode === 'login' ? 'Login successful!' : 'Registration successful!');
        } else {
            console.error('Auth failed:', data);
            alert(data.detail || 'Authentication failed');
        }
    } catch (error) {
        console.error('Auth error:', error);
        alert('Authentication failed. Please try again.');
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    document.getElementById('loginBtn').classList.remove('hidden');
    document.getElementById('registerBtn').classList.remove('hidden');
    document.getElementById('logoutBtn').classList.add('hidden');
    document.getElementById('personalizedSection').classList.add('hidden');
    document.getElementById('personalizedNewsGrid').innerHTML = '';
}

// Personalized News
async function loadPersonalizedNews() {
    if (!authToken) {
        alert('Please login to view personalized news');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/news/personalized?limit=12`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        const data = await response.json();
        
        const personalizedGrid = document.getElementById('personalizedNewsGrid');
        displayNewsInGrid(data.articles || [], personalizedGrid);
    } catch (error) {
        console.error('Error loading personalized news:', error);
        alert('Failed to load personalized news');
    } finally {
        showLoading(false);
    }
}

function displayNewsInGrid(articles, gridElement) {
    gridElement.innerHTML = '';
    
    if (articles.length === 0) {
        gridElement.innerHTML = '<p style="text-align: center; color: #666;">No articles found. Update your preferences.</p>';
        return;
    }
    
    articles.forEach(article => {
        const newsCard = document.createElement('div');
        newsCard.className = 'news-card';
        newsCard.innerHTML = `
            ${article.image_url ? `<img src="${article.image_url}" alt="${article.title}" onerror="this.style.display='none'">` : ''}
            <div class="news-card-content">
                <span class="category">${article.category}</span>
                <h3 class="title">${article.title}</h3>
                <p class="description">${article.description || 'No description available'}</p>
                <div class="meta">
                    <span class="source">${article.source}</span>
                    <span class="date">${formatDate(article.published_at)}</span>
                </div>
            </div>
        `;
        newsCard.addEventListener('click', () => window.open(article.url, '_blank'));
        gridElement.appendChild(newsCard);
    });
}

// Analysis Functions
async function loadTrends() {
    if (!authToken) {
        alert('Please login to view trends');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/analysis/trends?days=7`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        const data = await response.json();
        
        displayTrends(data);
    } catch (error) {
        console.error('Error loading trends:', error);
        alert('Failed to load trends');
    }
}

function displayTrends(data) {
    const resultsDiv = document.getElementById('analysisResults');
    
    let html = '<h3>📈 News Trends (Last 7 Days)</h3>';
    html += `<p><strong>Total Articles:</strong> ${data.total_articles}</p>`;
    
    html += '<h4>Category Distribution:</h4>';
    Object.entries(data.category_distribution).forEach(([category, count]) => {
        html += `<div class="trend-item">${category}: ${count} articles</div>`;
    });
    
    html += '<h4>Sentiment Distribution:</h4>';
    Object.entries(data.sentiment_distribution).forEach(([sentiment, count]) => {
        html += `<div class="trend-item">${sentiment}: ${count} articles</div>`;
    });
    
    resultsDiv.innerHTML = html;
}

async function loadKeywords() {
    if (!authToken) {
        alert('Please login to view keywords');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/analysis/keywords?days=7&limit=10`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        const data = await response.json();
        
        displayKeywords(data);
    } catch (error) {
        console.error('Error loading keywords:', error);
        alert('Failed to load keywords');
    }
}

function displayKeywords(data) {
    const resultsDiv = document.getElementById('analysisResults');
    
    let html = '<h3>🔥 Trending Keywords (Last 7 Days)</h3>';
    html += `<p><strong>Articles Analyzed:</strong> ${data.total_articles_analyzed}</p>`;
    
    html += '<div class="trend-item">';
    data.keywords.forEach((item, index) => {
        html += `<span style="display: inline-block; margin: 5px; padding: 5px 10px; background: #667eea; color: white; border-radius: 15px;">
            ${index + 1}. ${item.keyword} (${item.count})
        </span>`;
    });
    html += '</div>';
    
    resultsDiv.innerHTML = html;
}

// Utility Functions
function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    if (show) {
        spinner.classList.remove('hidden');
    } else {
        spinner.classList.add('hidden');
    }
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

function hideError() {
    document.getElementById('errorMessage').classList.add('hidden');
}
