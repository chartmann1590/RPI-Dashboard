from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import sqlite3
import subprocess
import threading
import time
from datetime import datetime, timedelta
import pytz
import logging
import requests
from functools import wraps
import random
import feedparser
import json
import re
from urllib.parse import urlparse
import math
from dotenv import load_dotenv
import hmac
import hashlib
import base64

# Load environment variables from .env file
load_dotenv()

# Try to import holidays library, fallback to manual detection if not available
try:
    import holidays
    HOLIDAYS_AVAILABLE = True
except ImportError:
    HOLIDAYS_AVAILABLE = False
    logging.warning("holidays library not installed. Install with: pip install holidays")

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration - Load from environment variables
GOTIFY_URL = os.getenv('GOTIFY_URL', 'https://services.charleshartmann.com/gotify/message')
GOTIFY_TOKEN = os.getenv('GOTIFY_TOKEN', '')

# Weather API (OpenWeatherMap - free tier)
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
WEATHER_CITY = os.getenv('WEATHER_CITY', 'Rotterdam,NY,US')
WEATHER_LAT = os.getenv('WEATHER_LAT', '42.7809')
WEATHER_LON = os.getenv('WEATHER_LON', '-74.5388')
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
WEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# News API (NewsAPI - free tier)
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
NEWS_API_URL = "https://newsapi.org/v2/everything"  # Changed to everything endpoint for local news
NEWS_QUERY = os.getenv('NEWS_QUERY', 'Rotterdam OR Schenectady OR Albany')
NY_NEWS_QUERY = os.getenv('NY_NEWS_QUERY', 'New York')  
HEADLINES_API_URL = "https://newsapi.org/v2/top-headlines"

# Ollama AI Configuration
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://74.76.44.128:11434')
OLLAMA_FALLBACK_URL = os.getenv('OLLAMA_FALLBACK_URL', 'http://10.0.0.74:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2')

# Admin password - Load from environment variables
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '')
if not ADMIN_PASSWORD:
    logging.warning("ADMIN_PASSWORD not set in environment variables. Admin features will be disabled.")

# Cache settings
CACHE_DURATION_HOURS = 1  # How long to cache API data

# Home Assistant Configuration
HA_URL = os.getenv('HA_URL', '').rstrip('/')
HA_TOKEN = os.getenv('HA_TOKEN', '')

if not HA_URL or not HA_TOKEN:
    logging.warning("Home Assistant URL or token not found in environment variables. HA features will be disabled.")

# Timezone Configuration
TIMEZONE = os.getenv('TIMEZONE', 'America/New_York')

# SwitchBot Configuration
SWITCHBOT_TOKEN = os.getenv('SWITCHBOT_TOKEN', '')
SWITCHBOT_SECRET = os.getenv('SWITCHBOT_SECRET', '')
SWITCHBOT_LOCK_IDS = [lock_id.strip() for lock_id in os.getenv('SWITCHBOT_LOCK_IDS', '').split(',') if lock_id.strip()]

if not SWITCHBOT_TOKEN or not SWITCHBOT_SECRET or not SWITCHBOT_LOCK_IDS:
    logging.warning("SwitchBot credentials or lock IDs not found in environment variables. SwitchBot features will be disabled.")

# OpenRouteService Configuration
# Get free API key from: https://openrouteservice.org/dev/#/signup
# Free tier: 2,000 requests/day
ORS_API_KEY = os.getenv('ORS_API_KEY', '')

if not ORS_API_KEY:
    logging.warning("OpenRouteService API key not found in environment variables. ORS features will be disabled. Get a free key at https://openrouteservice.org/dev/#/signup")

# TomTom Traffic API Configuration
# Get free API key from: https://developer.tomtom.com/
# Free tier: 2,500 requests/day - PROVIDES REAL-TIME TRAFFIC DATA
TOMTOM_API_KEY = os.getenv('TOMTOM_API_KEY', '')

if not TOMTOM_API_KEY:
    logging.warning("TomTom API key not found in environment variables. Real-time traffic features will be limited. Get a free key at https://developer.tomtom.com/")

def get_timezone():
    """Get the configured timezone object"""
    return pytz.timezone(TIMEZONE)

db_path = os.path.join('static', 'db', 'network_status.db')

# Function to detect screen resolution
def get_screen_resolution():
    """
    Detect the screen resolution of the connected display.
    Returns tuple of (width, height) or None if detection fails.
    """
    try:
        # Try using fbset to get framebuffer info
        result = subprocess.run(['fbset', '-s'], capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout
            # Parse fbset output for geometry
            for line in output.split('\n'):
                if 'geometry' in line:
                    # geometry 1920 1080 1920 1080 32
                    parts = line.split()
                    if len(parts) >= 3:
                        width = int(parts[1])
                        height = int(parts[2])
                        logging.info(f"Screen resolution detected via fbset: {width}x{height}")
                        return (width, height)
    except Exception as e:
        logging.debug(f"fbset method failed: {e}")
    
    try:
        # Try using tvservice for Raspberry Pi
        result = subprocess.run(['tvservice', '-s'], capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout
            # Parse output like: state 0x120016 [DVI DMT (82) RGB full 16:9], 1920x1080 @ 60.00Hz, progressive
            match = re.search(r'(\d+)x(\d+)', output)
            if match:
                width = int(match.group(1))
                height = int(match.group(2))
                logging.info(f"Screen resolution detected via tvservice: {width}x{height}")
                return (width, height)
    except Exception as e:
        logging.debug(f"tvservice method failed: {e}")
    
    try:
        # Try reading from /sys/class/graphics/fb0/virtual_size
        with open('/sys/class/graphics/fb0/virtual_size', 'r') as f:
            size = f.read().strip()
            width, height = map(int, size.split(','))
            logging.info(f"Screen resolution detected via /sys: {width}x{height}")
            return (width, height)
    except Exception as e:
        logging.debug(f"/sys method failed: {e}")
    
    try:
        # Try xrandr if X is running
        result = subprocess.run(['xrandr'], capture_output=True, text=True, env={**os.environ, 'DISPLAY': ':0'})
        if result.returncode == 0:
            output = result.stdout
            # Look for current resolution (marked with *)
            for line in output.split('\n'):
                if '*' in line:
                    match = re.search(r'(\d+)x(\d+)', line)
                    if match:
                        width = int(match.group(1))
                        height = int(match.group(2))
                        logging.info(f"Screen resolution detected via xrandr: {width}x{height}")
                        return (width, height)
    except Exception as e:
        logging.debug(f"xrandr method failed: {e}")
    
    # Default fallback resolution
    logging.warning("Could not detect screen resolution, using default 800x480")
    return (800, 480)

# Admin authentication decorator
def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.password != ADMIN_PASSWORD:
            return 'Authentication required', 401, {'WWW-Authenticate': 'Basic realm="Admin"'}
        return f(*args, **kwargs)
    return decorated_function

def create_db(retry_count=5, delay=0.1):
    attempts = 0
    while attempts < retry_count:
        try:
            if not os.path.exists(db_path):
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                mac_address TEXT NOT NULL,
                status TEXT NOT NULL,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notify TEXT DEFAULT 'none',
                alert_shown INTEGER DEFAULT 0
            )
            ''')
            c.execute('''
            CREATE TABLE IF NOT EXISTS device_history (
                id INTEGER PRIMARY KEY,
                device_id INTEGER,
                status TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(device_id) REFERENCES devices(id)
            )
            ''')
            # Create API cache table
            c.execute('''
            CREATE TABLE IF NOT EXISTS api_cache (
                id INTEGER PRIMARY KEY,
                cache_key TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            # Create joke history table
            c.execute('''
            CREATE TABLE IF NOT EXISTS joke_history (
                id INTEGER PRIMARY KEY,
                joke_text TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            # Create settings table
            c.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            # Create calendar_feeds table
            c.execute('''
            CREATE TABLE IF NOT EXISTS calendar_feeds (
                id INTEGER PRIMARY KEY,
                name TEXT,
                url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            # Create calendar_events table
            c.execute('''
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                location TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            # Create speed_tests table
            c.execute('''
            CREATE TABLE IF NOT EXISTS speed_tests (
                id INTEGER PRIMARY KEY,
                download_mbps REAL,
                upload_mbps REAL,
                ping_ms REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            # Create quote_history table
            c.execute('''
            CREATE TABLE IF NOT EXISTS quote_history (
                id INTEGER PRIMARY KEY,
                quote_text TEXT NOT NULL,
                author TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            # Create traffic_events table
            c.execute('''
            CREATE TABLE IF NOT EXISTS traffic_events (
                id INTEGER PRIMARY KEY,
                event_type TEXT NOT NULL,
                traffic_level TEXT NOT NULL,
                location TEXT,
                description TEXT,
                latitude REAL,
                longitude REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            # Create weather_alerts table
            c.execute('''
            CREATE TABLE IF NOT EXISTS weather_alerts (
                id INTEGER PRIMARY KEY,
                alert_id TEXT UNIQUE NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                headline TEXT,
                description TEXT,
                area TEXT,
                effective TIMESTAMP,
                expires TIMESTAMP,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            # Create packages table
            c.execute('''
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY,
                tracking_number TEXT NOT NULL,
                carrier TEXT NOT NULL,
                description TEXT,
                status TEXT,
                last_location TEXT,
                estimated_delivery TIMESTAMP,
                delivered_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            # Create packages_archive table
            c.execute('''
            CREATE TABLE IF NOT EXISTS packages_archive (
                id INTEGER PRIMARY KEY,
                tracking_number TEXT NOT NULL,
                carrier TEXT NOT NULL,
                description TEXT,
                status TEXT,
                last_location TEXT,
                estimated_delivery TIMESTAMP,
                delivered_date TIMESTAMP,
                created_at TIMESTAMP,
                archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            # Create shopping_list table
            c.execute('''
            CREATE TABLE IF NOT EXISTS shopping_list (
                id INTEGER PRIMARY KEY,
                item_name TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            conn.commit()
            conn.close()
            logging.info("Database created and initialized.")
            break
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                logging.warning(f"Database is locked, retrying in {delay} seconds...")
                attempts += 1
                time.sleep(delay)
            else:
                logging.error(f"Failed to create the database: {e}")
                raise

def add_alert_shown_column():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("PRAGMA table_info(devices)")
    columns = [column[1] for column in c.fetchall()]
    
    if 'alert_shown' not in columns:
        c.execute("ALTER TABLE devices ADD COLUMN alert_shown INTEGER DEFAULT 0")
        conn.commit()
        logging.info("'alert_shown' column added to devices table.")
    conn.close()

def ensure_joke_history_table():
    """Ensure joke_history table exists"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS joke_history (
                id INTEGER PRIMARY KEY,
                joke_text TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        logging.info("Joke history table ensured.")
    except Exception as e:
        logging.error(f"Error ensuring joke_history table: {e}")

def ensure_quote_history_table():
    """Ensure quote_history table exists"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS quote_history (
                id INTEGER PRIMARY KEY,
                quote_text TEXT NOT NULL,
                author TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        logging.info("Quote history table ensured.")
    except Exception as e:
        logging.error(f"Error ensuring quote_history table: {e}")

def cleanup_crash_events():
    """Remove all crash events from database - OSRM doesn't provide crash data"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        # Delete events with crash type OR descriptions containing crash/incident keywords
        c.execute("""
            DELETE FROM traffic_events 
            WHERE event_type = 'crash' 
            OR description LIKE '%crash%' 
            OR description LIKE '%incident%'
            OR description LIKE '%accident%'
            OR description LIKE '%possible incident%'
        """)
        deleted_count = c.rowcount
        conn.commit()
        conn.close()
        if deleted_count > 0:
            logging.info(f"Cleaned up {deleted_count} crash/incident events from database (OSRM doesn't provide crash data)")
        return deleted_count
    except Exception as e:
        logging.error(f"Error cleaning up crash events: {e}")
        return 0

def save_joke_to_history(joke_text):
    """Save a joke to history and keep only the last 100 jokes"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Insert the new joke
        c.execute("INSERT INTO joke_history (joke_text) VALUES (?)", (joke_text,))
        
        # Get count of jokes
        c.execute("SELECT COUNT(*) FROM joke_history")
        count = c.fetchone()[0]
        
        # If more than 100, delete the oldest ones
        if count > 100:
            # Get IDs of jokes to keep (last 100)
            c.execute("""
                SELECT id FROM joke_history 
                ORDER BY timestamp DESC 
                LIMIT 100
            """)
            keep_ids = [row[0] for row in c.fetchall()]
            
            # Delete jokes not in the keep list
            if keep_ids:
                placeholders = ','.join('?' * len(keep_ids))
                c.execute(f"DELETE FROM joke_history WHERE id NOT IN ({placeholders})", keep_ids)
        
        conn.commit()
        conn.close()
        logging.info(f"Saved joke to history (total jokes: {min(count, 100)})")
    except Exception as e:
        logging.error(f"Error saving joke to history: {e}")

def save_quote_to_history(quote_text, author):
    """Save a quote to history and keep only the last 100 quotes"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Insert the new quote
        c.execute("INSERT INTO quote_history (quote_text, author) VALUES (?, ?)", (quote_text, author))
        
        # Get count of quotes
        c.execute("SELECT COUNT(*) FROM quote_history")
        count = c.fetchone()[0]
        
        # If more than 100, delete the oldest ones
        if count > 100:
            # Get IDs of quotes to keep (last 100)
            c.execute("""
                SELECT id FROM quote_history 
                ORDER BY timestamp DESC 
                LIMIT 100
            """)
            keep_ids = [row[0] for row in c.fetchall()]
            
            # Delete quotes not in the keep list
            if keep_ids:
                placeholders = ','.join('?' * len(keep_ids))
                c.execute(f"DELETE FROM quote_history WHERE id NOT IN ({placeholders})", keep_ids)
        
        conn.commit()
        conn.close()
        logging.info(f"Saved quote to history (total quotes: {min(count, 100)})")
    except Exception as e:
        logging.error(f"Error saving quote to history: {e}")

def get_cached_data(cache_key, max_age=None):
    """Get cached data if it's still valid
    
    Args:
        cache_key: The cache key to look up
        max_age: Optional max age in seconds (overrides CACHE_DURATION_HOURS)
    """
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Get cache entry
        c.execute("""
            SELECT data, timestamp 
            FROM api_cache 
            WHERE cache_key = ?
        """, (cache_key,))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            data, timestamp_str = result
            # Parse timestamp
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            
            # Check if cache is still valid
            if max_age is not None:
                # Use custom max_age in seconds
                if datetime.now() - timestamp < timedelta(seconds=max_age):
                    logging.info(f"Using cached data for {cache_key} (max_age={max_age}s)")
                    return json.loads(data)
                else:
                    logging.info(f"Cache expired for {cache_key} (age > {max_age}s)")
            else:
                # Use default CACHE_DURATION_HOURS
                if datetime.now() - timestamp < timedelta(hours=CACHE_DURATION_HOURS):
                    logging.info(f"Using cached data for {cache_key}")
                    return json.loads(data)
                else:
                    logging.info(f"Cache expired for {cache_key}")
        
        return None
        
    except Exception as e:
        logging.error(f"Error getting cached data: {e}")
        return None

def set_cached_data(cache_key, data):
    """Store data in cache"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        # Insert or replace cache entry
        c.execute("""
            INSERT OR REPLACE INTO api_cache (cache_key, data, timestamp)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (cache_key, json.dumps(data)))
        conn.commit()
        conn.close()
        logging.info(f"Cached data for {cache_key}")
    except Exception as e:
        logging.error(f"Error setting cached data: {e}")

@app.route('/admin/edit_device/<int:id>', methods=['GET', 'POST'])
@require_admin
def edit_device(id):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        if request.method == 'POST':
            name = request.form['name']
            ip_address = request.form['ip_address']
            mac_address = request.form['mac_address']
            c.execute('''
            UPDATE devices
            SET name = ?, ip_address = ?, mac_address = ?
            WHERE id = ?
            ''', (name, ip_address, mac_address, id))
            conn.commit()
            return redirect(url_for('admin'))
        c.execute("SELECT * FROM devices WHERE id = ?", (id,))
        device = c.fetchone()
        if not device:
            return "Device not found", 404
        return render_template('edit_device.html', device=device)

@app.route('/admin/delete_device/<int:id>')
@require_admin
def delete_device(id):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM devices WHERE id = ?", (id,))
        c.execute("DELETE FROM device_history WHERE device_id = ?", (id,))
        conn.commit()
    return redirect(url_for('admin'))

@app.route('/admin/toggle_notify/<int:id>/<action>')
@require_admin
def toggle_notify(id, action):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("UPDATE devices SET notify = ? WHERE id = ?", (action, id))
        conn.commit()
    return redirect(url_for('admin'))

@app.route('/device/<name>')
def device_history(name):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("SELECT id, notify FROM devices WHERE name = ?", (name,))
        device_info = c.fetchone()
        if not device_info:
            return "Device not found", 404
        device_id = device_info[0]
        notify_status = device_info[1]
        search_query = request.args.get('search', '')
        if search_query:
            c.execute("SELECT status, timestamp FROM device_history WHERE device_id = ? AND timestamp LIKE ? ORDER BY timestamp ASC", (device_id, f'%{search_query}%'))
        else:
            c.execute("SELECT status, timestamp FROM device_history WHERE device_id = ? ORDER BY timestamp ASC", (device_id,))
        history = c.fetchall()
    ny_tz = get_timezone()
    formatted_history = []
    for entry in history:
        status, last_seen_str = entry
        last_seen_dt = datetime.strptime(last_seen_str, '%Y-%m-%d %H:%M:%S')
        last_seen_dt = last_seen_dt.replace(tzinfo=pytz.utc).astimezone(ny_tz)
        formatted_last_seen = last_seen_dt.strftime('%Y-%m-%d %I:%M:%S %p')
        formatted_history.append((status.capitalize(), formatted_last_seen))
    return render_template('device_history.html', name=name, history=formatted_history, search_query=search_query, notify_status=notify_status, device_id=device_id)

@app.route('/rpi-dashboard')
def rpi_dashboard():
    # Get screen resolution
    width, height = get_screen_resolution()
    
    # Pass screen dimensions and timezone to template
    return render_template('rpi_dashboard.html', screen_width=width, screen_height=height, timezone=TIMEZONE)

@app.route('/api/dashboard-data')
def dashboard_data():
    """API endpoint for dashboard data with caching"""
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        
        c.execute("SELECT name, status FROM devices")
        devices = c.fetchall()
        
        # Fetch weather, forecast, news, and joke with caching
        weather = get_weather()
        forecast = get_weather_forecast()
        news = get_news()
        joke = get_joke()
        weather_alerts = get_weather_alerts()
        
        # Fetch new features
        calendar_events = get_calendar_events()
        commute = get_commute_info()
        air_quality = get_air_quality()
        quote = get_daily_quote()
        astronomy = get_astronomy_data()
        internet_speed = get_internet_speed()
        sports_scores = get_sports_scores()
        photos = get_photos()
        
        # Fetch active packages
        c.execute("""
            SELECT id, tracking_number, carrier, description, status, last_location, 
                   estimated_delivery, delivered_date, updated_at
            FROM packages
            ORDER BY created_at DESC
        """)
        packages_data = c.fetchall()
        packages = []
        for pkg in packages_data:
            packages.append({
                'id': pkg[0],
                'tracking_number': pkg[1],
                'carrier': pkg[2],
                'description': pkg[3] or '',
                'status': pkg[4] or 'Unknown',
                'last_location': pkg[5] or '',
                'estimated_delivery': pkg[6],
                'delivered_date': pkg[7],
                'updated_at': pkg[8]
            })
        
        # Fetch shopping list items
        c.execute("""
            SELECT id, item_name, completed, created_at, updated_at
            FROM shopping_list
            ORDER BY completed ASC, created_at ASC
        """)
        shopping_list_data = c.fetchall()
        shopping_list = []
        for item in shopping_list_data:
            shopping_list.append({
                'id': item[0],
                'item_name': item[1],
                'completed': bool(item[2]),
                'created_at': item[3],
                'updated_at': item[4]
            })
        
        # For RPi dashboard, select one random news article
        random_news = None
        if news and len(news) > 0:
            # Filter out error messages for random selection
            valid_news = [n for n in news if n.get('news_type') != 'Error']
            if valid_news:
                random_news = random.choice(valid_news)
            else:
                random_news = news[0]  # Use error message if no valid news
        
        # Select random photo for RPi dashboard
        random_photo = None
        if photos and len(photos) > 0:
            random_photo = random.choice(photos)
        
        # Select next two calendar events for RPi dashboard
        next_calendar_events = []
        if calendar_events and len(calendar_events) > 0:
            next_calendar_events = calendar_events[:2]  # Next 2 events
        
        # Fetch SwitchBot locks
        switchbot_locks = get_switchbot_lock_status()
        
        return jsonify({
            'devices': [{'name': d[0], 'status': d[1]} for d in devices],
            'weather': weather,
            'forecast': forecast,
            'news': news,
            'random_news': random_news,
            'joke': joke,
            'weather_alerts': weather_alerts,
            'calendar_events': calendar_events,
            'next_calendar_events': next_calendar_events,
            'commute': commute,
            'air_quality': air_quality,
            'quote': quote,
            'astronomy': astronomy,
            'internet_speed': internet_speed,
            'sports_scores': sports_scores,
            'photos': photos,
            'random_photo': random_photo,
            'packages': packages,
            'shopping_list': shopping_list,
            'switchbot_locks': switchbot_locks,
            'time': datetime.now(get_timezone()).strftime('%I:%M %p'),
            'date': datetime.now(get_timezone()).strftime('%A, %B %d'),
            'timezone': TIMEZONE,
            'weather_radar_url': f"https://radar.weather.gov/ridge/standard/KENX_loop.gif"  # Albany, NY radar
        })

@app.route('/api/joke-history')
def joke_history():
    """API endpoint to get joke history with pagination"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        
        # Ensure valid values
        page = max(1, page)
        per_page = max(1, min(per_page, 100))  # Limit per_page to 100
        
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            
            # Get total count
            c.execute("SELECT COUNT(*) FROM joke_history")
            total_count = c.fetchone()[0]
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get paginated jokes
            c.execute("""
                SELECT joke_text, timestamp 
                FROM joke_history 
                ORDER BY timestamp DESC 
                LIMIT ? OFFSET ?
            """, (per_page, offset))
            jokes = c.fetchall()
            
            # Format the jokes
            formatted_jokes = []
            ny_tz = get_timezone()
            for joke_text, timestamp_str in jokes:
                timestamp_dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                timestamp_dt = timestamp_dt.replace(tzinfo=pytz.utc).astimezone(ny_tz)
                formatted_timestamp = timestamp_dt.strftime('%Y-%m-%d %I:%M %p')
                formatted_jokes.append({
                    'text': joke_text,
                    'timestamp': formatted_timestamp
                })
            
            # Calculate pagination info
            total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
            
            return jsonify({
                'jokes': formatted_jokes,
                'count': len(formatted_jokes),
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            })
    except Exception as e:
        logging.error(f"Error fetching joke history: {e}")
        return jsonify({
            'jokes': [],
            'count': 0,
            'total_count': 0,
            'page': 1,
            'per_page': 5,
            'total_pages': 1,
            'has_next': False,
            'has_prev': False,
            'error': str(e)
        }), 500

@app.route('/api/refresh-cache')
@require_admin
def refresh_cache():
    """Admin endpoint to force refresh cache"""
    try:
        # Force refresh weather
        weather = get_weather(use_cache=False)
        # Force refresh forecast
        forecast = get_weather_forecast(use_cache=False)
        # Force refresh news
        news = get_news(use_cache=False)
        
        return jsonify({
            'status': 'success',
            'message': 'Cache refreshed successfully',
            'weather_updated': weather is not None,
            'forecast_updated': forecast is not None,
            'news_updated': news is not None and len(news) > 0
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ==================== CALENDAR API ENDPOINTS ====================
@app.route('/api/calendar-events')
def api_calendar_events():
    """Get all calendar events"""
    events = get_calendar_events()
    return jsonify(events)

@app.route('/api/calendar-feeds', methods=['GET', 'POST'])
def api_calendar_feeds():
    """Get or add calendar feeds"""
    if request.method == 'GET':
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT id, name, url, created_at FROM calendar_feeds ORDER BY created_at DESC")
        feeds = c.fetchall()
        conn.close()
        
        return jsonify([{
            'id': f[0],
            'name': f[1],
            'url': f[2],
            'created_at': f[3]
        } for f in feeds])
    
    elif request.method == 'POST':
        data = request.json
        name = data.get('name', '')
        url = data.get('url', '')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("INSERT INTO calendar_feeds (name, url) VALUES (?, ?)", (name, url))
        conn.commit()
        feed_id = c.lastrowid
        conn.close()
        
        # Clear cache
        set_cached_data("calendar_events", None)
        
        return jsonify({'id': feed_id, 'status': 'success'})

@app.route('/api/calendar-feeds/<int:feed_id>', methods=['DELETE'])
def api_delete_calendar_feed(feed_id):
    """Delete a calendar feed"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM calendar_feeds WHERE id = ?", (feed_id,))
    conn.commit()
    conn.close()
    
    # Clear cache
    set_cached_data("calendar_events", None)
    
    return jsonify({'status': 'success'})

@app.route('/api/calendar-events/local', methods=['GET', 'POST'])
def api_local_calendar_events():
    """Get or add local calendar events"""
    if request.method == 'GET':
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            SELECT id, title, start_time, end_time, location, description, created_at
            FROM calendar_events
            ORDER BY start_time ASC
        """)
        events = c.fetchall()
        conn.close()
        
        return jsonify([{
            'id': e[0],
            'title': e[1],
            'start_time': e[2],
            'end_time': e[3],
            'location': e[4],
            'description': e[5],
            'created_at': e[6]
        } for e in events])
    
    elif request.method == 'POST':
        data = request.json
        title = data.get('title', '')
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        location = data.get('location', '')
        description = data.get('description', '')
        
        if not title or not start_time:
            return jsonify({'error': 'Title and start_time are required'}), 400
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO calendar_events (title, start_time, end_time, location, description)
            VALUES (?, ?, ?, ?, ?)
        """, (title, start_time, end_time, location, description))
        conn.commit()
        event_id = c.lastrowid
        conn.close()
        
        # Clear cache
        set_cached_data("calendar_events", None)
        
        return jsonify({'id': event_id, 'status': 'success'})

@app.route('/api/calendar-events/local/<int:event_id>', methods=['PUT', 'DELETE'])
def api_local_calendar_event(event_id):
    """Update or delete a local calendar event"""
    if request.method == 'PUT':
        data = request.json
        title = data.get('title', '')
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        location = data.get('location', '')
        description = data.get('description', '')
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            UPDATE calendar_events
            SET title = ?, start_time = ?, end_time = ?, location = ?, description = ?
            WHERE id = ?
        """, (title, start_time, end_time, location, description, event_id))
        conn.commit()
        conn.close()
        
        # Clear cache
        set_cached_data("calendar_events", None)
        
        return jsonify({'status': 'success'})
    
    elif request.method == 'DELETE':
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
        conn.commit()
        conn.close()
        
        # Clear cache
        set_cached_data("calendar_events", None)
        
        return jsonify({'status': 'success'})

# ==================== COMMUTE API ENDPOINTS ====================
@app.route('/api/commute-info')
def api_commute_info():
    """Get commute information with real-time traffic events from TomTom"""
    # Check if force refresh is requested
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    commute = get_commute_info(use_cache=not force_refresh)
    if commute is None:
        # Return empty response with error message instead of None
        return jsonify({
            'error': 'No commute route configured. Please set origin and destination addresses above.',
            'traffic_events': []
        })
    # Return full commute data including traffic_events from TomTom API
    # traffic_events contains real incidents like road closures, crashes, construction
    return jsonify(commute)

@app.route('/api/traffic-history')
def api_traffic_history():
    """Get traffic event history - currently returns empty as we don't create false traffic events"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # DELETE ALL FALSE TRAFFIC EVENTS - These were auto-generated from delay calculations
        # OpenRouteService already accounts for traffic, so these events are false positives
        # Delete ALL traffic events since we don't create them anymore
        c.execute("""
            DELETE FROM traffic_events
        """)
        deleted_events = c.rowcount
        if deleted_events > 0:
            logging.info(f"Cleaned up {deleted_events} false traffic events from database")
        conn.commit()
        conn.close()
        
        # Clear commute cache to force refresh
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("DELETE FROM api_cache WHERE cache_key = ?", ("commute_info",))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.warning(f"Error clearing commute cache: {e}")
        
        # Return empty events list - we don't create traffic events anymore
        # OpenRouteService already provides traffic-aware routing
        events = []
        
        ny_tz = get_timezone()
        formatted_events = []
        for event in events:
            event_type, traffic_level, location, description, lat, lon, timestamp_str = event
            # Double-check: filter out any crash/incident events that might have slipped through
            if (event_type == 'crash' or 
                (description and any(keyword in description.lower() for keyword in ['crash', 'incident', 'accident', 'possible incident']))):
                continue
                
            timestamp_dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            if timestamp_dt.tzinfo is None:
                timestamp_dt = ny_tz.localize(timestamp_dt)
            else:
                timestamp_dt = timestamp_dt.astimezone(ny_tz)
            
            formatted_events.append({
                'type': event_type,
                'traffic_level': traffic_level,
                'location': location or 'Unknown',
                'description': description or '',
                'time': timestamp_dt.strftime('%I:%M %p'),
                'date': timestamp_dt.strftime('%Y-%m-%d'),
                'lat': lat,
                'lon': lon
            })
        
        return jsonify({'events': formatted_events, 'count': len(formatted_events)})
    except Exception as e:
        logging.error(f"Error fetching traffic history: {e}")
        return jsonify({'events': [], 'count': 0, 'error': str(e)}), 500

@app.route('/api/traffic-history/clear-all', methods=['POST'])
@require_admin
def api_clear_all_traffic_events():
    """Admin endpoint to manually clear all traffic events"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("DELETE FROM traffic_events")
        deleted_count = c.rowcount
        conn.commit()
        conn.close()
        
        # Clear commute cache
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("DELETE FROM api_cache WHERE cache_key = ?", ("commute_info",))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.warning(f"Error clearing commute cache: {e}")
        
        logging.info(f"Admin cleared all {deleted_count} traffic events")
        return jsonify({'status': 'success', 'deleted_count': deleted_count})
    except Exception as e:
        logging.error(f"Error clearing all traffic events: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/traffic-history/clear-crashes', methods=['POST'])
@require_admin
def api_clear_crash_events():
    """Admin endpoint to manually clear all crash/incident events from database"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            DELETE FROM traffic_events 
            WHERE event_type = 'crash' 
            OR description LIKE '%crash%' 
            OR description LIKE '%incident%'
            OR description LIKE '%accident%'
            OR description LIKE '%possible incident%'
        """)
        deleted_count = c.rowcount
        conn.commit()
        conn.close()
        
        # Also clear cache
        set_cached_data("commute_info", None)
        
        logging.info(f"Manually deleted {deleted_count} crash/incident events from database")
        return jsonify({'status': 'success', 'deleted_count': deleted_count})
    except Exception as e:
        logging.error(f"Error clearing crash events: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/settings/commute', methods=['POST'])
def api_set_commute():
    """Set commute origin and destination"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        origin = data.get('origin', '').strip()
        destination = data.get('destination', '').strip()
        
        if not origin or not destination:
            return jsonify({'error': 'Origin and destination are required'}), 400
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Ensure settings table exists
        c.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        c.execute("INSERT OR REPLACE INTO settings (key, value, updated) VALUES ('commute_origin', ?, CURRENT_TIMESTAMP)", (origin,))
        c.execute("INSERT OR REPLACE INTO settings (key, value, updated) VALUES ('commute_destination', ?, CURRENT_TIMESTAMP)", (destination,))
        conn.commit()
        conn.close()
        
        # Clear cache by deleting the cache entry
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("DELETE FROM api_cache WHERE cache_key = ?", ("commute_info",))
            conn.commit()
            conn.close()
            logging.info("Cleared commute_info cache")
        except Exception as e:
            logging.warning(f"Error clearing cache: {e}")
        
        logging.info(f"Commute settings saved: {origin} -> {destination}")
        return jsonify({'status': 'success', 'origin': origin, 'destination': destination})
    except Exception as e:
        logging.error(f"Error saving commute settings: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== AIR QUALITY API ENDPOINTS ====================
@app.route('/api/air-quality')
def api_air_quality():
    """Get air quality data"""
    air_quality = get_air_quality()
    return jsonify(air_quality)

# ==================== QUOTES API ENDPOINTS ====================
@app.route('/api/daily-quote')
def api_daily_quote():
    """Get daily quote"""
    quote = get_daily_quote()
    return jsonify(quote)

@app.route('/api/quote-history')
def quote_history():
    """API endpoint to get quote history with pagination"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        
        # Ensure valid values
        page = max(1, page)
        per_page = max(1, min(per_page, 100))  # Limit per_page to 100
        
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            
            # Get total count
            c.execute("SELECT COUNT(*) FROM quote_history")
            total_count = c.fetchone()[0]
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get paginated quotes
            c.execute("""
                SELECT quote_text, author, timestamp 
                FROM quote_history 
                ORDER BY timestamp DESC 
                LIMIT ? OFFSET ?
            """, (per_page, offset))
            quotes = c.fetchall()
            
            # Format the quotes
            formatted_quotes = []
            ny_tz = get_timezone()
            for quote_text, author, timestamp_str in quotes:
                timestamp_dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                timestamp_dt = timestamp_dt.replace(tzinfo=pytz.utc).astimezone(ny_tz)
                formatted_timestamp = timestamp_dt.strftime('%Y-%m-%d %I:%M %p')
                formatted_quotes.append({
                    'text': quote_text,
                    'author': author or 'Unknown',
                    'timestamp': formatted_timestamp
                })
            
            # Calculate pagination info
            total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
            
            return jsonify({
                'quotes': formatted_quotes,
                'count': len(formatted_quotes),
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            })
    except Exception as e:
        logging.error(f"Error fetching quote history: {e}")
        return jsonify({
            'quotes': [],
            'count': 0,
            'total_count': 0,
            'page': 1,
            'per_page': 5,
            'total_pages': 1,
            'has_next': False,
            'has_prev': False,
            'error': str(e)
        }), 500

# ==================== ASTRONOMY API ENDPOINTS ====================
@app.route('/api/astronomy')
def api_astronomy():
    """Get astronomy data"""
    astronomy = get_astronomy_data()
    return jsonify(astronomy)

# ==================== WEATHER ALERTS API ENDPOINTS ====================
@app.route('/api/weather-alerts')
def api_weather_alerts():
    """Get weather alerts"""
    alerts = get_weather_alerts()
    return jsonify(alerts)

# ==================== SWITCHBOT API ENDPOINTS ====================
@app.route('/api/switchbot-locks')
def api_switchbot_locks():
    """Get SwitchBot lock statuses"""
    locks = get_switchbot_lock_status()
    return jsonify(locks)

# ==================== HOME ASSISTANT API ENDPOINTS ====================
@app.route('/api/home-assistant')
def api_home_assistant():
    """Get all Home Assistant data (for index page)"""
    try:
        entities = get_ha_states()
        devices = filter_ha_devices(entities, for_dashboard=False)
        battery_sensors = filter_ha_battery_sensors(entities, for_dashboard=False)
        
        return jsonify({
            'devices': devices,
            'battery_sensors': battery_sensors,
            'total_entities': len(entities)
        })
    except Exception as e:
        logging.error(f"Error in api_home_assistant: {e}")
        return jsonify({
            'devices': [],
            'battery_sensors': [],
            'total_entities': 0,
            'error': str(e)
        }), 500

@app.route('/api/home-assistant/dashboard')
def api_home_assistant_dashboard():
    """Get filtered Home Assistant data (for RPi dashboard)"""
    try:
        entities = get_ha_states()
        devices = filter_ha_devices(entities, for_dashboard=True)
        battery_sensors = filter_ha_battery_sensors(entities, for_dashboard=True)
        
        return jsonify({
            'devices': devices,
            'battery_sensors': battery_sensors,
            'total_on_devices': len(devices),
            'total_low_battery': len(battery_sensors)
        })
    except Exception as e:
        logging.error(f"Error in api_home_assistant_dashboard: {e}")
        return jsonify({
            'devices': [],
            'battery_sensors': [],
            'total_on_devices': 0,
            'total_low_battery': 0,
            'error': str(e)
        }), 500

# ==================== INTERNET SPEED API ENDPOINTS ====================
@app.route('/api/internet-speed')
def api_internet_speed():
    """Get internet speed test results"""
    speed = get_internet_speed()
    return jsonify(speed)

@app.route('/api/internet-speed/run', methods=['POST'])
def api_run_speed_test():
    """Trigger a speed test"""
    thread = threading.Thread(target=run_speed_test)
    thread.daemon = True
    thread.start()
    return jsonify({'status': 'started', 'message': 'Speed test started in background'})

# ==================== SPORTS API ENDPOINTS ====================
@app.route('/api/sports-scores')
def api_sports_scores():
    """Get sports scores with sport filtering"""
    scores = get_sports_scores()
    return jsonify(scores)

@app.route('/api/settings/sports', methods=['GET', 'POST'])
def api_sports_teams():
    """Get or set favorite sports teams"""
    if request.method == 'GET':
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT value FROM settings WHERE key = 'sports_teams'")
            result = c.fetchone()
            conn.close()
            
            if result:
                try:
                    teams = json.loads(result[0])
                except:
                    teams = []
            else:
                teams = []
            
            return jsonify({'teams': teams})
        except Exception as e:
            logging.error(f"Error getting sports teams: {e}")
            return jsonify({'teams': []})
    
    elif request.method == 'POST':
        """Set favorite sports teams"""
        try:
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            teams = data.get('teams', [])
            
            if not isinstance(teams, list):
                return jsonify({'error': 'Teams must be a list'}), 400
            
            # Filter and normalize teams - handle both old format (strings) and new format (objects)
            normalized_teams = []
            for team in teams:
                if isinstance(team, dict):
                    # New format: {name: "...", sport: "..."}
                    team_name = team.get('name', '').strip()
                    team_sport = team.get('sport', '').strip()
                    if team_name and team_sport:
                        normalized_teams.append({'name': team_name, 'sport': team_sport})
                elif isinstance(team, str):
                    # Old format: just a string
                    team = team.strip()
                    if team:
                        normalized_teams.append(team)
            
            teams = normalized_teams
            
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            # Ensure settings table exists
            c.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            c.execute("INSERT OR REPLACE INTO settings (key, value, updated) VALUES ('sports_teams', ?, CURRENT_TIMESTAMP)", (json.dumps(teams),))
            conn.commit()
            conn.close()
            
            # Clear cache
            set_cached_data("sports_scores", None)
            
            logging.info(f"Sports teams saved: {teams}")
            return jsonify({'status': 'success', 'teams': teams})
        except Exception as e:
            logging.error(f"Error saving sports teams: {e}")
            return jsonify({'error': str(e)}), 500

# ==================== PHOTO GALLERY API ENDPOINTS ====================
@app.route('/api/photos')
def api_photos():
    """Get list of photos"""
    photos = get_photos()
    return jsonify(photos)

@app.route('/api/upload-photo', methods=['POST'])
def api_upload_photo():
    """Upload a photo"""
    if 'photo' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    filename = secure_filename(file.filename)
    
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        return jsonify({'error': 'Invalid file type'}), 400
    
    gallery_dir = os.path.join('static', 'images', 'gallery')
    if not os.path.exists(gallery_dir):
        os.makedirs(gallery_dir, exist_ok=True)
    
    filepath = os.path.join(gallery_dir, filename)
    file.save(filepath)
    
    return jsonify({'status': 'success', 'filename': filename})

@app.route('/api/delete-photo/<filename>', methods=['DELETE'])
def api_delete_photo(filename):
    """Delete a photo"""
    filename = secure_filename(filename)
    gallery_dir = os.path.join('static', 'images', 'gallery')
    filepath = os.path.join(gallery_dir, filename)
    
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'status': 'success'})
    else:
        return jsonify({'error': 'File not found'}), 404

# ==================== PACKAGE TRACKING API ENDPOINTS ====================
@app.route('/api/packages', methods=['GET', 'POST'])
def api_packages():
    """Get active packages or add a new package"""
    if request.method == 'GET':
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("""
                SELECT id, tracking_number, carrier, description, status, last_location, 
                       estimated_delivery, delivered_date, created_at, updated_at
                FROM packages
                ORDER BY created_at DESC
            """)
            packages_data = c.fetchall()
            conn.close()
            
            packages = []
            for pkg in packages_data:
                packages.append({
                    'id': pkg[0],
                    'tracking_number': pkg[1],
                    'carrier': pkg[2],
                    'description': pkg[3] or '',
                    'status': pkg[4] or 'Unknown',
                    'last_location': pkg[5] or '',
                    'estimated_delivery': pkg[6],
                    'delivered_date': pkg[7],
                    'created_at': pkg[8],
                    'updated_at': pkg[9]
                })
            
            return jsonify(packages)
        except Exception as e:
            logging.error(f"Error fetching packages: {e}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            tracking_number = data.get('tracking_number', '').strip()
            description = data.get('description', '').strip()
            
            if not tracking_number:
                return jsonify({'error': 'Tracking number is required'}), 400
            
            # Detect carrier
            carrier = detect_carrier(tracking_number)
            
            # Get initial status
            status_data = get_package_status(tracking_number, carrier)
            
            # Insert into database
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("""
                INSERT INTO packages (tracking_number, carrier, description, status, last_location, estimated_delivery)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tracking_number,
                carrier,
                description,
                status_data['status'],
                status_data['last_location'],
                status_data['estimated_delivery']
            ))
            package_id = c.lastrowid
            conn.commit()
            conn.close()
            
            logging.info(f"Added package: {tracking_number} ({carrier})")
            return jsonify({'id': package_id, 'status': 'success'})
        except Exception as e:
            logging.error(f"Error adding package: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/packages/<int:package_id>', methods=['DELETE'])
def api_delete_package(package_id):
    """Delete a package"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("DELETE FROM packages WHERE id = ?", (package_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        logging.error(f"Error deleting package: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/packages/<int:package_id>/refresh', methods=['POST'])
def api_refresh_package(package_id):
    """Refresh package tracking status"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT tracking_number, carrier FROM packages WHERE id = ?", (package_id,))
        result = c.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'error': 'Package not found'}), 404
        
        tracking_number, carrier = result
        
        # Get updated status
        status_data = get_package_status(tracking_number, carrier)
        
        # Check if delivered
        delivered_date = None
        if status_data['status'].lower() == 'delivered':
            delivered_date = datetime.now(get_timezone())
        
        # Update package
        c.execute("""
            UPDATE packages 
            SET status = ?, last_location = ?, estimated_delivery = ?, 
                delivered_date = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            status_data['status'],
            status_data['last_location'],
            status_data['estimated_delivery'],
            delivered_date,
            package_id
        ))
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'package_status': status_data})
    except Exception as e:
        logging.error(f"Error refreshing package: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/packages/archive', methods=['GET'])
def api_packages_archive():
    """Get archived packages with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        
        page = max(1, page)
        per_page = max(1, min(per_page, 100))
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Get total count
        c.execute("SELECT COUNT(*) FROM packages_archive")
        total_count = c.fetchone()[0]
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get paginated packages
        c.execute("""
            SELECT id, tracking_number, carrier, description, status, last_location, 
                   estimated_delivery, delivered_date, created_at, archived_at
            FROM packages_archive
            ORDER BY archived_at DESC
            LIMIT ? OFFSET ?
        """, (per_page, offset))
        packages_data = c.fetchall()
        conn.close()
        
        packages = []
        for pkg in packages_data:
            packages.append({
                'id': pkg[0],
                'tracking_number': pkg[1],
                'carrier': pkg[2],
                'description': pkg[3] or '',
                'status': pkg[4] or 'Unknown',
                'last_location': pkg[5] or '',
                'estimated_delivery': pkg[6],
                'delivered_date': pkg[7],
                'created_at': pkg[8],
                'archived_at': pkg[9]
            })
        
        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
        
        return jsonify({
            'packages': packages,
            'count': len(packages),
            'total_count': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        })
    except Exception as e:
        logging.error(f"Error fetching archived packages: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== SHOPPING LIST API ENDPOINTS ====================
@app.route('/api/shopping-list', methods=['GET', 'POST'])
def api_shopping_list():
    """Get all shopping list items or add a new item"""
    if request.method == 'GET':
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("""
                SELECT id, item_name, completed, created_at, updated_at
                FROM shopping_list
                ORDER BY completed ASC, created_at ASC
            """)
            items_data = c.fetchall()
            conn.close()
            
            items = []
            for item in items_data:
                items.append({
                    'id': item[0],
                    'item_name': item[1],
                    'completed': bool(item[2]),
                    'created_at': item[3],
                    'updated_at': item[4]
                })
            
            return jsonify(items)
        except Exception as e:
            logging.error(f"Error fetching shopping list: {e}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            item_name = data.get('item_name', '').strip()
            
            if not item_name:
                return jsonify({'error': 'Item name is required'}), 400
            
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("""
                INSERT INTO shopping_list (item_name, completed)
                VALUES (?, 0)
            """, (item_name,))
            item_id = c.lastrowid
            conn.commit()
            conn.close()
            
            logging.info(f"Added shopping list item: {item_name}")
            return jsonify({'id': item_id, 'status': 'success'})
        except Exception as e:
            logging.error(f"Error adding shopping list item: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/shopping-list/<int:item_id>', methods=['PUT', 'DELETE'])
def api_shopping_list_item(item_id):
    """Update or delete a shopping list item"""
    if request.method == 'PUT':
        try:
            data = request.json
            item_name = data.get('item_name', '').strip()
            completed = data.get('completed')
            
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            # Check if item exists
            c.execute("SELECT id FROM shopping_list WHERE id = ?", (item_id,))
            if not c.fetchone():
                conn.close()
                return jsonify({'error': 'Item not found'}), 404
            
            # Update item
            if item_name and completed is not None:
                c.execute("""
                    UPDATE shopping_list 
                    SET item_name = ?, completed = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (item_name, 1 if completed else 0, item_id))
            elif item_name:
                c.execute("""
                    UPDATE shopping_list 
                    SET item_name = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (item_name, item_id))
            elif completed is not None:
                c.execute("""
                    UPDATE shopping_list 
                    SET completed = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (1 if completed else 0, item_id))
            else:
                conn.close()
                return jsonify({'error': 'No update data provided'}), 400
            
            conn.commit()
            conn.close()
            
            return jsonify({'status': 'success'})
        except Exception as e:
            logging.error(f"Error updating shopping list item: {e}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("DELETE FROM shopping_list WHERE id = ?", (item_id,))
            conn.commit()
            conn.close()
            return jsonify({'status': 'success'})
        except Exception as e:
            logging.error(f"Error deleting shopping list item: {e}")
            return jsonify({'error': str(e)}), 500

def ping_device(ip):
    logging.debug(f"Pinging IP: {ip}")
    result = subprocess.run(['ping', '-c', '1', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        logging.debug(f"Ping successful: {ip} is online.")
        return True
    else:
        logging.debug(f"Ping failed: {ip} is offline.")
        return False

def get_mac_address(ip):
    try:
        logging.debug(f"Getting MAC address for IP: {ip}")
        result = subprocess.check_output(['arp', '-n', ip], stderr=subprocess.STDOUT)
        result = result.decode('utf-8').splitlines()
        for line in result:
            if ip in line:
                parts = line.split()
                if len(parts) >= 3 and ':' in parts[2] and len(parts[2].split(':')) == 6:
                    mac_address = parts[2]
                    logging.debug(f"MAC address for IP {ip} is {mac_address}")
                    return mac_address.lower()
        logging.debug(f"No valid MAC address found for IP: {ip}")
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to get MAC address for IP: {ip}. Error: {e}")
        return None

def scan_network_for_mac(target_mac, network_range="10.0.0.0/24"):
    """
    Scan the network for a specific MAC address and return its IP if found.
    """
    try:
        logging.info(f"Scanning network for MAC address: {target_mac}")
        
        # First, try to ping the entire subnet to populate ARP table
        # Using fping if available, otherwise fall back to nmap or manual ping
        try:
            # Try fping for faster scanning
            subnet = network_range.rsplit('.', 1)[0]
            subprocess.run(['fping', '-a', '-g', f'{subnet}.1', f'{subnet}.254'], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fall back to manual ping scan
            logging.debug("fping not available, using manual ping scan")
            subnet = network_range.rsplit('.', 1)[0]
            for i in range(1, 255):
                ip = f"{subnet}.{i}"
                subprocess.run(['ping', '-c', '1', '-W', '1', ip], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Now check the ARP table for the MAC address
        result = subprocess.check_output(['arp', '-n'], stderr=subprocess.STDOUT)
        result = result.decode('utf-8').splitlines()
        
        for line in result:
            if target_mac.lower() in line.lower():
                parts = line.split()
                if len(parts) >= 3:
                    # Extract IP address (should be first element that looks like an IP)
                    for part in parts:
                        if re.match(r'\d+\.\d+\.\d+\.\d+', part):
                            logging.info(f"Found MAC {target_mac} at IP {part}")
                            return part
        
        logging.info(f"MAC address {target_mac} not found on network")
        return None
        
    except Exception as e:
        logging.error(f"Error scanning network for MAC {target_mac}: {e}")
        return None

def update_device_ip(device_id, new_ip):
    """Update the IP address for a device in the database"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("UPDATE devices SET ip_address = ? WHERE id = ?", (new_ip, device_id))
            conn.commit()
            logging.info(f"Updated device {device_id} with new IP: {new_ip}")
            return True
    except Exception as e:
        logging.error(f"Failed to update device IP: {e}")
        return False

def send_gotify_message(title, message):
    payload = {
        "title": title,
        "message": message,
        "priority": 5
    }
    headers = {
        "X-Gotify-Key": GOTIFY_TOKEN
    }
    try:
        logging.debug(f"Sending Gotify notification with title: {title} and message: {message}")
        response = requests.post(GOTIFY_URL, json=payload, headers=headers)
        response.raise_for_status()
        logging.info(f"Gotify notification sent: {title} - {message}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send Gotify notification: {e}")

def update_device_status(retry_count=5, delay=0.1):
    attempts = 0
    while attempts < retry_count:
        try:
            with sqlite3.connect(db_path) as conn:
                c = conn.cursor()
                
                c.execute("SELECT * FROM devices")
                devices = c.fetchall()

                for device in devices:
                    name, ip, expected_mac, current_status, last_seen, notify, device_id = device[1], device[2], device[3], device[4], device[5], device[6], device[0]
                    logging.info(f"Checking status for device {name} with IP {ip} and expected MAC {expected_mac}")
                    
                    is_online = ping_device(ip)
                    actual_mac = get_mac_address(ip) if is_online else None
                    
                    # Check if the device is at the expected IP with the correct MAC
                    if is_online and actual_mac == expected_mac.lower():
                        new_status = 'home'
                        logging.debug(f"Device {name} found at expected IP {ip}")
                    elif is_online and actual_mac and actual_mac != expected_mac.lower():
                        # Different device at this IP, search for the correct device by MAC
                        logging.info(f"Different MAC found at IP {ip}. Expected {expected_mac}, got {actual_mac}")
                        logging.info(f"Searching network for device {name} with MAC {expected_mac}")
                        
                        new_ip = scan_network_for_mac(expected_mac)
                        if new_ip:
                            logging.info(f"Found device {name} at new IP: {new_ip}")
                            # Update the IP in the database
                            if update_device_ip(device_id, new_ip):
                                # Send notification about IP change
                                send_gotify_message(
                                    f'{name} IP Changed',
                                    f'{name} moved from {ip} to {new_ip}'
                                )
                                new_status = 'home'
                                ip = new_ip  # Update for notification purposes
                            else:
                                new_status = 'away'
                        else:
                            new_status = 'away'
                    else:
                        # Device not found at expected IP, search the network
                        logging.info(f"Device {name} not found at IP {ip}, searching network")
                        new_ip = scan_network_for_mac(expected_mac)
                        if new_ip:
                            logging.info(f"Found device {name} at new IP: {new_ip}")
                            # Update the IP in the database
                            if update_device_ip(device_id, new_ip):
                                # Send notification about IP change
                                send_gotify_message(
                                    f'{name} IP Changed',
                                    f'{name} moved from {ip} to {new_ip}'
                                )
                                new_status = 'home'
                                ip = new_ip  # Update for notification purposes
                            else:
                                new_status = 'away'
                        else:
                            new_status = 'away'
                    
                    logging.debug(f"Device: {name}, Current status: {current_status}, New status: {new_status}")
                    
                    if new_status != current_status:
                        logging.info(f"Device {name} status changed from {current_status} to {new_status}.")
                        c.execute("UPDATE devices SET status = ?, last_seen = CURRENT_TIMESTAMP WHERE id = ?", (new_status, device_id))
                        c.execute("INSERT INTO device_history (device_id, status) VALUES (?, ?)", (device_id, new_status))
                        logging.debug(f"Inserted '{new_status}' status into device_history for {name}.")
                        
                        if new_status == 'home' and notify == 'home':
                            logging.info(f"Sending home notification for {name}.")
                            send_gotify_message(f'{name} is Home', f'{name} (IP: {ip}) is now home.')
                        elif new_status == 'away' and notify == 'away':
                            logging.info(f"Sending away notification for {name}.")
                            send_gotify_message(f'{name} is Away', f'{name} (IP: {ip}) is now away.')

                conn.commit()
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                logging.warning(f"Database is locked, retrying in {delay} seconds...")
                attempts += 1
                time.sleep(delay)
            else:
                logging.error(f"Failed to update device status: {e}")
                raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            conn.rollback()
            conn.close()
            raise

def periodic_scan():
    while True:
        logging.info("Starting periodic scan...")
        update_device_status()
        # Check weather alerts every 5 minutes
        get_weather_alerts(use_cache=False)
        time.sleep(60)

def get_weather(use_cache=True, retry_count=3):
    """Fetch current weather data with caching and retry logic"""
    cache_key = "weather_data"
    
    # Try to get cached data first
    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
    
    # If no cache or cache expired, fetch from API with retries
    for attempt in range(retry_count):
        try:
            params = {
                'q': WEATHER_CITY,
                'appid': WEATHER_API_KEY,
                'units': 'imperial'
            }
            response = requests.get(WEATHER_API_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            weather_data = {
                'temp': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'description': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'humidity': data['main']['humidity'],
                'wind_speed': round(data['wind']['speed']),
                'location': data['name'],
                'country': data['sys']['country'],
                'updated': datetime.now(get_timezone()).strftime('%I:%M %p')
            }
            
            # Cache the successful response
            set_cached_data(cache_key, weather_data)
            return weather_data
            
        except Exception as e:
            logging.error(f"Failed to fetch weather (attempt {attempt + 1}/{retry_count}): {e}")
            if attempt < retry_count - 1:
                time.sleep(2)  # Wait before retry
            else:
                # Return cached data even if expired, or None
                cached_data = get_cached_data("weather_data")
                if cached_data:
                    logging.info("Using expired cache due to API failure")
                    return cached_data
                return None

def get_weather_forecast(use_cache=True, retry_count=3):
    """Fetch weather forecast data with caching and retry logic"""
    cache_key = "weather_forecast"
    
    # Try to get cached data first
    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
    
    # If no cache or cache expired, fetch from API with retries
    for attempt in range(retry_count):
        try:
            params = {
                'lat': WEATHER_LAT,
                'lon': WEATHER_LON,
                'appid': WEATHER_API_KEY,
                'units': 'imperial',
                'cnt': 40  # Get max allowed in free tier (5 days worth)
            }
            response = requests.get(WEATHER_FORECAST_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Process hourly forecast (next 3 hours)
            hourly_forecast = []
            current_time = datetime.now()
            
            for item in data['list'][:3]:  # First 3 items = next 9 hours (3-hour intervals)
                forecast_time = datetime.fromtimestamp(item['dt'])
                hourly_forecast.append({
                    'time': forecast_time.strftime('%I %p'),
                    'temp': round(item['main']['temp']),
                    'description': item['weather'][0]['description'].title(),
                    'icon': item['weather'][0]['icon']
                })
            
            # Process daily forecast (next 3 days)
            daily_forecast = []
            daily_temps = {}
            
            # Group forecasts by day
            for item in data['list']:
                date = datetime.fromtimestamp(item['dt']).date()
                if date not in daily_temps:
                    daily_temps[date] = {
                        'temps': [],
                        'descriptions': [],
                        'icons': []
                    }
                daily_temps[date]['temps'].append(item['main']['temp'])
                daily_temps[date]['descriptions'].append(item['weather'][0]['description'])
                daily_temps[date]['icons'].append(item['weather'][0]['icon'])
            
            # Get next 3 days (skip today)
            sorted_dates = sorted(daily_temps.keys())
            for date in sorted_dates[1:4]:  # Skip today, get next 3
                if date in daily_temps:
                    temps = daily_temps[date]['temps']
                    # Most common weather description and icon for the day
                    most_common_desc = max(set(daily_temps[date]['descriptions']), 
                                         key=daily_temps[date]['descriptions'].count)
                    most_common_icon = max(set(daily_temps[date]['icons']), 
                                         key=daily_temps[date]['icons'].count)
                    
                    daily_forecast.append({
                        'day': date.strftime('%A'),
                        'high': round(max(temps)),
                        'low': round(min(temps)),
                        'description': most_common_desc.title(),
                        'icon': most_common_icon
                    })
            
            forecast_data = {
                'hourly': hourly_forecast,
                'daily': daily_forecast,
                'updated': datetime.now(get_timezone()).strftime('%I:%M %p')
            }
            
            # Cache the successful response
            set_cached_data(cache_key, forecast_data)
            return forecast_data
            
        except Exception as e:
            logging.error(f"Failed to fetch weather forecast (attempt {attempt + 1}/{retry_count}): {e}")
            if attempt < retry_count - 1:
                time.sleep(2)  # Wait before retry
            else:
                # Return cached data even if expired, or None
                cached_data = get_cached_data("weather_forecast")
                if cached_data:
                    logging.info("Using expired forecast cache due to API failure")
                    return cached_data
                return None

def get_news(use_cache=True, retry_count=3):
    """Fetch news articles with caching, retry logic, and fallback"""
    cache_key = "news_data"
    
    # Try to get cached data first
    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
    
    # If no cache or cache expired, fetch from API with retries
    for attempt in range(retry_count):
        try:
            # Get date from 3 days ago for fresher news
            from_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
            
            # First, try NewsAPI
            # Try top-headlines endpoint for US news
            try:
                url = "https://newsapi.org/v2/top-headlines"
                params = {
                    'country': 'us',
                    'apiKey': NEWS_API_KEY,
                    'pageSize': 10
                }
                
                response = requests.get(url, params=params, timeout=5)
                logging.info(f"NewsAPI response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    articles = []
                    
                    for article in data.get('articles', []):
                        if (article.get('title') and 
                            '[Removed]' not in article.get('title', '') and
                            article.get('description')):
                            
                            articles.append({
                                'title': article['title'],
                                'source': article['source']['name'],
                                'description': article.get('description', '')[:200] + '...' 
                                             if len(article.get('description', '')) > 200 else article.get('description', ''),
                                'publishedAt': article.get('publishedAt', ''),
                                'news_type': 'US National News'
                            })
                    
                    if articles:
                        logging.info(f"Successfully fetched {len(articles)} articles from NewsAPI")
                        # Cache the successful response
                        set_cached_data(cache_key, articles[:5])
                        return articles[:5]
                
                elif response.status_code == 426:
                    logging.warning("NewsAPI requires paid plan for production use")
                elif response.status_code == 401:
                    logging.error("NewsAPI authentication failed - check API key")
                else:
                    logging.error(f"NewsAPI error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                logging.error(f"NewsAPI request failed: {e}")
            
            # Fallback to RSS feeds if NewsAPI fails
            logging.info("Falling back to RSS feeds for news")
            
            rss_feeds = [
                {
                    'url': 'https://www.timesunion.com/news/feed/Local-News-193.php',  # Times Union Albany RSS
                    'source': 'Times Union',
                    'type': 'Local News'
                },
                {
                    'url': 'https://feeds.nbcnews.com/nbcnews/public/news',
                    'source': 'NBC News',
                    'type': 'US National News'
                },
                {
                    'url': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
                    'source': 'New York Times',
                    'type': 'US National News'
                },
                {
                    'url': 'http://feeds.bbci.co.uk/news/rss.xml',
                    'source': 'BBC News',
                    'type': 'World News'
                }
            ]
            
            all_articles = []
            
            for feed_info in rss_feeds:
                try:
                    feed = feedparser.parse(feed_info['url'])
                    
                    if feed.bozo:
                        logging.warning(f"Failed to parse RSS feed from {feed_info['source']}")
                        continue
                    
                    for entry in feed.entries[:3]:  # Get top 3 from each source
                        # Parse publication date
                        pub_date = None
                        if hasattr(entry, 'published_parsed'):
                            pub_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                        elif hasattr(entry, 'updated_parsed'):
                            pub_date = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
                        
                        # Skip old articles (older than 7 days)
                        if pub_date and (datetime.now() - pub_date).days > 7:
                            continue
                        
                        article = {
                            'title': entry.get('title', 'No title'),
                            'source': feed_info['source'],
                            'description': entry.get('summary', '')[:200] + '...' 
                                         if len(entry.get('summary', '')) > 200 else entry.get('summary', 'No description available'),
                            'publishedAt': pub_date.isoformat() if pub_date else datetime.now().isoformat(),
                            'news_type': feed_info['type']
                        }
                        
                        # Clean up HTML from description
                        article['description'] = re.sub('<[^<]+?>', '', article['description'])
                        
                        all_articles.append(article)
                        
                except Exception as e:
                    logging.error(f"Failed to fetch RSS from {feed_info['source']}: {e}")
                    continue
            
            if all_articles:
                # Sort by publication date (newest first)
                all_articles.sort(key=lambda x: x['publishedAt'], reverse=True)
                logging.info(f"Successfully fetched {len(all_articles)} articles from RSS feeds")
                # Cache the successful response
                set_cached_data(cache_key, all_articles[:5])
                return all_articles[:5]
                
        except Exception as e:
            logging.error(f"Critical error in get_news() (attempt {attempt + 1}/{retry_count}): {e}")
            if attempt < retry_count - 1:
                time.sleep(2)  # Wait before retry
            
    # If all attempts failed, try to return cached data even if expired
    cached_data = get_cached_data("news_data")
    if cached_data:
        logging.info("Using expired cache due to API failure")
        return cached_data
        
    # If everything fails, return a helpful error message
    logging.error("Failed to fetch news from all sources")
    return [{
        'title': 'News Currently Unavailable',
        'source': 'System',
        'description': 'Unable to fetch news at this time. Please try again later.',
        'publishedAt': datetime.now().isoformat(),
        'news_type': 'Error'
    }]

# ==================== CALENDAR FUNCTIONS ====================
def get_calendar_events(use_cache=True):
    """Fetch calendar events from all iCal feeds and local events"""
    cache_key = "calendar_events"
    
    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
    
    all_events = []
    ny_tz = get_timezone()
    now = datetime.now(ny_tz)
    seven_days_later = now + timedelta(days=7)
    
    try:
        # Get all calendar feeds
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT id, name, url FROM calendar_feeds")
        feeds = c.fetchall()
        
        # Parse iCal feeds
        try:
            from icalendar import Calendar
        except ImportError:
            logging.error("icalendar library not installed. Install with: pip install icalendar")
            # Continue without iCal parsing
            feeds = []
        
        for feed_id, feed_name, feed_url in feeds:
            try:
                response = requests.get(feed_url, timeout=10)
                response.raise_for_status()
                cal = Calendar.from_ical(response.content)
                
                for component in cal.walk('VEVENT'):
                    try:
                        summary = str(component.get('summary', ''))
                        dtstart = component.get('dtstart')
                        dtend = component.get('dtend')
                        location = str(component.get('location', ''))
                        
                        if dtstart:
                            if isinstance(dtstart.dt, datetime):
                                start_dt = dtstart.dt
                                if start_dt.tzinfo is None:
                                    start_dt = ny_tz.localize(start_dt)
                                else:
                                    start_dt = start_dt.astimezone(ny_tz)
                            else:
                                # All-day event
                                start_dt = ny_tz.localize(datetime.combine(dtstart.dt, datetime.min.time()))
                            
                            if start_dt >= now and start_dt <= seven_days_later:
                                if dtend:
                                    if isinstance(dtend.dt, datetime):
                                        end_dt = dtend.dt
                                        if end_dt.tzinfo is None:
                                            end_dt = ny_tz.localize(end_dt)
                                        else:
                                            end_dt = end_dt.astimezone(ny_tz)
                                    else:
                                        end_dt = ny_tz.localize(datetime.combine(dtend.dt, datetime.max.time()))
                                else:
                                    end_dt = start_dt + timedelta(hours=1)
                                
                                all_events.append({
                                    'title': summary,
                                    'start': start_dt.strftime('%Y-%m-%d %H:%M:%S'),
                                    'end': end_dt.strftime('%Y-%m-%d %H:%M:%S'),
                                    'location': location,
                                    'source': feed_name or f'Feed {feed_id}',
                                    'all_day': not isinstance(dtstart.dt, datetime) if dtstart else False
                                })
                    except Exception as e:
                        logging.error(f"Error parsing event from feed {feed_name}: {e}")
                        continue
            except Exception as e:
                logging.error(f"Error fetching calendar feed {feed_name}: {e}")
                continue
        
        # Get local calendar events
        c.execute("""
            SELECT id, title, start_time, end_time, location, description 
            FROM calendar_events 
            WHERE start_time >= ? AND start_time <= ?
            ORDER BY start_time ASC
        """, (now.strftime('%Y-%m-%d %H:%M:%S'), seven_days_later.strftime('%Y-%m-%d %H:%M:%S')))
        local_events = c.fetchall()
        
        for event in local_events:
            event_id, title, start_time, end_time, location, description = event
            start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            if start_dt.tzinfo is None:
                start_dt = ny_tz.localize(start_dt)
            else:
                start_dt = start_dt.astimezone(ny_tz)
            
            all_events.append({
                'id': event_id,
                'title': title,
                'start': start_dt.strftime('%Y-%m-%d %H:%M:%S'),
                'end': end_time if end_time else start_dt.strftime('%Y-%m-%d %H:%M:%S'),
                'location': location or '',
                'description': description or '',
                'source': 'Local',
                'all_day': False
            })
        
        conn.close()
        
        # Sort by start time
        all_events.sort(key=lambda x: x['start'])
        
        # Format for display
        formatted_events = []
        for event in all_events:
            start_dt = datetime.strptime(event['start'], '%Y-%m-%d %H:%M:%S')
            if start_dt.tzinfo:
                start_dt = start_dt.astimezone(ny_tz)
            else:
                start_dt = ny_tz.localize(start_dt)
            
            formatted_events.append({
                'id': event.get('id'),
                'title': event['title'],
                'date': start_dt.strftime('%A, %B %d'),
                'time': start_dt.strftime('%I:%M %p') if not event.get('all_day') else 'All Day',
                'location': event.get('location', ''),
                'description': event.get('description', ''),
                'source': event['source'],
                'all_day': event.get('all_day', False)
            })
        
        set_cached_data(cache_key, formatted_events)
        return formatted_events
        
    except Exception as e:
        logging.error(f"Error fetching calendar events: {e}")
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        return []

# ==================== TRAFFIC & COMMUTE FUNCTIONS ====================
def get_commute_info(use_cache=True):
    """Fetch commute information with REAL-TIME traffic data using TomTom API"""
    cache_key = "commute_info"
    
    if use_cache:
        cached_data = get_cached_data(cache_key, max_age=300)  # 5 minute cache for traffic
        if cached_data:
            return cached_data
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key = 'commute_origin'")
        origin_result = c.fetchone()
        c.execute("SELECT value FROM settings WHERE key = 'commute_destination'")
        dest_result = c.fetchone()
        conn.close()
        
        if not origin_result or not dest_result:
            logging.warning("Commute origin or destination not configured")
            return {
                'error': 'No commute route configured. Please set origin and destination addresses above.',
                'traffic_events': []
            }
        
        origin = origin_result[0]
        destination = dest_result[0]
        
        # Use Nominatim (OpenStreetMap) for geocoding - free, no API key required
        geocode_url = "https://nominatim.openstreetmap.org/search"
        headers = {
            'User-Agent': 'RPI-Dashboard/1.0'
        }
        
        try:
            # Get coordinates for origin
            geo_params = {'q': origin, 'format': 'json', 'limit': 1}
            response = requests.get(geocode_url, params=geo_params, headers=headers, timeout=10)
            if response.status_code == 200:
                geo_data = response.json()
                if geo_data and len(geo_data) > 0:
                    origin_lat = float(geo_data[0]['lat'])
                    origin_lon = float(geo_data[0]['lon'])
                    logging.info(f"Geocoded origin: {origin} -> {origin_lat}, {origin_lon}")
                else:
                    return {'error': f'Could not find location for origin: {origin}', 'traffic_events': []}
            else:
                return {'error': 'Geocoding service error for origin.', 'traffic_events': []}
            
            time.sleep(1)  # Nominatim rate limit
            
            # Get coordinates for destination
            geo_params = {'q': destination, 'format': 'json', 'limit': 1}
            response = requests.get(geocode_url, params=geo_params, headers=headers, timeout=10)
            if response.status_code == 200:
                geo_data = response.json()
                if geo_data and len(geo_data) > 0:
                    dest_lat = float(geo_data[0]['lat'])
                    dest_lon = float(geo_data[0]['lon'])
                    logging.info(f"Geocoded destination: {destination} -> {dest_lat}, {dest_lon}")
                else:
                    return {'error': f'Could not find location for destination: {destination}', 'traffic_events': []}
            else:
                return {'error': 'Geocoding service error for destination.', 'traffic_events': []}
            
            time.sleep(1)  # Nominatim rate limit
            
            # FALLBACK ORDER: TomTom (real-time) → OpenRouteService → OSRM
            
            # 1. Try TomTom API first (REAL-TIME TRAFFIC DATA)
            # Free tier: 2,500 requests/day with actual traffic flow data
            if TOMTOM_API_KEY:
                try:
                    logging.info("Trying TomTom API for real-time traffic...")
                    commute_data = fetch_tomtom_route(origin, destination, origin_lat, origin_lon, dest_lat, dest_lon)
                    if commute_data and not commute_data.get('error'):
                        # Also fetch traffic incidents from TomTom
                        # Pass route_coordinates to filter incidents that are actually ON the route
                        route_coords = commute_data.get('route_coordinates', [])
                        incidents = fetch_tomtom_incidents(origin_lat, origin_lon, dest_lat, dest_lon, route_coords)
                        if incidents:
                            commute_data['traffic_events'].extend(incidents)
                        set_cached_data(cache_key, commute_data)
                        return commute_data
                    else:
                        logging.warning("TomTom API failed, falling back to OpenRouteService")
                except Exception as e:
                    logging.error(f"TomTom API error: {e}, falling back to OpenRouteService")
            
            # 2. Try OpenRouteService as second fallback
            if ORS_API_KEY:
                try:
                    logging.info("Trying OpenRouteService API...")
                    commute_data = fetch_ors_route(origin, destination, origin_lat, origin_lon, dest_lat, dest_lon)
                    if commute_data and not commute_data.get('error'):
                        set_cached_data(cache_key, commute_data)
                        return commute_data
                    else:
                        logging.warning("OpenRouteService failed, falling back to OSRM")
                except Exception as e:
                    logging.error(f"OpenRouteService error: {e}, falling back to OSRM")
            
            # 3. Final fallback to OSRM (no real-time traffic, but reliable)
            logging.info("Using OSRM as final fallback...")
            commute_data = fetch_osrm_route(origin, destination, origin_lat, origin_lon, dest_lat, dest_lon)
            if commute_data:
                set_cached_data(cache_key, commute_data)
                return commute_data
            
            return {'error': 'Failed to get route from all services.', 'traffic_events': []}
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error fetching commute info: {e}")
            return {'error': f'Network error: {str(e)}', 'traffic_events': []}
        except Exception as e:
            logging.error(f"Error fetching commute info: {e}")
            return {'error': f'Error: {str(e)}', 'traffic_events': []}
            
    except Exception as e:
        logging.error(f"Error in get_commute_info: {e}")
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        return {'error': f'Error loading commute info: {str(e)}', 'traffic_events': []}


def fetch_tomtom_route(origin, destination, origin_lat, origin_lon, dest_lat, dest_lon):
    """
    Fetch route with REAL-TIME traffic data from TomTom API.
    TomTom provides actual traffic flow data and congestion information.
    Free tier: 2,500 requests/day
    """
    try:
        # TomTom Calculate Route API with traffic
        # https://developer.tomtom.com/routing-api/documentation/routing/calculate-route
        url = f"https://api.tomtom.com/routing/1/calculateRoute/{origin_lat},{origin_lon}:{dest_lat},{dest_lon}/json"
        
        params = {
            'key': TOMTOM_API_KEY,
            'traffic': 'true',  # Enable real-time traffic
            'travelMode': 'car',
            'routeType': 'fastest',
            'sectionType': 'traffic',  # Get traffic sections
            'computeTravelTimeFor': 'all',  # Get both traffic and no-traffic times
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code != 200:
            logging.error(f"TomTom API error: {response.status_code} - {response.text[:200]}")
            return None
        
        data = response.json()
        
        if not data.get('routes') or len(data['routes']) == 0:
            logging.error("TomTom returned no routes")
            return None
        
        route = data['routes'][0]
        summary = route.get('summary', {})
        
        # Get distance and duration
        distance_m = summary.get('lengthInMeters', 0)
        duration_sec = summary.get('travelTimeInSeconds', 0)  # WITH traffic
        no_traffic_duration = summary.get('noTrafficTravelTimeInSeconds', duration_sec)  # WITHOUT traffic
        traffic_delay = summary.get('trafficDelayInSeconds', 0)
        
        distance_km = distance_m / 1000
        duration_min = int(duration_sec / 60)
        
        logging.info(f"TomTom route: {duration_min} min (traffic delay: {traffic_delay}s)")
        
        # Extract route coordinates from legs
        route_coordinates = []
        legs = route.get('legs', [])
        for leg in legs:
            points = leg.get('points', [])
            for point in points:
                route_coordinates.append([point['longitude'], point['latitude']])
        
        if not route_coordinates:
            logging.error("TomTom returned no route coordinates")
            return None
        
        # Process traffic sections for colored segments
        route_segments = []
        sections = route.get('sections', [])
        
        # Filter to only traffic sections
        traffic_sections = [s for s in sections if s.get('sectionType') == 'TRAFFIC']
        
        if traffic_sections:
            logging.info(f"TomTom returned {len(traffic_sections)} traffic sections")
            
            for section in traffic_sections:
                start_idx = section.get('startPointIndex', 0)
                end_idx = section.get('endPointIndex', len(route_coordinates) - 1)
                
                # Get traffic level from TomTom's simpleCategory
                # Values: JAM, SLOW, NORMAL, FREE_FLOW
                simple_category = section.get('simpleCategory', 'UNKNOWN')
                current_speed = section.get('currentSpeed', 0)  # km/h
                free_flow_speed = section.get('freeFlowSpeed', 0)  # km/h
                traffic_delay_sec = section.get('delayInSeconds', 0)
                
                # Map TomTom categories to our traffic levels
                if simple_category == 'JAM':
                    traffic_level = 'heavy'
                elif simple_category == 'SLOW':
                    traffic_level = 'medium'
                else:  # NORMAL, FREE_FLOW, or unknown
                    traffic_level = 'light'
                
                # Alternative: use speed ratio if available
                if free_flow_speed > 0 and current_speed > 0:
                    speed_ratio = current_speed / free_flow_speed
                    if speed_ratio < 0.4:
                        traffic_level = 'heavy'
                    elif speed_ratio < 0.7:
                        traffic_level = 'medium'
                    else:
                        traffic_level = 'light'
                
                # Extract coordinates for this section
                section_coords = route_coordinates[start_idx:end_idx + 1]
                
                if section_coords:
                    route_segments.append({
                        'traffic_level': traffic_level,
                        'coordinates': section_coords,
                        'current_speed_kmh': current_speed,
                        'free_flow_speed_kmh': free_flow_speed,
                        'delay_seconds': traffic_delay_sec,
                        'tomtom_category': simple_category
                    })
        
        # If no traffic sections, create segments based on overall delay
        if not route_segments:
            logging.info("No traffic sections from TomTom, creating segment from overall data")
            
            # Calculate overall traffic level from delay
            if no_traffic_duration > 0:
                delay_ratio = traffic_delay / no_traffic_duration
                if delay_ratio > 0.3:
                    traffic_level = 'heavy'
                elif delay_ratio > 0.1:
                    traffic_level = 'medium'
                else:
                    traffic_level = 'light'
            else:
                traffic_level = 'light'
            
            route_segments.append({
                'traffic_level': traffic_level,
                'coordinates': route_coordinates,
                'delay_seconds': traffic_delay
            })
        
        # Build traffic events list from heavy traffic segments
        traffic_events = []
        for i, segment in enumerate(route_segments):
            if segment['traffic_level'] in ['heavy', 'medium']:
                if segment.get('coordinates') and len(segment['coordinates']) > 0:
                    mid_idx = len(segment['coordinates']) // 2
                    mid_coord = segment['coordinates'][mid_idx]
                    
                    delay_min = segment.get('delay_seconds', 0) // 60
                    
                    traffic_events.append({
                        'type': 'traffic',
                        'traffic_level': segment['traffic_level'],
                        'location': f"Route segment {i + 1}",
                        'description': f"{segment['traffic_level'].capitalize()} traffic" + 
                                      (f" - {delay_min} min delay" if delay_min > 0 else ""),
                        'time': datetime.now(get_timezone()).strftime('%I:%M %p'),
                        'lat': mid_coord[1],
                        'lon': mid_coord[0]
                    })
        
        commute_data = {
            'origin': origin,
            'destination': destination,
            'origin_lat': origin_lat,
            'origin_lon': origin_lon,
            'dest_lat': dest_lat,
            'dest_lon': dest_lon,
            'distance_km': round(distance_km, 1),
            'distance_miles': round(distance_km * 0.621371, 1),
            'duration_minutes': duration_min,
            'duration_formatted': f"{duration_min} min",
            'no_traffic_duration_min': int(no_traffic_duration / 60),
            'traffic_delay_min': int(traffic_delay / 60),
            'route_coordinates': route_coordinates,
            'route_segments': route_segments,
            'traffic_events': traffic_events,
            'traffic_source': 'TomTom (Real-time)',
            'updated': datetime.now(get_timezone()).strftime('%I:%M %p')
        }
        
        logging.info(f"TomTom commute: {duration_min} min, {len(route_segments)} segments, {len(traffic_events)} traffic events")
        return commute_data
        
    except Exception as e:
        logging.error(f"Error in fetch_tomtom_route: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return None


def calculate_distance_to_route(incident_lat, incident_lon, route_coordinates):
    """
    Calculate the minimum distance from an incident to the route.
    Uses simple point-to-line-segment distance calculation.
    Returns distance in kilometers.
    """
    import math
    
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points in km"""
        R = 6371  # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    def point_to_segment_distance(px, py, x1, y1, x2, y2):
        """Calculate shortest distance from point to line segment"""
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return haversine_distance(py, px, y1, x1)
        
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return haversine_distance(py, px, proj_y, proj_x)
    
    if not route_coordinates or len(route_coordinates) < 2:
        return float('inf')
    
    min_distance = float('inf')
    
    # Check distance to each segment of the route
    # Sample every 5th point for performance on long routes
    step = max(1, len(route_coordinates) // 100)
    for i in range(0, len(route_coordinates) - 1, step):
        # Route coordinates are [lon, lat]
        lon1, lat1 = route_coordinates[i]
        j = min(i + step, len(route_coordinates) - 1)
        lon2, lat2 = route_coordinates[j]
        
        dist = point_to_segment_distance(incident_lon, incident_lat, lon1, lat1, lon2, lat2)
        min_distance = min(min_distance, dist)
        
        # Early exit if we found a very close match
        if min_distance < 0.1:  # Less than 100 meters
            break
    
    return min_distance


def fetch_tomtom_incidents(origin_lat, origin_lon, dest_lat, dest_lon, route_coordinates=None):
    """
    Fetch traffic incidents along the route from TomTom Traffic Incidents API.
    Only returns incidents that are actually ON or very close to the route.
    """
    if not TOMTOM_API_KEY:
        return []
    
    try:
        # Calculate bounding box for incidents (with some padding)
        min_lat = min(origin_lat, dest_lat) - 0.05
        max_lat = max(origin_lat, dest_lat) + 0.05
        min_lon = min(origin_lon, dest_lon) - 0.05
        max_lon = max(origin_lon, dest_lon) + 0.05
        
        # TomTom Traffic Incidents API
        url = "https://api.tomtom.com/traffic/services/5/incidentDetails"
        
        params = {
            'key': TOMTOM_API_KEY,
            'bbox': f"{min_lon},{min_lat},{max_lon},{max_lat}",
            'fields': '{incidents{type,geometry{type,coordinates},properties{iconCategory,magnitudeOfDelay,events{description,code},startTime,endTime,from,to,length,delay,roadNumbers}}}',
            'language': 'en-US',
            'categoryFilter': '0,1,2,3,4,5,6,7,8,9,10,11,14',  # All incident types
            'timeValidityFilter': 'present'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            logging.warning(f"TomTom Incidents API error: {response.status_code}")
            return []
        
        data = response.json()
        incidents = []
        
        # Maximum distance from route to consider incident relevant (in km)
        # 2.0 km = ~2000 meters = about 1.2 miles - shows nearby incidents for awareness
        # but they won't affect overall route status (that's calculated from route segments)
        MAX_DISTANCE_KM = 2.0
        
        # Incident type mapping
        incident_types = {
            0: ('Unknown', 'incident'),
            1: ('Accident', 'crash'),
            2: ('Fog', 'weather'),
            3: ('Dangerous Conditions', 'incident'),
            4: ('Rain', 'weather'),
            5: ('Ice', 'weather'),
            6: ('Jam', 'traffic'),
            7: ('Lane Closed', 'construction'),
            8: ('Road Closed', 'closure'),
            9: ('Road Works', 'construction'),
            10: ('Wind', 'weather'),
            11: ('Flooding', 'weather'),
            14: ('Broken Down Vehicle', 'incident')
        }
        
        total_incidents = len(data.get('incidents', []))
        filtered_count = 0
        
        for incident in data.get('incidents', []):
            props = incident.get('properties', {})
            geom = incident.get('geometry', {})
            
            # Get incident location
            coords = geom.get('coordinates', [])
            if not coords:
                continue
            
            # Handle different geometry types
            if geom.get('type') == 'Point':
                lat, lon = coords[1], coords[0]
            elif geom.get('type') == 'LineString' and len(coords) > 0:
                # Use midpoint of line
                mid_idx = len(coords) // 2
                lon, lat = coords[mid_idx][0], coords[mid_idx][1]
            else:
                continue
            
            # IMPORTANT: Check if incident is actually on/near the route
            if route_coordinates and len(route_coordinates) > 1:
                distance_to_route = calculate_distance_to_route(lat, lon, route_coordinates)
                if distance_to_route > MAX_DISTANCE_KM:
                    filtered_count += 1
                    continue  # Skip this incident - it's not on our route
            
            # Get incident type
            icon_cat = props.get('iconCategory', 0)
            type_name, incident_type = incident_types.get(icon_cat, ('Incident', 'incident'))
            
            # Get description from events
            events = props.get('events', [])
            description = events[0].get('description', type_name) if events else type_name
            
            # Get delay info
            delay_sec = props.get('delay', 0)
            delay_min = delay_sec // 60 if delay_sec else 0
            
            # Get road info
            road_numbers = props.get('roadNumbers', [])
            road_info = ', '.join(road_numbers) if road_numbers else ''
            from_loc = props.get('from', '')
            to_loc = props.get('to', '')
            
            location = road_info or from_loc or 'On route'
            if from_loc and to_loc:
                location = f"{from_loc} to {to_loc}"
            
            # Determine traffic level based on incident type and delay
            if incident_type == 'crash' or incident_type == 'closure':
                traffic_level = 'heavy'
            elif delay_min > 10:
                traffic_level = 'heavy'
            elif delay_min > 5 or incident_type == 'construction':
                traffic_level = 'medium'
            else:
                traffic_level = 'light'
            
            incidents.append({
                'type': incident_type,
                'traffic_level': traffic_level,
                'location': location,
                'description': f"{type_name}: {description}" + (f" (+{delay_min} min)" if delay_min > 0 else ""),
                'time': datetime.now(get_timezone()).strftime('%I:%M %p'),
                'lat': lat,
                'lon': lon,
                'delay_minutes': delay_min,
                'icon_category': icon_cat
            })
        
        logging.info(f"TomTom found {total_incidents} incidents in area, {filtered_count} filtered out (not on route), {len(incidents)} on route")
        return incidents
        
    except Exception as e:
        logging.error(f"Error fetching TomTom incidents: {e}")
        return []


def fetch_ors_route(origin, destination, origin_lat, origin_lon, dest_lat, dest_lon):
    """
    Fetch route from OpenRouteService API (second fallback).
    ORS provides some traffic-aware routing but not real-time incident data.
    Free tier: 2,000 requests/day
    """
    try:
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        
        headers = {
            'Authorization': ORS_API_KEY,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        body = {
            'coordinates': [[float(origin_lon), float(origin_lat)], [float(dest_lon), float(dest_lat)]],
            'geometry': True,
            'instructions': True
        }
        
        response = requests.post(url, json=body, headers=headers, timeout=15)
        
        if response.status_code == 401:
            logging.error("OpenRouteService authentication failed - check API key")
            return None
        elif response.status_code == 429:
            logging.warning("OpenRouteService rate limit exceeded")
            return None
        elif response.status_code != 200:
            logging.error(f"OpenRouteService API error: {response.status_code} - {response.text[:200]}")
            return None
        
        data = response.json()
        
        if not data.get('routes') or len(data['routes']) == 0:
            logging.error("OpenRouteService returned no routes")
            return None
        
        route = data['routes'][0]
        summary = route.get('summary', {})
        
        distance_m = summary.get('distance', 0)
        duration_sec = summary.get('duration', 0)
        distance_km = distance_m / 1000
        duration_min = int(duration_sec / 60)
        
        # Extract route geometry
        route_geometry = route.get('geometry', {})
        route_coordinates = []
        
        if isinstance(route_geometry, dict) and route_geometry.get('coordinates'):
            route_coordinates = route_geometry['coordinates']
        elif isinstance(route_geometry, list):
            route_coordinates = route_geometry
        
        if not route_coordinates:
            logging.error("OpenRouteService returned no coordinates")
            return None
        
        # Build segments from steps
        route_segments = []
        segments = route.get('segments', [])
        
        if segments:
            total_distance = sum(s.get('distance', 0) for s in segments)
            coord_index = 0
            
            for segment in segments:
                seg_distance = segment.get('distance', 0)
                seg_duration = segment.get('duration', 0)
                
                # Estimate traffic level based on average speed
                if seg_distance > 0 and seg_duration > 0:
                    avg_speed_kmh = (seg_distance / 1000) / (seg_duration / 3600)
                    
                    if avg_speed_kmh < 20:
                        traffic_level = 'heavy'
                    elif avg_speed_kmh < 40:
                        traffic_level = 'medium'
                    else:
                        traffic_level = 'light'
                else:
                    traffic_level = 'light'
                
                # Allocate coordinates proportionally
                if total_distance > 0:
                    proportion = seg_distance / total_distance
                    num_coords = max(1, int(len(route_coordinates) * proportion))
                    end_index = min(coord_index + num_coords, len(route_coordinates))
                    segment_coords = route_coordinates[coord_index:end_index]
                    coord_index = end_index
                    
                    if segment_coords:
                        route_segments.append({
                            'traffic_level': traffic_level,
                            'coordinates': segment_coords
                        })
        
        # If no segments, create single segment
        if not route_segments:
            route_segments.append({
                'traffic_level': 'light',
                'coordinates': route_coordinates
            })
        
        commute_data = {
            'origin': origin,
            'destination': destination,
            'origin_lat': origin_lat,
            'origin_lon': origin_lon,
            'dest_lat': dest_lat,
            'dest_lon': dest_lon,
            'distance_km': round(distance_km, 1),
            'distance_miles': round(distance_km * 0.621371, 1),
            'duration_minutes': duration_min,
            'duration_formatted': f"{duration_min} min",
            'route_coordinates': route_coordinates,
            'route_segments': route_segments,
            'traffic_events': [],  # ORS doesn't provide real-time incidents
            'traffic_source': 'OpenRouteService',
            'updated': datetime.now(get_timezone()).strftime('%I:%M %p')
        }
        
        logging.info(f"OpenRouteService commute: {duration_min} min, {len(route_segments)} segments")
        return commute_data
        
    except Exception as e:
        logging.error(f"Error in fetch_ors_route: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return None


def fetch_osrm_route(origin, destination, origin_lat, origin_lon, dest_lat, dest_lon):
    """
    Fetch route from OSRM (final fallback).
    NOTE: OSRM does NOT provide real-time traffic data.
    Traffic levels are estimated based on road types and typical speeds.
    """
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
        
        params = {
            'overview': 'full',
            'alternatives': 'false',
            'steps': 'true',
            'geometries': 'geojson',
            'annotations': 'speed,duration,distance'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code != 200:
            logging.error(f"OSRM API error: {response.status_code}")
            return None
        
        data = response.json()
        
        if data.get('code') != 'Ok' or not data.get('routes'):
            logging.error(f"OSRM error: {data.get('code', 'Unknown')}")
            return None
        
        route = data['routes'][0]
        distance_m = route.get('distance', 0)
        duration_sec = route.get('duration', 0)
        distance_km = distance_m / 1000
        duration_min = int(duration_sec / 60)
        
        route_geometry = route.get('geometry', {})
        route_coordinates = route_geometry.get('coordinates', [])
        
        if not route_coordinates:
            logging.error("OSRM returned no coordinates")
            return None
        
        # Build segments from annotations
        route_segments = []
        legs = route.get('legs', [])
        
        for leg in legs:
            annotation = leg.get('annotation', {})
            speeds = annotation.get('speed', [])
            
            if speeds and route_coordinates:
                current_traffic_level = None
                segment_start_idx = 0
                
                for i, speed_ms in enumerate(speeds):
                    if i >= len(route_coordinates) - 1:
                        break
                    
                    speed_kmh = speed_ms * 3.6
                    
                    if speed_kmh < 20:
                        traffic_level = 'heavy'
                    elif speed_kmh < 40:
                        traffic_level = 'medium'
                    else:
                        traffic_level = 'light'
                    
                    if current_traffic_level is None:
                        current_traffic_level = traffic_level
                        segment_start_idx = i
                    elif traffic_level != current_traffic_level or i == len(speeds) - 1:
                        end_idx = i + 1 if i == len(speeds) - 1 else i
                        segment_coords = route_coordinates[segment_start_idx:end_idx + 1]
                        
                        if segment_coords:
                            route_segments.append({
                                'traffic_level': current_traffic_level,
                                'coordinates': segment_coords
                            })
                        
                        current_traffic_level = traffic_level
                        segment_start_idx = i
                
                if current_traffic_level and segment_start_idx < len(route_coordinates):
                    segment_coords = route_coordinates[segment_start_idx:]
                    if segment_coords:
                        route_segments.append({
                            'traffic_level': current_traffic_level,
                            'coordinates': segment_coords
                        })
        
        if not route_segments:
            route_segments.append({
                'traffic_level': 'light',
                'coordinates': route_coordinates
            })
        
        commute_data = {
            'origin': origin,
            'destination': destination,
            'origin_lat': origin_lat,
            'origin_lon': origin_lon,
            'dest_lat': dest_lat,
            'dest_lon': dest_lon,
            'distance_km': round(distance_km, 1),
            'distance_miles': round(distance_km * 0.621371, 1),
            'duration_minutes': duration_min,
            'duration_formatted': f"{duration_min} min",
            'route_coordinates': route_coordinates,
            'route_segments': route_segments,
            'traffic_events': [],
            'traffic_source': 'OSRM (Estimated)',
            'updated': datetime.now(get_timezone()).strftime('%I:%M %p')
        }
        
        logging.info(f"OSRM commute: {duration_min} min, {len(route_segments)} segments")
        return commute_data
        
    except Exception as e:
        logging.error(f"Error in fetch_osrm_route: {e}")
        return None

# ==================== AIR QUALITY FUNCTIONS ====================
def get_air_quality(use_cache=True):
    """Fetch air quality data using OpenWeatherMap API"""
    cache_key = "air_quality"
    
    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/air_pollution"
        params = {
            'lat': WEATHER_LAT,
            'lon': WEATHER_LON,
            'appid': WEATHER_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        aqi = data['list'][0]['main']['aqi']
        components = data['list'][0]['components']
        
        aqi_levels = {
            1: {'name': 'Good', 'color': '#00e400'},
            2: {'name': 'Fair', 'color': '#ffff00'},
            3: {'name': 'Moderate', 'color': '#ff7e00'},
            4: {'name': 'Poor', 'color': '#ff0000'},
            5: {'name': 'Very Poor', 'color': '#8f3f97'}
        }
        
        level_info = aqi_levels.get(aqi, {'name': 'Unknown', 'color': '#666666'})
        
        air_quality_data = {
            'aqi': aqi,
            'level': level_info['name'],
            'color': level_info['color'],
            'pm25': round(components.get('pm2_5', 0), 1),
            'pm10': round(components.get('pm10', 0), 1),
            'no2': round(components.get('no2', 0), 1),
            'o3': round(components.get('o3', 0), 1),
            'updated': datetime.now(get_timezone()).strftime('%I:%M %p')
        }
        
        set_cached_data(cache_key, air_quality_data)
        return air_quality_data
        
    except Exception as e:
        logging.error(f"Error fetching air quality: {e}")
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        return None

# ==================== QUOTES FUNCTIONS ====================
# Fallback quotes if all APIs fail
FALLBACK_QUOTES = [
    {'text': 'The only way to do great work is to love what you do.', 'author': 'Steve Jobs'},
    {'text': 'Innovation distinguishes between a leader and a follower.', 'author': 'Steve Jobs'},
    {'text': 'Life is what happens to you while you\'re busy making other plans.', 'author': 'John Lennon'},
    {'text': 'The future belongs to those who believe in the beauty of their dreams.', 'author': 'Eleanor Roosevelt'},
    {'text': 'It is during our darkest moments that we must focus to see the light.', 'author': 'Aristotle'},
    {'text': 'The only impossible journey is the one you never begin.', 'author': 'Tony Robbins'},
    {'text': 'In the middle of difficulty lies opportunity.', 'author': 'Albert Einstein'},
    {'text': 'The way to get started is to quit talking and begin doing.', 'author': 'Walt Disney'},
    {'text': 'Don\'t let yesterday take up too much of today.', 'author': 'Will Rogers'},
    {'text': 'You learn more from failure than from success.', 'author': 'Unknown'}
]

def get_daily_quote(use_cache=True):
    """Fetch daily quote from multiple APIs with fallbacks"""
    cache_key = "daily_quote"
    
    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data:
            # Check if it's from today
            try:
                updated_str = cached_data.get('updated', '')
                if updated_str:
                    cached_time = datetime.strptime(updated_str, '%Y-%m-%d')
                    if cached_time.date() == datetime.now(get_timezone()).date():
                        return cached_data
            except (ValueError, TypeError) as e:
                logging.warning(f"Error parsing cached quote date: {e}")
                # Continue to fetch new quote
    
    # Try multiple quote APIs in order
    quote_apis = [
        {
            'name': 'quotable.io',
            'url': 'https://api.quotable.io/random',
            'parser': lambda data: {
                'text': data.get('content', ''),
                'author': data.get('author', 'Unknown')
            }
        },
        {
            'name': 'zenquotes.io',
            'url': 'https://zenquotes.io/api/random',
            'parser': lambda data: {
                'text': data[0].get('q', '') if isinstance(data, list) and len(data) > 0 else '',
                'author': data[0].get('a', 'Unknown') if isinstance(data, list) and len(data) > 0 else 'Unknown'
            }
        }
    ]
    
    # Try each API
    for api in quote_apis:
        try:
            logging.info(f"Attempting to fetch quote from {api['name']}")
            response = requests.get(api['url'], timeout=10)
            logging.debug(f"{api['name']} response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logging.debug(f"{api['name']} response data: {data}")
                
                parsed = api['parser'](data)
                quote_text = parsed.get('text', '').strip()
                author = parsed.get('author', 'Unknown').strip()
                
                if quote_text:
                    quote_data = {
                        'text': quote_text,
                        'author': author,
                        'updated': datetime.now(get_timezone()).strftime('%Y-%m-%d')
                    }
                    
                    # Save to history
                    save_quote_to_history(quote_text, author)
                    
                    # Cache the successful response
                    set_cached_data(cache_key, quote_data)
                    logging.info(f"Successfully fetched quote from {api['name']}")
                    return quote_data
                else:
                    logging.warning(f"{api['name']} returned empty quote text")
            else:
                logging.warning(f"{api['name']} returned status code {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.Timeout as e:
            logging.error(f"Timeout fetching quote from {api['name']}: {e}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error fetching quote from {api['name']}: {e}")
        except (KeyError, IndexError, TypeError) as e:
            logging.error(f"Error parsing response from {api['name']}: {e}, response: {response.text[:200] if 'response' in locals() else 'N/A'}")
        except Exception as e:
            logging.error(f"Unexpected error fetching quote from {api['name']}: {e}")
    
    # If all APIs failed, try cached data
    cached_data = get_cached_data(cache_key)
    if cached_data:
        logging.info("Using cached quote due to all API failures")
        return cached_data
    
    # Last resort: use fallback quote
    import random
    fallback_quote = random.choice(FALLBACK_QUOTES)
    quote_data = {
        'text': fallback_quote['text'],
        'author': fallback_quote['author'],
        'updated': datetime.now(get_timezone()).strftime('%Y-%m-%d')
    }
    
    # Save fallback quote to history
    save_quote_to_history(quote_data['text'], quote_data['author'])
    
    logging.info("Using fallback quote")
    return quote_data

# ==================== ASTRONOMY FUNCTIONS ====================
def get_astronomy_data(use_cache=True):
    """Calculate moon phase and sunrise/sunset times using astral library"""
    cache_key = "astronomy_data"
    
    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
    
    try:
        from astral import LocationInfo
        from astral.sun import sun
        from astral.moon import phase
        
        city = LocationInfo("Rotterdam", "NY", "US", float(WEATHER_LAT), float(WEATHER_LON))
        s = sun(city.observer, date=datetime.now(get_timezone()).date())
        
        moon_phase_value = phase(datetime.now(get_timezone()).date())
        moon_phases = {
            0: {'name': 'New Moon', 'icon': '🌑'},
            0.25: {'name': 'First Quarter', 'icon': '🌓'},
            0.5: {'name': 'Full Moon', 'icon': '🌕'},
            0.75: {'name': 'Last Quarter', 'icon': '🌗'}
        }
        
        # Find closest phase
        closest_phase = min(moon_phases.keys(), key=lambda x: abs(x - moon_phase_value))
        phase_info = moon_phases[closest_phase]
        
        # Calculate percentage
        if moon_phase_value < 0.25:
            percentage = (moon_phase_value / 0.25) * 25
        elif moon_phase_value < 0.5:
            percentage = 25 + ((moon_phase_value - 0.25) / 0.25) * 25
        elif moon_phase_value < 0.75:
            percentage = 50 + ((moon_phase_value - 0.5) / 0.25) * 25
        else:
            percentage = 75 + ((moon_phase_value - 0.75) / 0.25) * 25
        
        ny_tz = get_timezone()
        sunrise = s['sunrise'].astimezone(ny_tz)
        sunset = s['sunset'].astimezone(ny_tz)
        
        astronomy_data = {
            'moon_phase': round(moon_phase_value, 2),
            'moon_phase_name': phase_info['name'],
            'moon_icon': phase_info['icon'],
            'moon_percentage': round(percentage),
            'sunrise': sunrise.strftime('%I:%M %p'),
            'sunset': sunset.strftime('%I:%M %p'),
            'updated': datetime.now(get_timezone()).strftime('%I:%M %p')
        }
        
        set_cached_data(cache_key, astronomy_data)
        return astronomy_data
        
    except ImportError:
        logging.error("astral library not installed. Install with: pip install astral")
        return None
    except Exception as e:
        logging.error(f"Error calculating astronomy data: {e}")
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        return None

# ==================== INTERNET SPEED TEST FUNCTIONS ====================
speed_test_running = False
last_speed_test = None

def run_speed_test():
    """Run internet speed test in background"""
    global speed_test_running, last_speed_test
    
    if speed_test_running:
        return
    
    speed_test_running = True
    try:
        import speedtest
        st = speedtest.Speedtest()
        st.get_best_server()
        
        download_mbps = st.download() / 1000000  # Convert to Mbps
        upload_mbps = st.upload() / 1000000  # Convert to Mbps
        ping_ms = st.results.ping
        
        # Save to database
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO speed_tests (download_mbps, upload_mbps, ping_ms)
            VALUES (?, ?, ?)
        """, (download_mbps, upload_mbps, ping_ms))
        conn.commit()
        conn.close()
        
        last_speed_test = {
            'download_mbps': round(download_mbps, 2),
            'upload_mbps': round(upload_mbps, 2),
            'ping_ms': round(ping_ms, 2),
            'timestamp': datetime.now(get_timezone()).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logging.info(f"Speed test completed: {download_mbps:.2f} Mbps down, {upload_mbps:.2f} Mbps up")
    except ImportError:
        logging.error("speedtest-cli library not installed. Install with: pip install speedtest-cli")
    except Exception as e:
        logging.error(f"Error running speed test: {e}")
    finally:
        speed_test_running = False

def get_internet_speed():
    """Get latest internet speed test results"""
    global last_speed_test
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            SELECT download_mbps, upload_mbps, ping_ms, timestamp
            FROM speed_tests
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        result = c.fetchone()
        conn.close()
        
        if result:
            download, upload, ping, timestamp = result
            return {
                'download_mbps': round(download, 2),
                'upload_mbps': round(upload, 2),
                'ping_ms': round(ping, 2),
                'timestamp': timestamp,
                'last_test': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
            }
        else:
            return None
    except Exception as e:
        logging.error(f"Error getting speed test results: {e}")
        return None

# ==================== SPORTS SCORES FUNCTIONS ====================
def get_sports_scores(use_cache=True):
    """Fetch sports scores using TheSportsDB API"""
    cache_key = "sports_scores"
    
    # Check cache first (5 minute cache to avoid rate limiting)
    if use_cache:
        cached = get_cached_data(cache_key, max_age=300)  # 5 minutes
        if cached:
            logging.info("Using cached sports scores")
            return cached
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key = 'sports_teams'")
        teams_result = c.fetchone()
        conn.close()
        
        if not teams_result:
            return []
        
        try:
            teams = json.loads(teams_result[0])
        except:
            teams = []
        
        if not teams:
            return []
        
        all_scores = []
        
        # Use TheSportsDB API (free, no key required)
        # Reduced timeout to 5 seconds and limit to 3 teams for faster response
        for team_data in teams[:3]:  # Limit to 3 teams for faster loading
            try:
                # Handle both old format (string) and new format (object with name and sport)
                if isinstance(team_data, dict):
                    team_name = team_data.get('name', '').strip()
                    required_sport = team_data.get('sport', '').strip()
                    logging.info(f"Processing team: name='{team_name}', sport='{required_sport}'")
                    
                    # CRITICAL: If sport is empty, set to None so we know to skip filtering
                    if not required_sport:
                        required_sport = None
                else:
                    # Old format - just a string
                    team_name = str(team_data).strip() if team_data else ''
                    required_sport = None
                    logging.info(f"Processing team (old format): name='{team_name}'")
                
                if not team_name:
                    logging.warning(f"Empty team name, skipping")
                    continue
                
                team_name_lower = team_name.lower()
                
                # Search for team with timeout
                search_url = f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={team_name}"
                logging.info(f"API URL: {search_url}")
                try:
                    response = requests.get(search_url, timeout=5)
                    logging.info(f"API status: {response.status_code}")
                except Exception as api_err:
                    logging.error(f"API ERROR: {api_err}")
                    continue
                    
                if response.status_code == 200:
                    data = response.json()
                    if data.get('teams') and len(data['teams']) > 0:
                        logging.info(f"API returned {len(data['teams'])} teams for '{team_name}'")
                        
                        # CRITICAL: If we have a required sport, ONLY use teams from that sport - NO EXCEPTIONS
                        logging.info(f"required_sport value = '{required_sport}' (type: {type(required_sport).__name__}, bool: {bool(required_sport)})")
                        
                        if required_sport:
                            original_count = len(data['teams'])
                            filtered_teams = []
                            required_sport_lower = required_sport.lower()
                            
                            for t in data['teams']:
                                sport = t.get('strSport', '').strip()
                                sport_lower = sport.lower().strip()
                                
                                # Log what we're comparing for debugging
                                logging.info(f"Comparing: required_sport='{required_sport_lower}' vs API sport='{sport_lower}' for team '{t.get('strTeam')}'")
                                
                                # Must match the required sport type exactly (case-insensitive, whitespace trimmed)
                                if sport_lower == required_sport_lower:
                                    filtered_teams.append(t)
                                    logging.info(f"✓ MATCH: Team '{t.get('strTeam')}' sport '{sport}' matches required '{required_sport}'")
                                else:
                                    logging.info(f"✗ NO MATCH: Team '{t.get('strTeam')}' sport '{sport}' does NOT match required '{required_sport}' - SKIPPING")
                            
                            # ONLY use filtered teams - if none found, skip this team entirely
                            if filtered_teams:
                                data['teams'] = filtered_teams
                                logging.info(f"Filtered '{team_name}': {original_count} -> {len(filtered_teams)} teams (sport={required_sport})")
                            else:
                                # Log all available sports for debugging
                                available_sports = [t.get('strSport', 'Unknown') for t in data['teams']]
                                logging.error(f"No teams found matching sport='{required_sport}' for '{team_name}'. Available sports: {set(available_sports)}")
                                continue
                        else:
                            # No sport specified - try to filter out foreign soccer teams at least
                            logging.warning(f"No sport specified for '{team_name}' - filtering out foreign soccer teams")
                            original_count = len(data['teams'])
                            filtered_teams = []
                            for t in data['teams']:
                                sport = t.get('strSport', '').lower()
                                country = t.get('strCountry', '').lower()
                                league = t.get('strLeague', '').upper()
                                
                                # Exclude foreign soccer teams
                                is_foreign_soccer = (
                                    sport == 'soccer' and 
                                    country not in ['united states', 'usa', ''] and
                                    'mls' not in league
                                )
                                
                                if not is_foreign_soccer:
                                    filtered_teams.append(t)
                            
                            if filtered_teams:
                                data['teams'] = filtered_teams
                                logging.info(f"Filtered '{team_name}': {original_count} -> {len(filtered_teams)} teams (removed foreign soccer)")
                            # If no filtered teams, use all teams (shouldn't happen but just in case)
                        
                        # Try to find the best matching team
                        # Since we've already filtered by sport/league, all teams in data['teams'] are valid
                        team = None
                        team_name_words_list = team_name_lower.split()
                        
                        # First, try exact match (case-insensitive)
                        for t in data['teams']:
                            if t.get('strTeam', '').lower() == team_name_lower:
                                team = t
                                logging.info(f"Found exact match for '{team_name}': {t.get('strTeam')} ({t.get('strSport')}, {t.get('strLeague')})")
                                break
                        
                        # If no exact match, try partial match (teams already filtered by sport)
                        if not team:
                            for t in data['teams']:
                                team_str = t.get('strTeam', '').lower()
                                # Check if team name is contained in the result or vice versa
                                if team_name_lower in team_str or team_str in team_name_lower:
                                    team = t
                                    logging.info(f"Found partial match for '{team_name}': {t.get('strTeam')} ({t.get('strSport')}, {t.get('strLeague')})")
                                    break
                        
                        # If still no match, use first team (already filtered by sport/league)
                        if not team and data['teams']:
                            team = data['teams'][0]
                            logging.info(f"Using first filtered team for '{team_name}': {team.get('strTeam')} ({team.get('strSport')}, {team.get('strLeague')})")
                        
                        # If we still don't have a team, skip
                        if not team:
                            logging.warning(f"No team found for '{team_name}' - skipping")
                            continue
                        
                        # Log which team was selected for debugging
                        selected_team_name = team.get('strTeam', 'Unknown')
                        selected_sport = team.get('strSport', 'Unknown')
                        selected_league = team.get('strLeague', 'Unknown')
                        team_id = team.get('idTeam')
                        
                        logging.info(f"SELECTED: {selected_team_name} | Sport: {selected_sport} | ID: {team_id}")
                        
                        # Get next event with shorter timeout
                        # First try the team's next event endpoint
                        upcoming_found = False
                        try:
                            events_url = f"https://www.thesportsdb.com/api/v1/json/3/eventsnext.php?id={team_id}"
                            response = requests.get(events_url, timeout=3)
                            if response.status_code == 200:
                                events_data = response.json()
                                if events_data.get('events'):
                                    # Find an event that matches our sport
                                    for event in events_data['events']:
                                        event_sport = event.get('strSport', '').lower()
                                        event_name = event.get('strEvent', '').lower()
                                        
                                        # Check if sport matches AND team name appears in event
                                        sport_ok = not required_sport or event_sport == required_sport.lower()
                                        team_in_event = selected_team_name.lower() in event_name
                                        
                                        if sport_ok and team_in_event:
                                            all_scores.append({
                                                'team': team_name,
                                                'event': event.get('strEvent', ''),
                                                'date': event.get('dateEvent', ''),
                                                'time': event.get('strTime', ''),
                                                'league': event.get('strLeague', ''),
                                                'status': 'Upcoming'
                                            })
                                            upcoming_found = True
                                            break
                        except requests.exceptions.Timeout:
                            logging.warning(f"Timeout fetching next event for {team_name}")
                        except Exception as e:
                            logging.warning(f"Error fetching next event for {team_name}: {e}")
                        
                        # If no upcoming event found and we have a league, try league schedule
                        if not upcoming_found and team.get('idLeague'):
                            try:
                                league_id = team.get('idLeague')
                                league_url = f"https://www.thesportsdb.com/api/v1/json/3/eventsnextleague.php?id={league_id}"
                                response = requests.get(league_url, timeout=3)
                                if response.status_code == 200:
                                    league_data = response.json()
                                    if league_data.get('events'):
                                        # Find events involving our team
                                        for event in league_data['events'][:20]:  # Check first 20 events
                                            event_name = event.get('strEvent', '').lower()
                                            if selected_team_name.lower() in event_name:
                                                all_scores.append({
                                                    'team': team_name,
                                                    'event': event.get('strEvent', ''),
                                                    'date': event.get('dateEvent', ''),
                                                    'time': event.get('strTime', ''),
                                                    'league': event.get('strLeague', ''),
                                                    'status': 'Upcoming'
                                                })
                                                break
                            except Exception as e:
                                logging.warning(f"Error fetching league events for {team_name}: {e}")
                        
                        # Get last result with shorter timeout
                        try:
                            results_url = f"https://www.thesportsdb.com/api/v1/json/3/eventslast.php?id={team_id}"
                            response = requests.get(results_url, timeout=3)
                            if response.status_code == 200:
                                results_data = response.json()
                                if results_data.get('results'):
                                    # Find a result that matches our sport
                                    for result in results_data['results']:
                                        event_sport = result.get('strSport', '').lower()
                                        
                                        # Only check sport matches if we have a required sport
                                        if required_sport and event_sport != required_sport.lower():
                                            continue  # Skip events from wrong sport
                                        
                                        all_scores.append({
                                            'team': team_name,
                                            'event': result.get('strEvent', ''),
                                            'score': f"{result.get('intHomeScore', '?')} - {result.get('intAwayScore', '?')}",
                                            'date': result.get('dateEvent', ''),
                                            'league': result.get('strLeague', ''),
                                            'status': 'Completed'
                                        })
                                        break
                        except requests.exceptions.Timeout:
                            logging.warning(f"Timeout fetching last result for {team_name}")
                        except Exception as e:
                            logging.warning(f"Error fetching last result for {team_name}: {e}")
            except requests.exceptions.Timeout:
                logging.warning(f"Timeout searching for team {team_name}")
                continue
            except Exception as e:
                logging.error(f"Error fetching sports data for {team_name}: {e}")
                continue
        
        set_cached_data(cache_key, all_scores)
        logging.info(f"Fetched {len(all_scores)} sports scores")
        return all_scores
        
    except Exception as e:
        logging.error(f"Error fetching sports scores: {e}")
        cached_data = get_cached_data(cache_key)
        if cached_data:
            logging.info("Using cached sports scores due to error")
            return cached_data
        return []

# ==================== PHOTO GALLERY FUNCTIONS ====================
def get_photos():
    """Get list of photos from gallery directory"""
    gallery_dir = os.path.join('static', 'images', 'gallery')
    
    if not os.path.exists(gallery_dir):
        os.makedirs(gallery_dir, exist_ok=True)
    
    photos = []
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    
    try:
        for filename in os.listdir(gallery_dir):
            if any(filename.lower().endswith(ext) for ext in allowed_extensions):
                filepath = os.path.join(gallery_dir, filename)
                file_size = os.path.getsize(filepath)
                file_time = os.path.getmtime(filepath)
                photos.append({
                    'filename': filename,
                    'url': f'/static/images/gallery/{filename}',
                    'size': file_size,
                    'uploaded': datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Sort by upload time (newest first)
        photos.sort(key=lambda x: x['uploaded'], reverse=True)
        return photos
    except Exception as e:
        logging.error(f"Error getting photos: {e}")
        return []

def get_joke(use_cache=True, retry_count=3):
    """Fetch a random joke from Ollama AI with caching and retry logic, with fallback server"""
    cache_key = "joke_data"
    
    # Try to get cached data first
    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
    
    # List of Ollama servers to try (primary first, then fallback)
    ollama_servers = [OLLAMA_URL, OLLAMA_FALLBACK_URL]
    
    # If no cache or cache expired, fetch from Ollama API with retries
    for attempt in range(retry_count):
        # Try each server for this attempt
        for server_url in ollama_servers:
            try:
                url = f"{server_url}/api/generate"
                payload = {
                    "model": OLLAMA_MODEL,
                    "prompt": "Tell me a funny, family-friendly joke. Keep it short and appropriate for all ages.",
                    "stream": False
                }
                
                logging.info(f"Attempting to fetch joke from {server_url} (attempt {attempt + 1}/{retry_count})")
                response = requests.post(url, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
                
                # Extract joke text from response
                joke_text = data.get('response', '').strip()
                
                if joke_text:
                    joke_data = {
                        'text': joke_text,
                        'updated': datetime.now(get_timezone()).strftime('%I:%M %p')
                    }
                    
                    # Save to history
                    save_joke_to_history(joke_text)
                    
                    # Cache the successful response
                    set_cached_data(cache_key, joke_data)
                    logging.info(f"Successfully fetched joke from Ollama server: {server_url}")
                    return joke_data
                else:
                    logging.warning(f"Ollama server {server_url} returned empty joke response")
                    
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to fetch joke from {server_url} (attempt {attempt + 1}/{retry_count}): {e}")
                # Continue to next server or retry
                continue
            except Exception as e:
                logging.error(f"Error processing joke response from {server_url} (attempt {attempt + 1}/{retry_count}): {e}")
                # Continue to next server or retry
                continue
        
        # If all servers failed for this attempt, wait before retrying
        if attempt < retry_count - 1:
            time.sleep(2)  # Wait before retry
    
    # If all attempts failed, try to return cached data even if expired
    cached_data = get_cached_data(cache_key)
    if cached_data:
        logging.info("Using expired cache due to API failure")
        return cached_data
    
    # If everything fails, return a helpful error message
    logging.error("Failed to fetch joke from all Ollama servers")
    return {
        'text': 'Unable to fetch a joke at this time. Please try again later.',
        'updated': datetime.now(get_timezone()).strftime('%I:%M %p')
    }

# ==================== PACKAGE TRACKING FUNCTIONS ====================
def detect_carrier(tracking_number):
    """Detect carrier from tracking number format"""
    tracking = tracking_number.strip().replace(' ', '').replace('-', '')
    
    # USPS: 20-22 digits, often starts with 9
    if tracking.isdigit() and len(tracking) >= 20 and len(tracking) <= 22:
        if tracking.startswith('9'):
            return 'USPS'
        return 'USPS'  # Most USPS tracking numbers are 20-22 digits
    
    # UPS: 18 characters, alphanumeric, often starts with 1Z
    if len(tracking) == 18 and tracking.startswith('1Z'):
        return 'UPS'
    
    # FedEx: 12-14 digits, or alphanumeric patterns
    if tracking.isdigit() and (len(tracking) == 12 or len(tracking) == 14):
        return 'FedEx'
    if len(tracking) >= 12 and len(tracking) <= 14 and any(c.isalpha() for c in tracking):
        return 'FedEx'
    
    # Amazon: varies - often 10-11 digits or alphanumeric starting with TBA
    if tracking.startswith('TBA') or tracking.startswith('TBC'):
        return 'Amazon'
    if len(tracking) >= 10 and len(tracking) <= 11:
        return 'Amazon'
    
    # Default to USPS if uncertain
    return 'USPS'

def get_package_status(tracking_number, carrier):
    """Fetch package tracking status from carrier using public tracking pages"""
    tracking = tracking_number.strip().replace(' ', '').replace('-', '')
    
    try:
        # Try using AfterShip public tracking (no API key required for basic lookups)
        # Alternative: use carrier-specific public tracking pages
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Try carrier-specific tracking URLs and parse basic info
        # Note: This is a simplified implementation - full parsing would require BeautifulSoup
        if carrier == 'USPS':
            url = f"https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking}"
        elif carrier == 'UPS':
            url = f"https://www.ups.com/track?tracknum={tracking}"
        elif carrier == 'FedEx':
            url = f"https://www.fedex.com/fedextrack/?trknbr={tracking}"
        elif carrier == 'Amazon':
            # Amazon tracking varies - use generic status
            return {
                'status': 'In Transit',
                'last_location': 'Processing',
                'estimated_delivery': None
            }
        else:
            url = None
        
        if url:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    # Basic status detection from response
                    content = response.text.lower()
                    if 'delivered' in content:
                        return {
                            'status': 'Delivered',
                            'last_location': 'Delivered',
                            'estimated_delivery': None
                        }
                    elif 'out for delivery' in content:
                        return {
                            'status': 'Out for Delivery',
                            'last_location': 'Out for Delivery',
                            'estimated_delivery': None
                        }
                    elif 'in transit' in content or 'tracking' in content:
                        return {
                            'status': 'In Transit',
                            'last_location': 'In Transit',
                            'estimated_delivery': None
                        }
            except Exception as e:
                logging.debug(f"Error parsing tracking page: {e}")
        
        # Default status if unable to determine
        return {
            'status': 'In Transit',
            'last_location': 'Processing',
            'estimated_delivery': None
        }
        
    except Exception as e:
        logging.error(f"Error fetching package status for {tracking_number}: {e}")
        return {
            'status': 'Error',
            'last_location': '',
            'estimated_delivery': None
        }

# ==================== WEATHER ALERTS FUNCTIONS ====================
def get_weather_alerts(use_cache=True):
    """Fetch weather alerts from NWS API (free, no API key required)"""
    cache_key = "weather_alerts"
    
    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
    
    try:
        # NWS API endpoint - no API key required
        url = f"https://api.weather.gov/alerts/active?point={WEATHER_LAT},{WEATHER_LON}"
        headers = {
            'User-Agent': 'HomeDashboard/1.0 (contact@example.com)'  # NWS requires User-Agent
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        alerts = []
        if 'features' in data and data['features']:
            for feature in data['features']:
                properties = feature.get('properties', {})
                alert_id = properties.get('id', '')
                
                # Check if alert already exists in database
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute("SELECT id FROM weather_alerts WHERE alert_id = ?", (alert_id,))
                exists = c.fetchone()
                
                if not exists:
                    # Insert new alert
                    c.execute('''
                        INSERT INTO weather_alerts (alert_id, alert_type, severity, headline, description, area, effective, expires)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        alert_id,
                        properties.get('event', 'Unknown'),
                        properties.get('severity', 'Unknown'),
                        properties.get('headline', ''),
                        properties.get('description', ''),
                        properties.get('areaDesc', ''),
                        properties.get('effective'),
                        properties.get('expires')
                    ))
                    conn.commit()
                
                # Format alert for response
                effective_str = properties.get('effective', '')
                expires_str = properties.get('expires', '')
                
                alerts.append({
                    'id': alert_id,
                    'type': properties.get('event', 'Unknown'),
                    'severity': properties.get('severity', 'Unknown'),
                    'headline': properties.get('headline', ''),
                    'description': properties.get('description', ''),
                    'area': properties.get('areaDesc', ''),
                    'effective': effective_str,
                    'expires': expires_str
                })
            
            conn.close()
        
        # Cache for 5 minutes
        set_cached_data(cache_key, alerts)
        logging.info(f"Fetched {len(alerts)} weather alerts")
        return alerts
        
    except Exception as e:
        logging.error(f"Error fetching weather alerts: {e}")
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        return []

# ==================== HOME ASSISTANT FUNCTIONS ====================
def get_ha_states(use_cache=True):
    """Fetch all entity states from Home Assistant API"""
    if not HA_URL or not HA_TOKEN:
        logging.warning("Home Assistant not configured")
        return []
    
    cache_key = "ha_states"
    
    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
    
    try:
        url = f"{HA_URL}/api/states"
        headers = {
            'Authorization': f'Bearer {HA_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Cache for 1 minute
        set_cached_data(cache_key, data)
        logging.info(f"Fetched {len(data)} Home Assistant entities")
        return data
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching Home Assistant states: {e}")
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        return []
    except Exception as e:
        logging.error(f"Unexpected error fetching Home Assistant states: {e}")
        return []

def filter_ha_devices(entities, for_dashboard=False):
    """Filter Home Assistant entities based on criteria"""
    if not entities:
        return []
    
    # Device domains that can be "on"
    device_domains = ['light', 'switch', 'binary_sensor', 'fan', 'climate', 'media_player', 'cover', 'lock']
    
    devices = []
    for entity in entities:
        entity_id = entity.get('entity_id', '')
        domain = entity_id.split('.')[0] if '.' in entity_id else ''
        state = entity.get('state', '').lower()
        
        # Skip if not a device domain
        if domain not in device_domains:
            continue
        
        # For dashboard: only show devices that are "on"
        if for_dashboard:
            if state == 'on':
                devices.append(entity)
        else:
            # For index page: show all devices
            devices.append(entity)
    
    return devices

def filter_ha_battery_sensors(entities, for_dashboard=False):
    """Filter battery sensors from Home Assistant entities"""
    if not entities:
        return []
    
    battery_sensors = []
    for entity in entities:
        entity_id = entity.get('entity_id', '').lower()
        attributes = entity.get('attributes', {})
        state = entity.get('state', '')
        
        # Check if it's a battery sensor
        is_battery = 'battery' in entity_id or 'battery_level' in entity_id
        
        if not is_battery:
            continue
        
        # Try to get battery level from attributes or state
        battery_level = None
        if 'battery' in attributes:
            try:
                battery_level = float(attributes['battery'])
            except (ValueError, TypeError):
                pass
        elif 'battery_level' in attributes:
            try:
                battery_level = float(attributes['battery_level'])
            except (ValueError, TypeError):
                pass
        elif state.replace('.', '').replace('-', '').isdigit():
            try:
                battery_level = float(state)
            except (ValueError, TypeError):
                pass
        
        if battery_level is not None:
            # For dashboard: only show sensors with battery < 25%
            if for_dashboard:
                if battery_level < 25:
                    battery_sensors.append({
                        **entity,
                        'battery_level': battery_level
                    })
            else:
                # For index page: show all battery sensors
                battery_sensors.append({
                    **entity,
                    'battery_level': battery_level
                })
    
    return battery_sensors

# ==================== SWITCHBOT FUNCTIONS ====================
def generate_switchbot_signature():
    """Generate HMAC-SHA256 signature for SwitchBot API authentication"""
    t = int(round(time.time() * 1000))
    nonce = ''
    string_to_sign = f'{SWITCHBOT_TOKEN}{t}{nonce}'
    sign = base64.b64encode(
        hmac.new(
            SWITCHBOT_SECRET.encode(),
            msg=string_to_sign.encode(),
            digestmod=hashlib.sha256
        ).digest()
    ).decode()
    headers = {
        'Authorization': SWITCHBOT_TOKEN,
        'sign': sign,
        't': str(t),
        'nonce': nonce,
        'Content-Type': 'application/json'
    }
    return headers

def get_switchbot_lock_status(use_cache=True):
    """Fetch lock statuses from SwitchBot API with caching"""
    if not SWITCHBOT_TOKEN or not SWITCHBOT_SECRET or not SWITCHBOT_LOCK_IDS:
        logging.warning("SwitchBot not configured")
        return []
    
    cache_key = "switchbot_locks"
    
    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
    
    locks = []
    headers = generate_switchbot_signature()
    
    for lock_device_id in SWITCHBOT_LOCK_IDS:
        try:
            url = f'https://api.switch-bot.com/v1.1/devices/{lock_device_id}/status'
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            lock_data = response.json()
            lock_state = lock_data.get('body', {}).get('lockState')
            
            if lock_state is not None:
                locks.append({
                    'device_id': lock_device_id,
                    'name': f'Lock {lock_device_id[-4:]}',  # Use last 4 chars as name
                    'status': lock_state.lower()  # 'locked' or 'unlocked'
                })
                logging.info(f"SwitchBot lock {lock_device_id} status: {lock_state}")
            else:
                locks.append({
                    'device_id': lock_device_id,
                    'name': f'Lock {lock_device_id[-4:]}',
                    'status': 'unknown'
                })
                logging.error(f"'lockState' not found for lock {lock_device_id}")
                
        except requests.RequestException as e:
            logging.error(f"Error checking lock {lock_device_id} status: {e}")
            locks.append({
                'device_id': lock_device_id,
                'name': f'Lock {lock_device_id[-4:]}',
                'status': 'error'
            })
        except Exception as e:
            logging.error(f"Unexpected error checking lock {lock_device_id}: {e}")
            locks.append({
                'device_id': lock_device_id,
                'name': f'Lock {lock_device_id[-4:]}',
                'status': 'error'
            })
    
    # Cache the successful response (cache even if some locks failed)
    if locks:
        set_cached_data(cache_key, locks)
    
    return locks

# ==================== HOLIDAY THEMING FUNCTIONS ====================
def calculate_easter(year):
    """Calculate Easter date for a given year using the Anonymous Gregorian algorithm"""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(year, month, day)

def get_current_holiday(test_holiday=None):
    """Get current holiday theme data"""
    # Use configured timezone for holiday detection
    ny_tz = get_timezone()
    today = datetime.now(ny_tz).date()
    
    # Check for test holiday override
    if test_holiday:
        holiday_name = test_holiday.lower()
    else:
        # Check database for test holiday setting
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT value FROM settings WHERE key = 'test_holiday'")
            result = c.fetchone()
            conn.close()
            if result and result[0]:
                holiday_name = result[0].lower()
            else:
                holiday_name = None
        except:
            holiday_name = None
    
    # If no test holiday, detect actual holiday
    if not holiday_name:
        # Use holidays library if available
        if HOLIDAYS_AVAILABLE:
            us_holidays = holidays.UnitedStates(years=today.year)
            holiday_list = us_holidays.get(today)
            if holiday_list:
                # holidays library returns a list or string
                if isinstance(holiday_list, list):
                    holiday_str = holiday_list[0] if holiday_list else None
                else:
                    holiday_str = holiday_list
                
                if holiday_str:
                    # Map common holiday names to our theme names
                    holiday_str_lower = holiday_str.lower()
                    if 'new year' in holiday_str_lower:
                        holiday_name = 'new_year'
                    elif 'martin luther king' in holiday_str_lower or 'mlk' in holiday_str_lower:
                        holiday_name = None  # No theme for MLK Day
                    elif 'president' in holiday_str_lower or 'washington' in holiday_str_lower:
                        holiday_name = None  # No theme for Presidents Day
                    elif 'memorial' in holiday_str_lower:
                        holiday_name = None  # No theme for Memorial Day
                    elif 'independence' in holiday_str_lower or 'july' in holiday_str_lower:
                        holiday_name = 'july_4th'
                    elif 'labor' in holiday_str_lower:
                        holiday_name = None  # No theme for Labor Day
                    elif 'columbus' in holiday_str_lower:
                        holiday_name = None  # No theme for Columbus Day
                    elif 'veterans' in holiday_str_lower:
                        holiday_name = None  # No theme for Veterans Day
                    elif 'thanksgiving' in holiday_str_lower:
                        holiday_name = 'thanksgiving'
                    elif 'christmas' in holiday_str_lower:
                        holiday_name = 'christmas'
        
        # Manual date checking for holidays not in library or for fallback
        if not holiday_name:
            month = today.month
            day = today.day
            
            # New Year (Jan 1)
            if month == 1 and day == 1:
                holiday_name = 'new_year'
                logging.info("New Year's Day detected")
            # Valentine's Day (Feb 14)
            elif month == 2 and day == 14:
                holiday_name = 'valentines'
                logging.info("Valentine's Day detected")
            # St. Patrick's Day (Mar 17)
            elif month == 3 and day == 17:
                holiday_name = 'st_patricks'
                logging.info("St. Patrick's Day detected")
            # Easter (calculated)
            elif month in [3, 4]:
                easter_date = calculate_easter(today.year)
                if today == easter_date.date():
                    holiday_name = 'easter'
                    logging.info(f"Easter detected: {easter_date.date()}")
            # 4th of July (Jul 4)
            elif month == 7 and day == 4:
                holiday_name = 'july_4th'
                logging.info("4th of July detected")
            # Halloween (Oct 31)
            elif month == 10 and day == 31:
                holiday_name = 'halloween'
                logging.info("Halloween detected")
            # Thanksgiving (4th Thursday of November)
            elif month == 11:
                # Find 4th Thursday
                first_day = datetime(today.year, 11, 1).weekday()
                # 0 = Monday, 3 = Thursday
                # Calculate days until first Thursday
                days_until_thursday = (3 - first_day) % 7
                if days_until_thursday == 0:
                    days_until_thursday = 7
                # 4th Thursday = 1st Thursday + 21 days
                thanksgiving_day = 1 + days_until_thursday + 21
                if day == thanksgiving_day:
                    holiday_name = 'thanksgiving'
                    logging.info(f"Thanksgiving detected: {today.year}-11-{thanksgiving_day}")
            # Christmas (Dec 25)
            elif month == 12 and day == 25:
                holiday_name = 'christmas'
                logging.info("Christmas detected")
    
    # Return theme data based on holiday
    if not holiday_name:
        return None
    
    holiday_themes = {
        'new_year': {
            'name': 'New Year',
            'particle_type': 'confetti',
            'background_gradient': 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
            'colors': {
                'primary': '#FFD700',
                'secondary': '#C0C0C0',
                'accent': '#FFA500'
            }
        },
        'valentines': {
            'name': "Valentine's Day",
            'particle_type': 'hearts',
            'background_gradient': 'linear-gradient(135deg, #ff6b9d 0%, #c44569 50%, #f8b500 100%)',
            'colors': {
                'primary': '#FF1493',
                'secondary': '#FF69B4',
                'accent': '#FFB6C1'
            }
        },
        'st_patricks': {
            'name': "St. Patrick's Day",
            'particle_type': 'shamrocks',
            'background_gradient': 'linear-gradient(135deg, #2d5016 0%, #3d7c2f 50%, #5cb85c 100%)',
            'colors': {
                'primary': '#228B22',
                'secondary': '#32CD32',
                'accent': '#90EE90'
            }
        },
        'easter': {
            'name': 'Easter',
            'particle_type': 'eggs',
            'background_gradient': 'linear-gradient(135deg, #ffb3d9 0%, #ffccff 50%, #e6ccff 100%)',
            'colors': {
                'primary': '#FFB6C1',
                'secondary': '#FFC0CB',
                'accent': '#FFE4E1'
            }
        },
        'july_4th': {
            'name': '4th of July',
            'particle_type': 'stars',
            'background_gradient': 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
            'colors': {
                'primary': '#FF0000',
                'secondary': '#FFFFFF',
                'accent': '#0000FF'
            }
        },
        'halloween': {
            'name': 'Halloween',
            'particle_type': 'bats',
            'background_gradient': 'linear-gradient(135deg, #1a1a1a 0%, #2d1b1b 50%, #4a2c2c 100%)',
            'colors': {
                'primary': '#FF8C00',
                'secondary': '#000000',
                'accent': '#8B4513'
            }
        },
        'thanksgiving': {
            'name': 'Thanksgiving',
            'particle_type': 'leaves',
            'background_gradient': 'linear-gradient(135deg, #8b4513 0%, #cd853f 50%, #daa520 100%)',
            'colors': {
                'primary': '#FF8C00',
                'secondary': '#CD853F',
                'accent': '#DAA520'
            }
        },
        'christmas': {
            'name': 'Christmas',
            'particle_type': 'snow',
            'background_gradient': 'linear-gradient(135deg, #1a1a2e 0%, #2d1b1b 50%, #1a2e1a 100%)',
            'colors': {
                'primary': '#FF0000',
                'secondary': '#228B22',
                'accent': '#FFD700'
            }
        }
    }
    
    return holiday_themes.get(holiday_name)

@app.route('/api/holiday-theme')
def api_holiday_theme():
    """Get current holiday theme data"""
    # Check for test holiday in query parameter
    test_holiday = request.args.get('test-holiday')
    
    theme = get_current_holiday(test_holiday=test_holiday)
    
    if theme:
        logging.info(f"Holiday theme detected: {theme['name']} (test_mode: {test_holiday is not None})")
        return jsonify({
            'active': True,
            'holiday': theme['name'],
            'particle_type': theme['particle_type'],
            'background_gradient': theme['background_gradient'],
            'colors': theme['colors']
        })
    else:
        logging.debug("No holiday theme active today")
        return jsonify({
            'active': False,
            'holiday': None,
            'particle_type': None,
            'background_gradient': None,
            'colors': None
        })

@app.route('/api/settings/holiday-test', methods=['POST'])
@require_admin
def api_set_holiday_test():
    """Set test holiday for testing themes"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        test_holiday = data.get('test_holiday', '').strip()
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Ensure settings table exists
        c.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        if test_holiday:
            c.execute("INSERT OR REPLACE INTO settings (key, value, updated) VALUES ('test_holiday', ?, CURRENT_TIMESTAMP)", (test_holiday,))
        else:
            # Clear test holiday
            c.execute("DELETE FROM settings WHERE key = 'test_holiday'")
        
        conn.commit()
        conn.close()
        
        logging.info(f"Test holiday set to: {test_holiday if test_holiday else 'None (auto-detect)'}")
        return jsonify({'status': 'success', 'test_holiday': test_holiday if test_holiday else None})
    except Exception as e:
        logging.error(f"Error setting test holiday: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/holiday-test', methods=['GET'])
@require_admin
def api_get_holiday_test():
    """Get current test holiday setting"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key = 'test_holiday'")
        result = c.fetchone()
        conn.close()
        
        test_holiday = result[0] if result else None
        return jsonify({'test_holiday': test_holiday})
    except Exception as e:
        logging.error(f"Error getting test holiday: {e}")
        return jsonify({'test_holiday': None})

@app.route('/')
def index():
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()

        c.execute("SELECT name, status, last_seen FROM devices")
        devices = c.fetchall()

        unique_devices = {}
        for device in devices:
            unique_devices[device[0]] = device

        devices = list(unique_devices.values())

    ny_tz = get_timezone()
    formatted_devices = []
    for device in devices:
        last_seen_str = device[2]
        if last_seen_str is None:
            formatted_last_seen = "Never"
        else:
            last_seen_dt = datetime.strptime(last_seen_str, '%Y-%m-%d %H:%M:%S')
            last_seen_dt = last_seen_dt.replace(tzinfo=pytz.utc).astimezone(ny_tz)
            formatted_last_seen = last_seen_dt.strftime('%Y-%m-%d %I:%M:%S %p')
        formatted_devices.append((device[0], device[1], formatted_last_seen))

    return render_template('index.html', devices=formatted_devices, timezone=TIMEZONE)

@app.route('/admin')
@require_admin
def admin():
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM devices")
        devices = c.fetchall()
    return render_template('admin.html', devices=devices)

@app.route('/admin/add_device', methods=['GET', 'POST'])
@require_admin
def add_device():
    if request.method == 'POST':
        name = request.form.get('name')
        ip_address = request.form.get('ip_address')
        mac_address = request.form.get('mac_address')
        if not name or not ip_address or not mac_address:
            return render_template('add_device.html', error="All fields are required.")
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('''
            INSERT INTO devices (name, ip_address, mac_address, status, last_seen, notify)
            VALUES (?, ?, ?, 'offline', NULL, 'none')
            ''', (name, ip_address, mac_address))
            conn.commit()
        return redirect(url_for('admin'))
    return render_template('add_device.html')

def periodic_speed_test():
    """Run speed test every hour"""
    while True:
        time.sleep(60 * 60)  # 1 hour
        logging.info("Running periodic speed test...")
        run_speed_test()

def periodic_package_updates():
    """Update package statuses every 30 minutes"""
    while True:
        time.sleep(30 * 60)  # 30 minutes
        logging.info("Updating package statuses...")
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT id, tracking_number, carrier FROM packages WHERE delivered_date IS NULL")
            packages = c.fetchall()
            conn.close()
            
            for package_id, tracking_number, carrier in packages:
                try:
                    status_data = get_package_status(tracking_number, carrier)
                    
                    delivered_date = None
                    if status_data['status'].lower() == 'delivered':
                        delivered_date = datetime.now(get_timezone())
                    
                    conn = sqlite3.connect(db_path)
                    c = conn.cursor()
                    c.execute("""
                        UPDATE packages 
                        SET status = ?, last_location = ?, estimated_delivery = ?, 
                            delivered_date = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (
                        status_data['status'],
                        status_data['last_location'],
                        status_data['estimated_delivery'],
                        delivered_date,
                        package_id
                    ))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    logging.error(f"Error updating package {package_id}: {e}")
        except Exception as e:
            logging.error(f"Error in periodic package updates: {e}")

def periodic_package_archiving():
    """Archive delivered packages 24 hours after delivery"""
    while True:
        time.sleep(60 * 60)  # Check every hour
        logging.info("Checking for packages to archive...")
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            # Find packages delivered more than 24 hours ago
            c.execute("""
                SELECT id, tracking_number, carrier, description, status, last_location, 
                       estimated_delivery, delivered_date, created_at
                FROM packages
                WHERE delivered_date IS NOT NULL 
                AND datetime(delivered_date) <= datetime('now', '-1 day')
            """)
            packages_to_archive = c.fetchall()
            
            for pkg in packages_to_archive:
                # Move to archive
                c.execute("""
                    INSERT INTO packages_archive 
                    (tracking_number, carrier, description, status, last_location, 
                     estimated_delivery, delivered_date, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, pkg[1:])  # Skip id (first element)
                
                # Delete from active packages
                c.execute("DELETE FROM packages WHERE id = ?", (pkg[0],))
                
                logging.info(f"Archived package: {pkg[1]}")
            
            # Keep only last 50 archived packages
            c.execute("""
                DELETE FROM packages_archive 
                WHERE id NOT IN (
                    SELECT id FROM packages_archive 
                    ORDER BY archived_at DESC 
                    LIMIT 50
                )
            """)
            
            conn.commit()
            conn.close()
            
            if packages_to_archive:
                logging.info(f"Archived {len(packages_to_archive)} packages")
        except Exception as e:
            logging.error(f"Error in periodic package archiving: {e}")

if __name__ == '__main__':
    create_db()
    add_alert_shown_column()
    ensure_joke_history_table()
    ensure_quote_history_table()
    cleanup_crash_events()  # Remove any old crash entries

    scan_thread = threading.Thread(target=periodic_scan)
    scan_thread.daemon = True
    scan_thread.start()
    
    speed_test_thread = threading.Thread(target=periodic_speed_test)
    speed_test_thread.daemon = True
    speed_test_thread.start()
    
    package_update_thread = threading.Thread(target=periodic_package_updates)
    package_update_thread.daemon = True
    package_update_thread.start()
    
    package_archive_thread = threading.Thread(target=periodic_package_archiving)
    package_archive_thread.daemon = True
    package_archive_thread.start()

    app.run(host='0.0.0.0', port=5000, debug=True)