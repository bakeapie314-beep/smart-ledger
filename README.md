The Smart Ledger solves the problem of information overload in financial news. Instead of scrolling through dozens of articles across multiple sites, users get AI-generated summaries that identify key themes and trends across five major categories: Finance, Investing, Accounting, Cybersecurity, and World News.The platform features:

Real-time news aggregation from NewsAPI
AI-powered content summarization analyzing 50+ financial keywords
Live stock price tracking with interactive charts
Responsive, accessible design with dark/light themes
Auto-refreshing content every 5-10 minutes

Features
News Aggregation

5 News Categories: Finance, Investing, Accounting, Cybersecurity, World News
Real-time Updates: Content refreshes every 5-10 minutes
Smart Filtering: Validates articles, removes spam, ensures quality content
Source Attribution: Clear citations from Bloomberg, Reuters, WSJ, and more

AI-Powered Summaries

Contextual Analysis: Scans articles for 50+ category-specific keywords
Theme Identification: Identifies trending topics and key developments
Intelligent Synthesis: Generates coherent paragraphs linking multiple stories
Time-Stamped: Shows exactly when summaries were last updated

Stock Market Data

Live Ticker: Displays 8 major stock symbols with real-time prices
Interactive Charts: Chart.js visualizations showing 30-day price history
Change Indicators: Color-coded positive/negative price movements
Detailed Modals: Click any stock for full details (price, volume, market cap)

User Experience

Responsive Design: Optimized for mobile, tablet, and desktop
Dark/Light Themes: Persistent theme selection with localStorage
Accessibility: WCAG 2.1 AA compliant with ARIA labels, keyboard navigation, screen reader support
Reading Time: Automatic calculation for each article
Smooth Animations: CSS animations with reduced-motion support

🛠️ Tech Stack
Backend

Python 3.11
Flask 3.0.0 - Web framework
Flask-CORS - Cross-origin resource sharing
Requests - HTTP library for API calls
yfinance - Yahoo Finance API wrapper

Frontend

HTML5/CSS3 - Semantic markup and modern styling
JavaScript (ES6+) - Async/await, Promises, DOM manipulation
Chart.js 3.9.1 - Interactive stock price visualizations
Google Fonts - Space Grotesk, Inter, Merriweather

APIs

NewsAPI - News article aggregation
Yahoo Finance - Stock price data

Deployment

Render - Backend (Web Service) and Frontend (Static Site)
UptimeRobot - Backend monitoring and keep-alive

📦 Installation
Prerequisites

Python 3.11 or higher
pip (Python package manager)
NewsAPI key (free at newsapi.org)

Clone the Repository
bashgit clone https://github.com/bakeapie314-beep/smart-ledger.git
cd smart-ledger
Backend Setup

Navigate to backend directory:

bashcd backend

Create virtual environment:

bashpython -m venv venv
source venv/bin/activate  # On Mac/Linux
# OR
venv\Scripts\activate  # On Windows

Install dependencies:

bashpip install -r requirements.txt

Create .env file in backend directory:

bashNEWS_API_KEY=your_newsapi_key_here

Run the backend:

bashpython app.py
Backend will start on http://localhost:5001
Frontend Setup

Navigate to frontend directory:

bashcd ../frontend

Open index.html in your browser, or use a local server:

bash# Python 3
python -m http.server 8000

# Then visit http://localhost:8000

🚀 Usage
Running Locally

Start the backend (in backend directory):

bashpython app.py

Open frontend (in frontend directory):


Double-click index.html, or
Use a local server: python -m http.server 8000


Navigate between news categories using the top navigation tabs
Click stock tickers to view detailed charts and metrics
Toggle theme using the moon/sun button (top right)

API Endpoints
The backend exposes several REST endpoints:
GET  /                           - Health check
GET  /api/news/<category>        - Get news for specific category
GET  /api/stocks                 - Get current stock data
GET  /api/chart/<symbol>         - Get historical chart data for stock
GET  /api/refresh/<category>     - Force refresh news cache
GET  /api/debug                  - API status and debug info
Example Request:
bashcurl http://localhost:5001/api/news/finance
Example Response:
json{
  "articles": [...],
  "summary": "Today's finance news on October 8, 2025 centers on...",
  "last_updated": "2025-10-08T14:30:00",
  "total_found": 6,
  "category": "finance"
}

🔑 API Configuration
NewsAPI Setup

Sign up for free at newsapi.org
Copy your API key
Add to .env file: NEWS_API_KEY=your_key_here

Rate Limits (Free Tier):

100 requests per day
Historical data up to 1 month

Yahoo Finance
No API key required. Uses the yfinance library which scrapes Yahoo Finance data. Note that Yahoo Finance may rate-limit requests from cloud servers.

🌐 Deployment
Deploy to Render
Backend Deployment

Push code to GitHub
Create new Web Service on Render
Configure:

Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: python app.py
Environment Variable: NEWS_API_KEY=your_key



Frontend Deployment

Create new Static Site on Render
Configure:

Root Directory: frontend
Build Command: (leave empty)
Publish Directory: .


Update index.html with backend URL:

javascriptBASE_URL: 'https://your-backend-name.onrender.com'
Keep Backend Awake
Free tier backends sleep after 15 minutes. Use UptimeRobot to ping your backend every 5 minutes:

Sign up at uptimerobot.com
Add new monitor with your backend URL
Set interval to 5 minutes


📁 Project Structure
smart-ledger/
├── backend/
│   ├── app.py              # Flask application and API endpoints
│   ├── requirements.txt    # Python dependencies
│   └── runtime.txt         # Python version specification
│
├── frontend/
│   └── index.html          # Single-page application (HTML/CSS/JS)
│
└── README.md
Key Components
Backend (app.py):

NewsAPIService class - Handles all news and stock operations
fetch_news_from_api() - Queries NewsAPI with retry logic
generate_ai_summary() - AI-powered summarization engine
get_stock_data() - Fetches live stock prices
Flask routes for REST API

Frontend (index.html):

Responsive newspaper-style layout
JavaScript modules for API communication
Chart.js integration for visualizations
Accessibility features (ARIA, keyboard nav)
Theme management system


⚠️ Known Limitations
Free Tier Constraints
Backend Cold Start:
Render's free tier spins down after 15 minutes of inactivity. First request may take 30-60 seconds. Mitigated with UptimeRobot monitoring.
Stock Data:
Yahoo Finance API rate-limits cloud server requests. When this occurs, the app falls back to realistic simulated data. The infrastructure for real-time data is fully functional—it's a free-tier API limitation, not a code issue.
NewsAPI Rate Limits:
Free tier allows 100 requests/day. Smart caching (10-minute intervals) keeps usage well within limits for typical portfolio traffic.
Browser Compatibility
Tested and working on:

✅ Chrome 90+
✅ Firefox 88+
✅ Safari 14+
✅ Edge 90+


🔮 Future Enhancements

 User authentication and personalized feeds
 Save favorite articles
 Email newsletter subscriptions
 Custom price alerts
 Portfolio tracking
 Mobile app (React Native)
 Paid API integration for guaranteed real-time data
 Multi-language support
 Advanced filtering options
 Social sharing features


🤝 Contributing
Contributions, issues, and feature requests are welcome!

Fork the repository
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request
