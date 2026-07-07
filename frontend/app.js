// API Configuration
const API_BASE_URL = (window.location.hostname === 'localhost' || window.location.protocol === 'file:')
    ? 'http://localhost:8000/api/v1'
    : 'https://your-railway-app.railway.app/api/v1';

// State
let selectedCategories = [];
let selectedRegion = 'global';
let authToken = localStorage.getItem('authToken');
let currentUser = null;

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
    loadCategories();
    loadRegions();
    setupEventListeners();
    checkAuthStatus();
});

// Load Categories
async function loadCategories() {
    try {
        console.log('Loading categories from:', `${API_BASE_URL}/categories`);
        const response = await fetch(`${API_BASE_URL}/categories`);
        const data = await response.json();
        
        console.log('Categories data:', data);
        
        const categoryGrid = document.getElementById('categoryGrid');
        if (!categoryGrid) {
            console.error('categoryGrid element not found!');
            return;
        }
        categoryGrid.innerHTML = '';
        
        // Handle both array response and object with categories property
        const categories = Array.isArray(data) ? data : (data.categories || []);
        
        categories.forEach(category => {
            const categoryItem = document.createElement('div');
            categoryItem.className = 'category-item';
            categoryItem.dataset.category = category;
            categoryItem.innerHTML = `
                <div class="icon">${categoryIcons[category] || '📰'}</div>
                <div class="name">${category.charAt(0).toUpperCase() + category.slice(1)}</div>
            `;
            categoryItem.addEventListener('click', () => toggleCategory(category, categoryItem));
            categoryGrid.appendChild(categoryItem);
        });
        
        console.log('Categories rendered successfully');
    } catch (error) {
        console.error('Error loading categories:', error);
        showError('Failed to load categories');
    }
}

// Load Regions
async function loadRegions() {
    try {
        console.log('Loading regions from:', `${API_BASE_URL}/regions`);
        const response = await fetch(`${API_BASE_URL}/regions`);
        const data = await response.json();
        
        console.log('Regions data:', data);
        
        const regionGrid = document.getElementById('regionGrid');
        if (!regionGrid) {
            console.error('regionGrid element not found!');
            return;
        }
        regionGrid.innerHTML = '';
        
        // Handle both array response and object with regions property
        const regions = Array.isArray(data) ? data : (data.regions || []);
        
        regions.forEach(region => {
            const regionItem = document.createElement('div');
            regionItem.className = 'region-item';
            regionItem.dataset.region = region;
            regionItem.innerHTML = `
                <div class="name">${region.charAt(0).toUpperCase() + region.slice(1)}</div>
            `;
            regionItem.addEventListener('click', () => selectRegion(region, regionItem));
            regionGrid.appendChild(regionItem);
        });
        
        // Select global by default
        const globalItem = regionGrid.querySelector('[data-region="global"]');
        if (globalItem) {
            selectRegion('global', globalItem);
        }
        
        console.log('Regions rendered successfully');
    } catch (error) {
        console.error('Error loading regions:', error);
        showError('Failed to load regions');
    }
}

// Toggle Category Selection
function toggleCategory(category, element) {
    const index = selectedCategories.indexOf(category);
    
    if (index > -1) {
        selectedCategories.splice(index, 1);
        element.classList.remove('selected');
    } else {
        selectedCategories.push(category);
        element.classList.add('selected');
    }
    
    // Auto-load news if categories selected
    if (selectedCategories.length > 0) {
        loadNews();
    }
}

// Select Region
function selectRegion(region, element) {
    selectedRegion = region;
    
    document.querySelectorAll('.region-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    element.classList.add('selected');
    
    // Reload news with new region
    if (selectedCategories.length > 0) {
        loadNews();
    }
}

// Load News
async function loadNews() {
    if (selectedCategories.length === 0) {
        showError('Please select at least one category');
        return;
    }
    
    showLoading(true);
    hideError();
    
    try {
        const category = selectedCategories[0]; // Use first selected category
        const response = await fetch(
            `${API_BASE_URL}/news?category=${category}&region=${selectedRegion}&limit=12`
        );
        const data = await response.json();
        
        displayNews(data.articles || []);
        document.getElementById('newsTitle').textContent = 
            `${category.charAt(0).toUpperCase() + category.slice(1)} News - ${selectedRegion.toUpperCase()}`;
    } catch (error) {
        console.error('Error loading news:', error);
        showError('Failed to load news. Please try again.');
    } finally {
        showLoading(false);
    }
}

// Display News
function displayNews(articles) {
    const newsGrid = document.getElementById('newsGrid');
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

// Authentication
function checkAuthStatus() {
    if (authToken) {
        document.getElementById('loginBtn').classList.add('hidden');
        document.getElementById('registerBtn').classList.add('hidden');
        document.getElementById('logoutBtn').classList.remove('hidden');
        document.getElementById('personalizedSection').classList.remove('hidden');
        loadCurrentUser();
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
        }
    } catch (error) {
        console.error('Error loading user:', error);
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Auth buttons
    document.getElementById('loginBtn').addEventListener('click', () => openAuthModal('login'));
    document.getElementById('registerBtn').addEventListener('click', () => openAuthModal('register'));
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    // Modal close
    document.querySelector('.close').addEventListener('click', closeAuthModal);
    document.getElementById('authModal').addEventListener('click', (e) => {
        if (e.target.id === 'authModal') closeAuthModal();
    });
    
    // Auth form
    document.getElementById('authForm').addEventListener('submit', handleAuth);
    
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', loadNews);
    
    // Personalized news
    document.getElementById('loadPersonalizedBtn').addEventListener('click', loadPersonalizedNews);
    
    // Analysis buttons
    document.getElementById('trendsBtn').addEventListener('click', loadTrends);
    document.getElementById('keywordsBtn').addEventListener('click', loadKeywords);
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
