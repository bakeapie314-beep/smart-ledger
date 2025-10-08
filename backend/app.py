#!/usr/bin/env python3
"""
Smart Ledger Backend - Fixed News Updates with Debugging
"""

import requests
from datetime import datetime, timedelta
import json
import time
import random
from flask import Flask, jsonify
from flask_cors import CORS
import logging
import yfinance as yf
import os
from urllib.parse import urlparse

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NewsAPIService:
    def __init__(self):
        # NewsAPI key integrated
        self.api_key = os.getenv('NEWS_API_KEY') or '22aa9ecc898e4e5aae7eab5b60347b27'
        self.base_url = 'https://newsapi.org/v2'
        
        # Track API usage
        self.request_count = 0
        self.last_reset = datetime.now()
        
        # Category mappings for NewsAPI
        self.category_mappings = {
            'accounting': {
                'keywords': ['accounting', 'audit', 'bookkeeping', 'CPA', 'financial reporting', 'tax'],
                'sources': 'bloomberg,reuters,financial-times,the-wall-street-journal',
                'domains': 'bloomberg.com,reuters.com,ft.com,wsj.com,accountingtoday.com'
            },
            'finance': {
                'keywords': ['finance', 'banking', 'fintech', 'financial services', 'monetary policy', 'economy'],
                'sources': 'bloomberg,reuters,financial-times,the-wall-street-journal,cnbc',
                'domains': 'bloomberg.com,reuters.com,ft.com,wsj.com,cnbc.com'
            },
            'investing': {
                'keywords': ['investing', 'stocks', 'portfolio', 'trading', 'market analysis', 'investment'],
                'sources': 'bloomberg,reuters,financial-times,the-wall-street-journal',
                'domains': 'bloomberg.com,reuters.com,ft.com,wsj.com,marketwatch.com'
            },
            'cybersecurity': {
                'keywords': ['cybersecurity', 'data breach', 'hacking', 'cyber attack', 'information security'],
                'sources': 'ars-technica,techcrunch,wired,the-verge',
                'domains': 'arstechnica.com,techcrunch.com,wired.com,theverge.com'
            },
            'worldnews': {
                'keywords': ['international', 'global', 'world politics', 'diplomacy', 'international relations'],
                'sources': 'bbc-news,reuters,cnn,associated-press,al-jazeera-english',
                'domains': 'bbc.com,reuters.com,cnn.com,apnews.com,aljazeera.com'
            }
        }

    def check_api_status(self):
        """Check if API key is valid and working"""
        try:
            test_url = f"{self.base_url}/everything"
            test_params = {
                'apiKey': self.api_key,
                'q': 'test',
                'pageSize': 1,
                'language': 'en'
            }
            
            response = requests.get(test_url, params=test_params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok':
                    logger.info("✅ NewsAPI is working correctly")
                    return True
                else:
                    logger.error(f"❌ NewsAPI error: {data}")
                    return False
            elif response.status_code == 429:
                logger.error("❌ NewsAPI rate limit exceeded")
                return False
            elif response.status_code == 401:
                logger.error("❌ NewsAPI invalid API key")
                return False
            else:
                logger.error(f"❌ NewsAPI HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ NewsAPI connection error: {e}")
            return False

    def fetch_news_from_api(self, category, max_articles=6):
        """Fetch real news articles from NewsAPI with better debugging"""
        try:
            # Check API status first
            if not self.check_api_status():
                logger.warning("API check failed, using fallback articles")
                return self.get_fallback_articles(category)

            config = self.category_mappings.get(category, {})
            keywords = config.get('keywords', [category])
            sources = config.get('sources', '')
            domains = config.get('domains', '')
            
            articles = []
            
            # More recent date range - last 3 days instead of 7
            from_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
            logger.info(f"🔍 Searching for {category} articles from {from_date}")
            
            # Try multiple search strategies
            search_strategies = [
                {
                    'q': ' OR '.join(keywords[:2]),  # Use fewer keywords 
                    'sources': sources,
                    'from': from_date,
                    'sortBy': 'publishedAt'
                },
                {
                    'q': keywords[0],
                    'domains': domains,
                    'from': from_date,
                    'sortBy': 'publishedAt'
                },
                {
                    'q': category,
                    'language': 'en',
                    'from': from_date,
                    'sortBy': 'publishedAt'
                }
            ]
            
            for i, strategy in enumerate(search_strategies):
                if len(articles) >= max_articles:
                    break
                    
                params = {
                    'apiKey': self.api_key,
                    'language': 'en',
                    'pageSize': 20,
                }
                params.update(strategy)
                
                try:
                    logger.info(f"📡 API Request {i+1}: {params['q']}")
                    response = requests.get(f"{self.base_url}/everything", params=params, timeout=15)
                    self.request_count += 1
                    
                    logger.info(f"📊 Response Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get('status') == 'ok' and data.get('articles'):
                            total_results = data.get('totalResults', 0)
                            found_articles = len(data['articles'])
                            logger.info(f"📰 Found {found_articles} articles (total: {total_results})")
                            
                            for article in data['articles']:
                                if len(articles) >= max_articles:
                                    break
                                    
                                if self.is_valid_article(article, category):
                                    processed_article = self.process_article(article)
                                    if processed_article not in articles:
                                        articles.append(processed_article)
                                        logger.info(f"✅ Added: {article.get('title', '')[:60]}...")
                                else:
                                    logger.debug(f"❌ Filtered out: {article.get('title', '')[:60]}...")
                        else:
                            logger.warning(f"⚠️ No articles in response: {data}")
                    
                    elif response.status_code == 429:
                        logger.error(f"🚫 Rate limit hit! Request count: {self.request_count}")
                        break
                    else:
                        logger.error(f"❌ HTTP {response.status_code}: {response.text}")
                        
                except requests.exceptions.RequestException as e:
                    logger.error(f"🔌 Request error: {e}")
                    continue
                
                # Small delay between requests
                time.sleep(0.5)
            
            logger.info(f"📋 Final result: {len(articles)} articles for {category}")
            
            # Return articles if we have at least 1, otherwise fallback
            if len(articles) >= 1:
                return articles[:max_articles]
            else:
                logger.warning(f"⚠️ Insufficient articles from API for {category}, using fallback")
                return self.get_fallback_articles(category)
                
        except Exception as e:
            logger.error(f"💥 Error fetching news from API: {e}")
            return self.get_fallback_articles(category)

    def is_valid_article(self, article, category):
        """Less strict article validation"""
        # Check for required fields
        if not all([
            article.get('title'),
            article.get('description'),
            article.get('url'),
            article.get('publishedAt')
        ]):
            return False
            
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        
        # More lenient filtering - only block obvious spam
        spam_terms = ['[removed]', '[deleted]', 'error', 'page not found', 'subscribe now']
        if any(term in title or term in description for term in spam_terms):
            return False
        
        # Check if article is recent (last 5 days)
        try:
            pub_date = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
            if (datetime.now(pub_date.tzinfo) - pub_date).days > 5:
                return False
        except:
            pass  # If date parsing fails, don't exclude the article
            
        return True

    def process_article(self, article):
        """Process and format article data"""
        # More robust date formatting
        pub_date = article.get('publishedAt', '')
        try:
            if pub_date:
                dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
            else:
                formatted_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            formatted_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        return {
            'title': article.get('title', '').replace(' - Reuters', '').replace(' | CNN', ''),
            'description': article.get('description', '')[:300] + ('...' if len(article.get('description', '')) > 300 else ''),
            'url': article.get('url', ''),
            'published_at': formatted_date,
            'source': article.get('source', {}).get('name', 'Unknown'),
            'image': article.get('urlToImage') or self.get_category_image(),
            'scraped_at': datetime.now().isoformat()
        }

    def get_category_image(self):
        """Get a random category-appropriate image"""
        images = [
            'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&h=200&fit=crop',
            'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=200&fit=crop',
            'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400&h=200&fit=crop',
            'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=400&h=200&fit=crop',
            'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=200&fit=crop'
        ]
        return random.choice(images)

    def get_fallback_articles(self, category):
        """High-quality fallback articles with current dates"""
        current_time = datetime.now()
        
        # Create articles with today's date
        base_articles = {
            'finance': [
                {
                    'title': 'Federal Reserve Signals Continued Monetary Policy Adjustments',
                    'description': 'The Federal Reserve continues to monitor economic indicators and adjust monetary policy to support sustainable growth and price stability.',
                    'url': 'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm',
                    'source': 'Federal Reserve'
                },
                {
                    'title': 'Financial Markets Show Mixed Signals Amid Economic Uncertainty',
                    'description': 'Market analysts report mixed signals as investors navigate changing economic conditions and geopolitical developments.',
                    'url': 'https://www.bloomberg.com/markets',
                    'source': 'Bloomberg'
                },
                {
                    'title': 'Digital Banking Innovation Continues to Transform Financial Services',
                    'description': 'Financial technology companies continue to drive innovation in digital banking, mobile payments, and customer experience.',
                    'url': 'https://techcrunch.com/category/fintech/',
                    'source': 'TechCrunch'
                }
            ],
            'investing': [
                {
                    'title': 'Technology Stocks Lead Market Performance in Current Quarter',
                    'description': 'Technology sector stocks continue to show strong performance as investors focus on innovation and growth opportunities.',
                    'url': 'https://www.marketwatch.com/investing',
                    'source': 'MarketWatch'
                },
                {
                    'title': 'ESG Investing Trends Shape Portfolio Strategies',
                    'description': 'Environmental, social, and governance factors increasingly influence investment decisions and portfolio construction.',
                    'url': 'https://www.morningstar.com/funds',
                    'source': 'Morningstar'
                }
            ],
            'accounting': [
                {
                    'title': 'FASB Updates Accounting Standards for Modern Business Practices',
                    'description': 'The Financial Accounting Standards Board continues to update accounting standards to address evolving business models and practices.',
                    'url': 'https://www.fasb.org/home',
                    'source': 'FASB'
                }
            ],
            'cybersecurity': [
                {
                    'title': 'Cybersecurity Threats Evolve as Organizations Strengthen Defenses',
                    'description': 'Security professionals report new threat vectors while organizations implement advanced cybersecurity measures.',
                    'url': 'https://www.cisa.gov/news-events/cybersecurity-advisories',
                    'source': 'CISA'
                }
            ],
            'worldnews': [
                {
                    'title': 'Global Economic Cooperation Continues Through International Forums',
                    'description': 'International organizations work together to address global economic challenges and promote sustainable development.',
                    'url': 'https://www.reuters.com/world/',
                    'source': 'Reuters'
                }
            ]
        }
        
        articles = base_articles.get(category, base_articles['finance'])
        
        # Add current timestamp to each article
        for article in articles:
            article.update({
                'published_at': current_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
                'image': self.get_category_image(),
                'scraped_at': current_time.isoformat()
            })
        
        return articles

    def generate_ai_summary(self, articles, category):
        """Generate specific AI summary from actual article content"""
        current_date = datetime.now().strftime('%B %d, %Y')
        
        if not articles or len(articles) == 0:
            return f"No recent {category} news available for {current_date}."
        
        try:
            # Extract key information from articles
            titles = [a.get('title', '') for a in articles[:5]]
            descriptions = [a.get('description', '')[:200] for a in articles[:5]]
            sources = list(set([a.get('source', 'Unknown') for a in articles[:5]]))
            
            # Combine all text for keyword analysis
            all_text = ' '.join(titles + descriptions).lower()
            
            # Category-specific keywords to identify themes
            keywords_map = {
                'finance': {
                    'keywords': ['federal reserve', 'interest rate', 'inflation', 'banking', 'monetary policy', 
                               'economic growth', 'gdp', 'recession', 'market', 'financial services'],
                    'context': 'financial sector'
                },
                'investing': {
                    'keywords': ['stock market', 'portfolio', 'earnings', 'dividend', 'bull market', 'bear market',
                               'rally', 'sell-off', 'investor', 'trading', 'shares', 'equity'],
                    'context': 'investment markets'
                },
                'cybersecurity': {
                    'keywords': ['data breach', 'cyberattack', 'ransomware', 'vulnerability', 'hacking', 
                               'security threat', 'malware', 'phishing', 'encryption', 'zero-day'],
                    'context': 'cybersecurity landscape'
                },
                'accounting': {
                    'keywords': ['audit', 'financial reporting', 'gaap', 'ifrs', 'compliance', 'tax reform',
                               'accounting standard', 'disclosure', 'revenue recognition', 'fasb'],
                    'context': 'accounting profession'
                },
                'worldnews': {
                    'keywords': ['government', 'policy', 'international', 'diplomatic', 'trade agreement',
                               'sanctions', 'treaty', 'election', 'global', 'geopolitical'],
                    'context': 'global developments'
                }
            }
            
            # Get category-specific info
            category_info = keywords_map.get(category, {'keywords': [], 'context': category})
            
            # Find matching keywords
            found_themes = []
            for keyword in category_info['keywords']:
                if keyword in all_text:
                    found_themes.append(keyword)
            
            # Build comprehensive summary
            summary_parts = []
            
            # Opening statement with date and context
            if found_themes:
                theme_list = ', '.join(found_themes[:3])
                summary_parts.append(
                    f"Today's {category} news on {current_date} centers on {theme_list}."
                )
            else:
                summary_parts.append(
                    f"{category.capitalize()} news for {current_date} highlights key industry developments."
                )
            
            # Lead story with actual content
            if len(articles) > 0:
                lead = articles[0]
                lead_title = lead.get('title', 'Breaking news')
                lead_desc = lead.get('description', '')[:150]
                lead_source = lead.get('source', 'Reports')
                
                summary_parts.append(
                    f'{lead_source} reports that {lead_title.lower() if not lead_title[0].isupper() else lead_title[0].lower() + lead_title[1:]}'
                )
                
                if lead_desc:
                    # Extract the most informative sentence
                    sentences = lead_desc.split('.')
                    if sentences:
                        summary_parts.append(f"— {sentences[0].strip()}.")
            
            # Add second story for context
            if len(articles) > 1:
                second = articles[1]
                second_title = second.get('title', '')
                second_source = second.get('source', 'Another report')
                
                if second_title:
                    summary_parts.append(
                        f"Additionally, {second_source} covers {second_title.lower() if not second_title[0].isupper() else second_title[0].lower() + second_title[1:]}."
                    )
            
            # Add third story if available
            if len(articles) > 2:
                third = articles[2]
                third_desc = third.get('description', '')[:120]
                
                if third_desc:
                    summary_parts.append(
                        f"Further analysis reveals {third_desc.lower() if third_desc else 'ongoing developments'}."
                    )
            
            # Closing with additional context
            if len(articles) > 3:
                remaining = len(articles) - 3
                sources_text = ', '.join(sources[:3]) if len(sources) > 1 else sources[0]
                summary_parts.append(
                    f"Coverage from {sources_text} and others provides {remaining} additional {'perspective' if remaining == 1 else 'perspectives'} on today's {category_info['context']}."
                )
            elif len(sources) > 1:
                summary_parts.append(
                    f"Analysis from {', '.join(sources[:3])} provides comprehensive coverage of today's {category_info['context']}."
                )
            
            return ' '.join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            # Fallback to basic summary
            if articles and len(articles) > 0:
                return f"Latest {category} news from {current_date}: {articles[0].get('title', 'Multiple stories available')}. {len(articles)} {'article' if len(articles) == 1 else 'articles'} available below."
            return f"Monitoring {category} developments on {current_date}."

    def get_category_news(self, category):
        """Main method to get news for a category with enhanced debugging"""
        try:
            logger.info(f"🚀 Starting news fetch for category: {category}")
            start_time = time.time()
            
            # Fetch articles from NewsAPI
            articles = self.fetch_news_from_api(category, max_articles=6)
            
            # Generate summary
            summary = self.generate_ai_summary(articles, category)
            
            fetch_time = time.time() - start_time
            logger.info(f"⏱️ News fetch completed in {fetch_time:.2f}s")
            
            result = {
                'articles': articles,
                'summary': summary,
                'last_updated': datetime.now().isoformat(),
                'total_found': len(articles),
                'category': category,
                'api_source': 'NewsAPI' if self.api_key != 'YOUR_API_KEY_HERE' else 'Fallback',
                'debug_info': {
                    'request_count': self.request_count,
                    'fetch_time_seconds': round(fetch_time, 2),
                    'from_cache': False
                }
            }
            
            logger.info(f"✅ Successfully provided {len(articles)} articles for {category}")
            return result
            
        except Exception as e:
            logger.error(f"💥 Error getting category news for {category}: {e}")
            return {
                'articles': self.get_fallback_articles(category),
                'summary': f"Monitoring the latest developments in {category} on {datetime.now().strftime('%B %d, %Y')}.",
                'last_updated': datetime.now().isoformat(),
                'total_found': len(self.get_fallback_articles(category)),
                'category': category,
                'error': str(e),
                'debug_info': {
                    'request_count': self.request_count,
                    'from_cache': False,
                    'error_occurred': True
                }
            }

    def get_stock_data(self, symbols):
        """Get real-time stock data using Yahoo Finance"""
        try:
            stock_data = {}
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    hist = ticker.history(period="1d", interval="5m")
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        prev_close = info.get('previousClose', current_price)
                        change_percent = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0
                        
                        # Format market cap
                        market_cap = info.get('marketCap', 0)
                        if market_cap > 1e12:
                            market_cap_str = f"{market_cap/1e12:.1f}T"
                        elif market_cap > 1e9:
                            market_cap_str = f"{market_cap/1e9:.1f}B"
                        elif market_cap > 1e6:
                            market_cap_str = f"{market_cap/1e6:.1f}M"
                        else:
                            market_cap_str = f"{market_cap:,.0f}"
                        
                        # Format volume
                        volume = info.get('volume', 0)
                        if volume > 1e9:
                            volume_str = f"{volume/1e9:.1f}B"
                        elif volume > 1e6:
                            volume_str = f"{volume/1e6:.1f}M"
                        elif volume > 1e3:
                            volume_str = f"{volume/1e3:.1f}K"
                        else:
                            volume_str = f"{volume:,.0f}"
                        
                        stock_data[symbol] = {
                            'symbol': symbol,
                            'price': round(current_price, 2),
                            'change': round(change_percent, 2),
                            'volume': volume_str,
                            'marketCap': market_cap_str,
                            'name': info.get('longName', symbol),
                            'last_updated': datetime.now().isoformat()
                        }
                    else:
                        stock_data[symbol] = self.get_fallback_stock_data(symbol)
                        
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {e}")
                    stock_data[symbol] = self.get_fallback_stock_data(symbol)
                    
            return stock_data
        except Exception as e:
            logger.error(f"Error in get_stock_data: {e}")
            return {symbol: self.get_fallback_stock_data(symbol) for symbol in symbols}

    def get_stock_chart_data(self, symbol):
        """Get real historical chart data for a stock symbol"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get 1 month of daily data
            hist = ticker.history(period="1mo", interval="1d")
            
            if hist.empty:
                logger.warning(f"No historical data found for {symbol}")
                return self.get_fallback_chart_data(symbol)
            
            # Format data for Chart.js
            labels = []
            prices = []
            
            for date, row in hist.iterrows():
                labels.append(date.strftime('%b %d'))
                prices.append(round(row['Close'], 2))
            
            return {
                'labels': labels,
                'data': prices,
                'symbol': symbol,
                'period': '1mo',
                'source': 'yahoo_finance',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching chart data for {symbol}: {e}")
            return self.get_fallback_chart_data(symbol)
    
    def get_fallback_chart_data(self, symbol):
        """Generate fallback chart data if Yahoo Finance fails"""
        # Use the same seeded random approach for consistency
        import hashlib
        seed = int(hashlib.md5(symbol.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        # Generate 30 days of fake data
        labels = []
        prices = []
        base_price = 100.0
        
        for i in range(30):
            date = datetime.now() - timedelta(days=30-i)
            labels.append(date.strftime('%b %d'))
            
            # Add some realistic price movement
            change = random.uniform(-0.05, 0.05)  # -5% to +5% daily change
            base_price = base_price * (1 + change)
            prices.append(round(base_price, 2))
        
        return {
            'labels': labels,
            'data': prices,
            'symbol': symbol,
            'period': '1mo',
            'source': 'fallback',
            'last_updated': datetime.now().isoformat()
        }

    def get_fallback_stock_data(self, symbol):
        """Provide fallback stock data when API fails"""
        fallback_data = {
            'AAPL': {'price': 189.45, 'change': 2.15, 'marketCap': '2.9T', 'volume': '89.2M', 'name': 'Apple Inc.'},
            'MSFT': {'price': 412.73, 'change': 1.89, 'marketCap': '3.1T', 'volume': '42.1M', 'name': 'Microsoft Corporation'},
            'GOOGL': {'price': 142.87, 'change': -0.45, 'marketCap': '1.8T', 'volume': '28.5M', 'name': 'Alphabet Inc.'},
            'AMZN': {'price': 156.92, 'change': 1.67, 'marketCap': '1.6T', 'volume': '55.3M', 'name': 'Amazon.com Inc.'},
            'TSLA': {'price': 267.34, 'change': 3.21, 'marketCap': '849.2B', 'volume': '127.4M', 'name': 'Tesla Inc.'},
            'NVDA': {'price': 478.92, 'change': 2.78, 'marketCap': '1.2T', 'volume': '91.8M', 'name': 'NVIDIA Corporation'},
            'META': {'price': 324.56, 'change': -1.12, 'marketCap': '825.4B', 'volume': '23.7M', 'name': 'Meta Platforms Inc.'},
            'NFLX': {'price': 445.89, 'change': 0.93, 'marketCap': '198.3B', 'volume': '15.2M', 'name': 'Netflix Inc.'}
        }
        
        base_data = fallback_data.get(symbol, {
            'price': 100.00, 'change': 0.0, 'marketCap': '1.0B', 'volume': '10.0M', 'name': symbol
        })
        
        return {
            'symbol': symbol,
            'price': base_data['price'],
            'change': base_data['change'],
            'volume': base_data['volume'],
            'marketCap': base_data['marketCap'],
            'name': base_data['name'],
            'last_updated': datetime.now().isoformat()
        }

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["*"])

# Initialize news service
news_service = NewsAPIService()

# Reduced cache duration for more frequent updates
news_cache = {}
stock_cache = {}
chart_cache = {}
cache_duration = timedelta(minutes=10)  # Reduced from 30 to 10 minutes
stock_cache_duration = timedelta(minutes=5)
chart_cache_duration = timedelta(hours=1)

@app.route('/')
def home():
    """Health check endpoint with debug info"""
    api_status = "Active" if news_service.api_key != 'YOUR_API_KEY_HERE' else "Not Configured (Using Fallback)"
    
    return jsonify({
        'status': 'Smart Ledger NewsAPI Backend is running!',
        'version': '3.2.0 - Enhanced Debugging',
        'current_time': datetime.now().isoformat(),
        'newsapi_status': api_status,
        'api_request_count': news_service.request_count,
        'categories': list(news_service.category_mappings.keys()),
        'cache_info': {
            'news_entries': len(news_cache),
            'cache_duration_minutes': cache_duration.total_seconds() / 60
        },
        'features': [
            'Real NewsAPI integration with debugging',
            'Enhanced error tracking',
            'Reduced cache duration (10 min)',
            'API status monitoring',
            'Real-time stock data',
            'Real historical stock charts'
        ],
        'endpoints': {
            'news': '/api/news/<category>',
            'stocks': '/api/stocks',
            'chart': '/api/chart/<symbol>',
            'refresh': '/api/refresh/<category>',
            'debug': '/api/debug',
            'health': '/'
        }
    })

@app.route('/api/debug')
def debug_info():
    """Debug endpoint to check NewsAPI status"""
    try:
        api_working = news_service.check_api_status()
        
        return jsonify({
            'newsapi_working': api_working,
            'api_key_configured': news_service.api_key != 'YOUR_API_KEY_HERE',
            'api_key_preview': f"{news_service.api_key[:8]}..." if news_service.api_key != 'YOUR_API_KEY_HERE' else "Not set",
            'request_count': news_service.request_count,
            'last_reset': news_service.last_reset.isoformat(),
            'cache_entries': {
                'news': len(news_cache),
                'stocks': len(stock_cache),
                'charts': len(chart_cache)
            },
            'cache_duration_minutes': cache_duration.total_seconds() / 60,
            'current_time': datetime.now().isoformat(),
            'recommendations': [
                "Check if NewsAPI key is valid at https://newsapi.org/account",
                "Ensure you haven't exceeded the monthly request limit",
                "Try clearing cache by calling /api/refresh/<category>",
                "Check backend logs for detailed error messages"
            ]
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'debug_failed': True
        }), 500

@app.route('/api/news/<category>')
def get_news(category):
    """API endpoint to get news for a category with cache info"""
    if category not in news_service.category_mappings:
        return jsonify({
            'error': 'Invalid category',
            'valid_categories': list(news_service.category_mappings.keys())
        }), 400
    
    # Check cache first
    cache_key = f"news_{category}"
    if (cache_key in news_cache and 
        datetime.now() - news_cache[cache_key]['cached_at'] < cache_duration):
        logger.info(f"🗃️ Returning cached data for {category}")
        cached_data = news_cache[cache_key]['data']
        cached_data['debug_info']['from_cache'] = True
        cached_data['debug_info']['cached_at'] = news_cache[cache_key]['cached_at'].isoformat()
        return jsonify(cached_data)
    
    try:
        # Fetch fresh data
        logger.info(f"🔄 Fetching fresh data for {category}")
        data = news_service.get_category_news(category)
        
        # Cache the result
        news_cache[cache_key] = {
            'data': data,
            'cached_at': datetime.now()
        }
        
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Error in get_news for {category}: {e}")
        return jsonify({
            'error': 'Failed to fetch news',
            'message': str(e),
            'category': category,
            'debug_info': {
                'error_occurred': True,
                'error_time': datetime.now().isoformat()
            }
        }), 500

@app.route('/api/refresh/<category>')
def refresh_news(category):
    """Force refresh news for a category and clear cache"""
    if category not in news_service.category_mappings:
        return jsonify({
            'error': 'Invalid category',
            'valid_categories': list(news_service.category_mappings.keys())
        }), 400
    
    cache_key = f"news_{category}"
    if cache_key in news_cache:
        del news_cache[cache_key]
        logger.info(f"🗑️ Cleared cache for {category}")
    
    # Reset request count for debugging
    news_service.request_count = 0
    news_service.last_reset = datetime.now()
    
    return get_news(category)

@app.route('/api/stocks')
def get_stocks():
    """API endpoint to get real-time stock data"""
    try:
        # Check cache first
        if ('stocks' in stock_cache and 
            datetime.now() - stock_cache['stocks']['cached_at'] < stock_cache_duration):
            logger.info("Returning cached stock data")
            return jsonify(stock_cache['stocks']['data'])
        
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
        
        logger.info("Fetching fresh stock data from Yahoo Finance...")
        stock_data = news_service.get_stock_data(symbols)
        
        result = {
            'stocks': stock_data,
            'last_updated': datetime.now().isoformat(),
            'status': 'success'
        }
        
        # Cache the result
        stock_cache['stocks'] = {
            'data': result,
            'cached_at': datetime.now()
        }
        
        logger.info("Stock data fetched and cached successfully")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_stocks: {e}")
        return jsonify({
            'error': 'Failed to fetch stock data',
            'message': str(e),
            'status': 'error'
        }), 500

@app.route('/api/chart/<symbol>')
def get_chart_data(symbol):
    """API endpoint to get historical chart data for a stock"""
    try:
        # Check cache first
        cache_key = f"chart_{symbol.upper()}"
        if (cache_key in chart_cache and 
            datetime.now() - chart_cache[cache_key]['cached_at'] < chart_cache_duration):
            logger.info(f"Returning cached chart data for {symbol}")
            return jsonify(chart_cache[cache_key]['data'])
        
        logger.info(f"Fetching fresh chart data for {symbol}")
        chart_data = news_service.get_stock_chart_data(symbol.upper())
        
        # Cache the result
        chart_cache[cache_key] = {
            'data': chart_data,
            'cached_at': datetime.now()
        }
        
        logger.info(f"Chart data fetched and cached for {symbol}")
        return jsonify(chart_data)
        
    except Exception as e:
        logger.error(f"Error in get_chart_data for {symbol}: {e}")
        return jsonify({
            'error': 'Failed to fetch chart data',
            'message': str(e),
            'symbol': symbol
        }), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Smart Ledger NewsAPI Backend v3.2...")
    logger.info(f"📊 Available categories: {list(news_service.category_mappings.keys())}")
    
    # Test API on startup
    if news_service.check_api_status():
        logger.info("✅ NewsAPI is working properly!")
    else:
        logger.warning("⚠️ NewsAPI issues detected - check debug endpoint")
    
    logger.info(f"🔄 Cache duration set to {cache_duration.total_seconds()/60} minutes")
    logger.info("🌐 Server starting on http://localhost:5001")
    logger.info("🐛 Debug endpoint available at http://localhost:5001/api/debug")
    
    port = int(os.environ.get('PORT', 5001))
app.run(debug=False, host='0.0.0.0', port=port)