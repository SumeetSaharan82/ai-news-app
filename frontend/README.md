# AI News App - Frontend

A modern, responsive web interface for the AI News App built with vanilla HTML, CSS, and JavaScript.

## Features

### Current Features (Phase 1 & 2)
- **News Category Selection** - Interactive category grid with icons
- **Region Selection** - Filter news by geographic region
- **News Display** - Beautiful card-based news article display
- **User Authentication** - Login and registration modals
- **Personalized News** - Tailored news feed for logged-in users
- **News Analysis** - View trends and trending keywords
- **Responsive Design** - Works on desktop and mobile devices

### Planned Features (Phase 3)
- **ML Recommendations** - AI-powered article recommendations
- **Real-time Alerts** - Live news notifications
- **Social Sharing** - Share articles on social media
- **Reading History** - Track read articles
- **Bookmarks** - Save articles for later

## Getting Started

### Prerequisites
- A web browser (Chrome, Firefox, Safari, Edge)
- Backend API running on `http://localhost:8000`

### Installation

1. Ensure the backend is running:
```bash
cd /Users/sumeetsaharan/ai-news-app/ai-news-app
python3 -m backend.main
```

2. Open the frontend in your browser:
```bash
open frontend/index.html
```

Or simply double-click `frontend/index.html` in your file manager.

## Usage

### Viewing News
1. Select one or more news categories from the category grid
2. Select a region from the region grid
3. News articles will automatically load based on your selection
4. Click on any article to read the full story

### User Authentication
1. Click "Register" to create a new account
2. Fill in your email, password, and name
3. Click "Login" to sign in with existing credentials
4. Once logged in, you'll see personalized news options

### Personalized News
1. Login to your account
2. Click "Load Personalized News" in the personalized section
3. News will be tailored to your preferences
4. Update your preferences via the API to customize your feed

### News Analysis
1. Login to your account
2. Click "View Trends" to see category and sentiment distribution
3. Click "Trending Keywords" to see popular topics

## File Structure

```
frontend/
├── index.html      # Main HTML structure
├── styles.css      # Styling and responsive design
├── app.js          # Application logic and API integration
└── README.md       # This file
```

## API Integration

The frontend connects to the backend API at `http://localhost:8000/api/v1`:

### Endpoints Used
- `GET /categories` - Load available categories
- `GET /regions` - Load available regions
- `GET /news` - Fetch news by category and region
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info
- `GET /news/personalized` - Get personalized news
- `GET /analysis/trends` - Get news trends
- `GET /analysis/keywords` - Get trending keywords

## Customization

### Changing API URL
Edit `app.js` line 3:
```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

### Adding Categories
Edit `app.js` lines 8-17 to add more category icons:
```javascript
const categoryIcons = {
    'general': '📰',
    'technology': '💻',
    // Add more categories here
};
```

### Styling
Edit `styles.css` to customize colors, fonts, and layout.

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Mobile Support

The frontend is fully responsive and works on:
- iOS Safari
- Chrome Mobile
- Firefox Mobile
- Samsung Internet

## Development

### Adding New Features

1. **Add UI elements** to `index.html`
2. **Add styles** to `styles.css`
3. **Add logic** to `app.js`
4. **Connect to API** using the existing pattern

### Example: Adding a New API Call

```javascript
async function loadNewFeature() {
    try {
        const response = await fetch(`${API_BASE_URL}/new-endpoint`);
        const data = await response.json();
        // Process data
    } catch (error) {
        console.error('Error:', error);
    }
}
```

## Phase 3 Preparation

### ML Recommendations Architecture
The frontend is prepared for ML recommendations:
- User reading history tracking (to be implemented)
- Preference-based filtering (already in place)
- Recommendation API endpoint (to be added in backend)

### Real-time Alerts Architecture
The frontend is prepared for real-time alerts:
- WebSocket support (to be implemented)
- Push notification API (to be added)
- Alert UI components (to be designed)

## Troubleshooting

### News not loading
- Ensure backend is running on port 8000
- Check browser console for errors
- Verify API URL in `app.js`

### Authentication not working
- Check that user is registered in the database
- Verify JWT token is stored in localStorage
- Check backend logs for authentication errors

### Styling issues
- Clear browser cache
- Check that `styles.css` is linked in `index.html`
- Verify CSS file path

## Performance

The frontend uses:
- Lazy loading for images
- Efficient DOM manipulation
- Minimal external dependencies
- Optimized CSS with transitions

## Security

- JWT tokens stored in localStorage
- HTTPS recommended for production
- Input validation on forms
- XSS protection through proper escaping

## Future Enhancements

- [ ] PWA support for offline access
- [ ] Dark mode toggle
- [ ] Article bookmarking
- [ ] Reading history
- [ ] Social sharing buttons
- [ ] Search functionality
- [ ] Filter by date range
- [ ] Save search queries
