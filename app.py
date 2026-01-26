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

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
GOTIFY_URL = "https://services.charleshartmann.com/gotify/message"
GOTIFY_TOKEN = "A.kpf59MW.kkH0O"

# Weather API (OpenWeatherMap - free tier)
WEATHER_API_KEY = "99a6ec730a9f48b06d04f49872935bca"  # You'll need to get a free API key from openweathermap.org
WEATHER_CITY = "Rotterdam,NY,US"  # Your location
WEATHER_LAT = "42.7809"  # Latitude for Rotterdam, NY
WEATHER_LON = "-74.5388"  # Longitude for Rotterdam, NY
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
WEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# News API (NewsAPI - free tier)
NEWS_API_KEY = "d300916c9e42461cbcf52d7ff1e3e76a"  # You'll need to get a free API key from newsapi.org
NEWS_API_URL = "https://newsapi.org/v2/everything"  # Changed to everything endpoint for local news
NEWS_QUERY = "Rotterdam OR Schenectady OR Albany"  # Local area search terms
NY_NEWS_QUERY = "New York"  
HEADLINES_API_URL = "https://newsapi.org/v2/top-headlines"

# Ollama AI Configuration
OLLAMA_URL = "http://74.76.44.128:11434"
OLLAMA_FALLBACK_URL = "http://10.0.0.74:11434"
OLLAMA_MODEL = "llama3.2"

# Admin password (in production, use proper authentication)
ADMIN_PASSWORD = "Cm0NeY12051!"  # WARNING: Do NOT use hardcoded passwords in production. Use environment variables or a secure vault.

# Cache settings
CACHE_DURATION_HOURS = 1  # How long to cache API data

# Timezone
TIMEZONE = 'America/New_York'

# ROMM Configuration (for currently playing game)
ROMM_URL = os.getenv('ROMM_URL', '')
ROMM_USERNAME = os.getenv('ROMM_USERNAME', '')
ROMM_PASSWORD = os.getenv('ROMM_PASSWORD', '')

# RetroAchievements Configuration
RETROACHIEVEMENTS_API_KEY = os.getenv('RETROACHIEVEMENTS_API_KEY', '')
RETROACHIEVEMENTS_USERNAME = os.getenv('RETROACHIEVEMENTS_USERNAME', '')

# Home Assistant Configuration
HA_URL = os.getenv('HA_URL', '').rstrip('/')
HA_TOKEN = os.getenv('HA_TOKEN', '')

if not HA_URL or not HA_TOKEN:
    logging.warning("Home Assistant URL or token not found in environment variables. HA features will be disabled.")

# SwitchBot Configuration
SWITCHBOT_TOKEN = os.getenv('SWITCHBOT_TOKEN', '')
SWITCHBOT_SECRET = os.getenv('SWITCHBOT_SECRET', '')
SWITCHBOT_LOCK_IDS = [lock_id.strip() for lock_id in os.getenv('SWITCHBOT_LOCK_IDS', '').split(',') if lock_id.strip()]

if not SWITCHBOT_TOKEN or not SWITCHBOT_SECRET:
    logging.warning("SwitchBot credentials not found in environment variables. SwitchBot features will be disabled.")

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
            # Create packages table for package tracking
            c.execute('''
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY,
                tracking_number TEXT NOT NULL,
                carrier TEXT,
                description TEXT,
                status TEXT DEFAULT 'In Transit',
                expected_delivery TEXT,
                delivered INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            # Create shopping_list table
            c.execute('''
            CREATE TABLE IF NOT EXISTS shopping_list (
                id INTEGER PRIMARY KEY,
                item_name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                category TEXT,
                checked INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

def get_cached_data(cache_key, max_age_hours=None):
    """Get cached data if it's still valid. max_age_hours overrides default cache duration."""
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

            # Use custom max_age or default
            cache_hours = max_age_hours if max_age_hours is not None else CACHE_DURATION_HOURS

            # Check if cache is still valid
            if datetime.now() - timestamp < timedelta(hours=cache_hours):
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

    device_domains = ['light', 'switch', 'binary_sensor', 'fan', 'climate', 'media_player', 'cover', 'lock']

    devices = []
    for entity in entities:
        entity_id = entity.get('entity_id', '')
        domain = entity_id.split('.')[0] if '.' in entity_id else ''
        state = entity.get('state', '').lower()

        if domain not in device_domains:
            continue

        if for_dashboard:
            if state == 'on':
                devices.append(entity)
        else:
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

        is_battery = 'battery' in entity_id or 'battery_level' in entity_id

        if not is_battery:
            continue

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
            if for_dashboard:
                if battery_level < 25:
                    battery_sensors.append({**entity, 'battery_level': battery_level})
            else:
                battery_sensors.append({**entity, 'battery_level': battery_level})

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

def get_switchbot_device_names():
    """Fetch device names from SwitchBot API"""
    try:
        headers = generate_switchbot_signature()
        response = requests.get('https://api.switch-bot.com/v1.1/devices', headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        devices = data.get('body', {}).get('deviceList', [])
        return {d['deviceId']: d['deviceName'] for d in devices}
    except Exception as e:
        logging.error(f"Error fetching SwitchBot device names: {e}")
        return {}

def get_switchbot_lock_status(use_cache=True):
    """Fetch lock statuses from SwitchBot API with caching and rate limit handling"""
    if not SWITCHBOT_TOKEN or not SWITCHBOT_SECRET or not SWITCHBOT_LOCK_IDS:
        logging.warning("SwitchBot not configured")
        return []

    cache_key = "switchbot_locks"
    rate_limit_key = "switchbot_rate_limit"
    last_good_key = "switchbot_locks_last_good"

    # Check if we're in a rate limit backoff period (15 minutes)
    rate_limit_data = get_cached_data(rate_limit_key, max_age_hours=0.25)  # 15 minutes
    if rate_limit_data:
        logging.debug("SwitchBot API rate limited, using last known good data")
        # Return last known good data if available
        last_good = get_cached_data(last_good_key, max_age_hours=24)  # Keep for 24 hours
        if last_good:
            return last_good
        # If no good data, return error status for all locks
        return [{'device_id': lid, 'name': f'Lock {lid[-4:]}', 'status': 'rate_limited'}
                for lid in SWITCHBOT_LOCK_IDS]

    if use_cache:
        # Use longer cache (10 minutes) to avoid rate limiting
        cached_data = get_cached_data(cache_key, max_age_hours=0.167)  # 10 minutes
        if cached_data:
            return cached_data

    locks = []
    has_errors = False
    is_rate_limited = False
    headers = generate_switchbot_signature()
    device_names = get_switchbot_device_names()

    for lock_device_id in SWITCHBOT_LOCK_IDS:
        lock_name = device_names.get(lock_device_id, f'Lock {lock_device_id[-4:]}')
        try:
            url = f'https://api.switch-bot.com/v1.1/devices/{lock_device_id}/status'
            response = requests.get(url, headers=headers, timeout=10)

            # Check for rate limiting specifically
            if response.status_code == 429:
                logging.warning(f"SwitchBot API rate limited (429)")
                is_rate_limited = True
                has_errors = True
                locks.append({
                    'device_id': lock_device_id,
                    'name': lock_name,
                    'status': 'rate_limited'
                })
                continue

            response.raise_for_status()
            lock_data = response.json()
            lock_state = lock_data.get('body', {}).get('lockState')

            if lock_state is not None:
                locks.append({
                    'device_id': lock_device_id,
                    'name': lock_name,
                    'status': lock_state.lower()
                })
                logging.info(f"SwitchBot lock {lock_name} status: {lock_state}")
            else:
                locks.append({
                    'device_id': lock_device_id,
                    'name': lock_name,
                    'status': 'unknown'
                })

        except requests.RequestException as e:
            logging.error(f"Error checking lock {lock_device_id} status: {e}")
            if '429' in str(e):
                is_rate_limited = True
            has_errors = True
            locks.append({
                'device_id': lock_device_id,
                'name': lock_name,
                'status': 'error'
            })
        except Exception as e:
            logging.error(f"Unexpected error checking lock {lock_device_id}: {e}")
            has_errors = True
            locks.append({
                'device_id': lock_device_id,
                'name': lock_name,
                'status': 'error'
            })

    # If rate limited, set backoff period and return last good data
    if is_rate_limited:
        set_cached_data(rate_limit_key, {'rate_limited': True})
        logging.info("SwitchBot rate limit detected, entering 15-minute backoff period")
        # Return last known good data if available
        last_good = get_cached_data(last_good_key, max_age_hours=24)
        if last_good:
            return last_good
        return locks

    # Cache successful results
    if locks and not has_errors:
        set_cached_data(cache_key, locks)
        # Also save as last known good data
        set_cached_data(last_good_key, locks)

    return locks

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
    ny_tz = pytz.timezone('America/New_York')
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
    
    # Pass screen dimensions to template
    return render_template('rpi_dashboard.html', screen_width=width, screen_height=height)

@app.route('/tv-dashboard')
def tv_dashboard():
    """TV-optimized dashboard with grid and carousel modes"""
    return render_template('tv_dashboard.html', timezone=TIMEZONE)

@app.route('/api/dashboard-data')
def dashboard_data():
    """API endpoint for dashboard data with caching"""
    # Check if refresh parameter is set to bypass cache
    force_refresh = request.args.get('refresh', '').lower() == 'true'
    use_cache = not force_refresh

    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()

        c.execute("SELECT name, status FROM devices")
        devices = c.fetchall()

        # Fetch weather, forecast, news, and joke with caching
        weather = get_weather(use_cache=use_cache)
        forecast = get_weather_forecast(use_cache=use_cache)
        news = get_news(use_cache=use_cache)
        joke = get_joke(use_cache=use_cache)

        # Fetch new features
        calendar_events = get_calendar_events(use_cache=use_cache)
        commute = get_commute_info(use_cache=use_cache)
        air_quality = get_air_quality(use_cache=use_cache)
        quote = get_daily_quote(use_cache=use_cache)
        astronomy = get_astronomy_data(use_cache=use_cache)
        internet_speed = get_internet_speed()
        sports_scores = get_sports_scores(use_cache=use_cache)
        photos = get_photos()

        # Gaming integrations
        romm_playing = get_romm_currently_playing(use_cache=use_cache)
        retroachievements = get_retroachievements(use_cache=use_cache)

        # Smart home integrations
        switchbot_locks = get_switchbot_lock_status(use_cache=use_cache)
        ha_entities = get_ha_states(use_cache=use_cache)
        ha_devices = filter_ha_devices(ha_entities, for_dashboard=True)
        ha_battery = filter_ha_battery_sensors(ha_entities, for_dashboard=True)

        # Package tracking and shopping list
        packages = get_packages()
        shopping_list = get_shopping_list()

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
        
        # Select random calendar event for RPi dashboard
        random_calendar_event = None
        if calendar_events and len(calendar_events) > 0:
            random_calendar_event = random.choice(calendar_events[:5])  # Next 5 events
        
        return jsonify({
            'devices': [{'name': d[0], 'status': d[1]} for d in devices],
            'weather': weather,
            'forecast': forecast,
            'news': news,
            'random_news': random_news,
            'joke': joke,
            'calendar_events': calendar_events,
            'random_calendar_event': random_calendar_event,
            'commute': commute,
            'air_quality': air_quality,
            'quote': quote,
            'astronomy': astronomy,
            'internet_speed': internet_speed,
            'sports_scores': sports_scores,
            'photos': photos,
            'random_photo': random_photo,
            'romm_playing': romm_playing,
            'retroachievements': retroachievements,
            'switchbot_locks': switchbot_locks,
            'home_assistant': {
                'devices': ha_devices,
                'battery_sensors': ha_battery,
                'total_on_devices': len(ha_devices),
                'total_low_battery': len(ha_battery)
            },
            'packages': packages,
            'shopping_list': shopping_list,
            'time': datetime.now().strftime('%I:%M %p'),
            'date': datetime.now().strftime('%A, %B %d'),
            'weather_radar_url': f"https://radar.weather.gov/ridge/standard/KENX_loop.gif"  # Albany, NY radar
        })

@app.route('/api/joke-history')
def joke_history():
    """API endpoint to get joke history (last 100 jokes)"""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT joke_text, timestamp 
                FROM joke_history 
                ORDER BY timestamp DESC 
                LIMIT 100
            """)
            jokes = c.fetchall()
            
            # Format the jokes
            formatted_jokes = []
            ny_tz = pytz.timezone('America/New_York')
            for joke_text, timestamp_str in jokes:
                timestamp_dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                timestamp_dt = timestamp_dt.replace(tzinfo=pytz.utc).astimezone(ny_tz)
                formatted_timestamp = timestamp_dt.strftime('%Y-%m-%d %I:%M %p')
                formatted_jokes.append({
                    'text': joke_text,
                    'timestamp': formatted_timestamp
                })
            
            return jsonify({
                'jokes': formatted_jokes,
                'count': len(formatted_jokes)
            })
    except Exception as e:
        logging.error(f"Error fetching joke history: {e}")
        return jsonify({
            'jokes': [],
            'count': 0,
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
    """Get commute information"""
    # Check if force refresh is requested
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    commute = get_commute_info(use_cache=not force_refresh)
    return jsonify(commute)

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

# ==================== ASTRONOMY API ENDPOINTS ====================
@app.route('/api/astronomy')
def api_astronomy():
    """Get astronomy data"""
    astronomy = get_astronomy_data()
    return jsonify(astronomy)

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
    """Get sports scores"""
    scores = get_sports_scores()
    return jsonify(scores)

@app.route('/api/settings/sports', methods=['GET'])
def api_get_sports_teams():
    """Get favorite sports teams"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key = 'sports_teams'")
        result = c.fetchone()
        conn.close()

        if result:
            teams = json.loads(result[0])
            return jsonify({'teams': teams})
        return jsonify({'teams': []})
    except Exception as e:
        logging.error(f"Error getting sports teams: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/sports', methods=['POST'])
def api_set_sports_teams():
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
        
        # Filter out empty strings
        teams = [team.strip() for team in teams if team and team.strip()]
        
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

# ==================== PACKAGE TRACKING ====================
def get_packages():
    """Get active (undelivered) packages for dashboard"""
    ensure_packages_table()
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            SELECT id, tracking_number, carrier, description, status, expected_delivery, created_at
            FROM packages
            WHERE delivered = 0
            ORDER BY expected_delivery ASC, created_at DESC
        """)
        packages = c.fetchall()
        conn.close()

        return [{
            'id': p[0],
            'tracking_number': p[1],
            'carrier': p[2] or 'Unknown',
            'description': p[3] or 'Package',
            'status': p[4] or 'In Transit',
            'expected_delivery': p[5],
            'created_at': p[6]
        } for p in packages]
    except Exception as e:
        logging.error(f"Error getting packages: {e}")
        return []

def ensure_packages_table():
    """Ensure packages table exists"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY,
                tracking_number TEXT NOT NULL,
                carrier TEXT,
                description TEXT,
                status TEXT DEFAULT 'In Transit',
                expected_delivery TEXT,
                delivered INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error ensuring packages table: {e}")

@app.route('/api/packages', methods=['GET'])
def api_get_packages():
    """Get all packages"""
    ensure_packages_table()
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            SELECT id, tracking_number, carrier, description, status, expected_delivery, delivered, created_at
            FROM packages
            WHERE delivered = 0
            ORDER BY created_at DESC
        """)
        packages = c.fetchall()
        conn.close()

        return jsonify([{
            'id': p[0],
            'tracking_number': p[1],
            'carrier': p[2],
            'description': p[3],
            'status': p[4],
            'expected_delivery': p[5],
            'delivered': p[6] == 1,
            'created_at': p[7]
        } for p in packages])
    except Exception as e:
        logging.error(f"Error getting packages: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/packages', methods=['POST'])
def api_add_package():
    """Add a new package"""
    ensure_packages_table()
    try:
        data = request.get_json()
        tracking_number = data.get('tracking_number', '').strip()
        carrier = data.get('carrier', '').strip()
        description = data.get('description', '').strip()
        expected_delivery = data.get('expected_delivery', '').strip()

        if not tracking_number:
            return jsonify({'error': 'Tracking number is required'}), 400

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO packages (tracking_number, carrier, description, expected_delivery)
            VALUES (?, ?, ?, ?)
        """, (tracking_number, carrier, description, expected_delivery))
        conn.commit()
        package_id = c.lastrowid
        conn.close()

        return jsonify({'status': 'success', 'id': package_id})
    except Exception as e:
        logging.error(f"Error adding package: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/packages/<int:package_id>', methods=['PUT'])
def api_update_package(package_id):
    """Update a package"""
    ensure_packages_table()
    try:
        data = request.get_json()
        status = data.get('status')
        delivered = data.get('delivered')

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        if delivered is not None:
            c.execute("UPDATE packages SET delivered = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                     (1 if delivered else 0, package_id))
        if status:
            c.execute("UPDATE packages SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                     (status, package_id))

        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        logging.error(f"Error updating package: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/packages/<int:package_id>', methods=['DELETE'])
def api_delete_package(package_id):
    """Delete a package"""
    ensure_packages_table()
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

# ==================== SHOPPING LIST ====================
def get_shopping_list():
    """Get unchecked shopping list items for dashboard"""
    ensure_shopping_list_table()
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            SELECT id, item_name, quantity, category
            FROM shopping_list
            WHERE checked = 0
            ORDER BY category ASC, created_at DESC
        """)
        items = c.fetchall()
        conn.close()

        return [{
            'id': i[0],
            'item_name': i[1],
            'quantity': i[2],
            'category': i[3] or 'General'
        } for i in items]
    except Exception as e:
        logging.error(f"Error getting shopping list: {e}")
        return []

def ensure_shopping_list_table():
    """Ensure shopping_list table exists"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS shopping_list (
                id INTEGER PRIMARY KEY,
                item_name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                category TEXT,
                checked INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error ensuring shopping_list table: {e}")

@app.route('/api/shopping-list', methods=['GET'])
def api_get_shopping_list():
    """Get shopping list items"""
    ensure_shopping_list_table()
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            SELECT id, item_name, quantity, category, checked, created_at
            FROM shopping_list
            ORDER BY checked ASC, created_at DESC
        """)
        items = c.fetchall()
        conn.close()

        return jsonify([{
            'id': i[0],
            'item_name': i[1],
            'quantity': i[2],
            'category': i[3],
            'checked': i[4] == 1,
            'created_at': i[5]
        } for i in items])
    except Exception as e:
        logging.error(f"Error getting shopping list: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/shopping-list', methods=['POST'])
def api_add_shopping_item():
    """Add item to shopping list"""
    ensure_shopping_list_table()
    try:
        data = request.get_json()
        item_name = data.get('item_name', '').strip()
        quantity = data.get('quantity', 1)
        category = data.get('category', '').strip()

        if not item_name:
            return jsonify({'error': 'Item name is required'}), 400

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO shopping_list (item_name, quantity, category)
            VALUES (?, ?, ?)
        """, (item_name, quantity, category))
        conn.commit()
        item_id = c.lastrowid
        conn.close()

        return jsonify({'status': 'success', 'id': item_id})
    except Exception as e:
        logging.error(f"Error adding shopping item: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/shopping-list/<int:item_id>', methods=['PUT'])
def api_update_shopping_item(item_id):
    """Update shopping list item (toggle checked, update quantity)"""
    ensure_shopping_list_table()
    try:
        data = request.get_json()
        checked = data.get('checked')
        quantity = data.get('quantity')
        item_name = data.get('item_name')

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        if checked is not None:
            c.execute("UPDATE shopping_list SET checked = ? WHERE id = ?",
                     (1 if checked else 0, item_id))
        if quantity is not None:
            c.execute("UPDATE shopping_list SET quantity = ? WHERE id = ?",
                     (quantity, item_id))
        if item_name is not None:
            c.execute("UPDATE shopping_list SET item_name = ? WHERE id = ?",
                     (item_name, item_id))

        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        logging.error(f"Error updating shopping item: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/shopping-list/<int:item_id>', methods=['DELETE'])
def api_delete_shopping_item(item_id):
    """Delete shopping list item"""
    ensure_shopping_list_table()
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("DELETE FROM shopping_list WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        logging.error(f"Error deleting shopping item: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/shopping-list/clear-checked', methods=['DELETE'])
def api_clear_checked_items():
    """Clear all checked items from shopping list"""
    ensure_shopping_list_table()
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("DELETE FROM shopping_list WHERE checked = 1")
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        logging.error(f"Error clearing checked items: {e}")
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
                'updated': datetime.now().strftime('%I:%M %p')
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
                'updated': datetime.now().strftime('%I:%M %p')
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
    ny_tz = pytz.timezone('America/New_York')
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
    """Fetch commute information using OpenRouteService API"""
    cache_key = "commute_info"
    
    if use_cache:
        cached_data = get_cached_data(cache_key)
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
            return None
        
        origin = origin_result[0]
        destination = dest_result[0]
        
        # Use Nominatim (OpenStreetMap) for geocoding - free, no API key required
        geocode_url = "https://nominatim.openstreetmap.org/search"
        headers = {
            'User-Agent': 'RPI-Dashboard/1.0'  # Required by Nominatim
        }
        
        try:
            # Get coordinates for origin using Nominatim
            geo_params = {
                'q': origin,
                'format': 'json',
                'limit': 1
            }
            response = requests.get(geocode_url, params=geo_params, headers=headers, timeout=10)
            if response.status_code == 200:
                geo_data = response.json()
                if geo_data and len(geo_data) > 0:
                    origin_lat = geo_data[0]['lat']
                    origin_lon = geo_data[0]['lon']
                    origin_str = f"{origin_lon},{origin_lat}"  # lon,lat format for OpenRouteService
                    logging.info(f"Geocoded origin: {origin} -> {origin_lat}, {origin_lon}")
                else:
                    logging.error(f"No geocoding results for origin: {origin}")
                    return None
            else:
                logging.error(f"Geocoding API error for origin: {response.status_code}")
                return None
            
            # Small delay to respect Nominatim rate limits
            time.sleep(1)
            
            # Get coordinates for destination using Nominatim
            geo_params = {
                'q': destination,
                'format': 'json',
                'limit': 1
            }
            response = requests.get(geocode_url, params=geo_params, headers=headers, timeout=10)
            if response.status_code == 200:
                geo_data = response.json()
                if geo_data and len(geo_data) > 0:
                    dest_lat = geo_data[0]['lat']
                    dest_lon = geo_data[0]['lon']
                    dest_str = f"{dest_lon},{dest_lat}"  # lon,lat format for OpenRouteService
                    logging.info(f"Geocoded destination: {destination} -> {dest_lat}, {dest_lon}")
                else:
                    logging.error(f"No geocoding results for destination: {destination}")
                    return None
            else:
                logging.error(f"Geocoding API error for destination: {response.status_code}")
                return None
            
            # Small delay to respect Nominatim rate limits
            time.sleep(1)
            
            # Get directions using OSRM (Open Source Routing Machine) - free, no API key required
            # OSRM uses lon,lat format and expects coordinates separated by semicolons
            url = "http://router.project-osrm.org/route/v1/driving/{coordinates}"
            coordinates_str = f"{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
            full_url = url.format(coordinates=coordinates_str)
            
            params = {
                'overview': 'full',  # Get full route geometry for map display
                'alternatives': 'false',
                'steps': 'false',
                'geometries': 'geojson'  # Get GeoJSON format for easy map rendering
            }
            
            response = requests.get(full_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 'Ok' and data.get('routes'):
                    route = data['routes'][0]
                    distance_m = route.get('distance', 0)  # Distance in meters
                    duration_sec = route.get('duration', 0)  # Duration in seconds
                    distance_km = distance_m / 1000
                    duration_min = int(duration_sec / 60)
                    
                    # Extract route geometry for map display
                    route_geometry = route.get('geometry', {})
                    route_coordinates = []
                    if route_geometry and route_geometry.get('coordinates'):
                        # GeoJSON format: [[lon, lat], [lon, lat], ...]
                        route_coordinates = route_geometry['coordinates']
                    
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
                        'route_coordinates': route_coordinates,  # For map display
                        'updated': datetime.now().strftime('%I:%M %p')
                    }
                    
                    set_cached_data(cache_key, commute_data)
                    logging.info(f"Commute info fetched: {duration_min} min, {round(distance_km * 0.621371, 1)} miles")
                    return commute_data
                else:
                    logging.error(f"OSRM API returned error: {data.get('code', 'Unknown')}")
                    return None
            else:
                logging.error(f"OSRM directions API error: {response.status_code} - {response.text[:200]}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching commute info (network): {e}")
            return None
        except KeyError as e:
            logging.error(f"Error parsing geocoding response: {e}")
            return None
        except Exception as e:
            logging.error(f"Error fetching commute info: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return None
    except Exception as e:
        logging.error(f"Error in get_commute_info: {e}")
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
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
            'updated': datetime.now().strftime('%I:%M %p')
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
def get_daily_quote(use_cache=True):
    """Fetch quote from multiple APIs with fallbacks (refreshes every 4 hours)"""
    cache_key = "daily_quote"

    if use_cache:
        cached_data = get_cached_data(cache_key, max_age_hours=4)
        if cached_data:
            return cached_data

    quote_data = None

    # Try ZenQuotes API first
    try:
        url = "https://zenquotes.io/api/random"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data and len(data) > 0:
            quote_data = {
                'text': data[0].get('q', ''),
                'author': data[0].get('a', 'Unknown'),
                'updated': datetime.now().strftime('%Y-%m-%d')
            }
            logging.info("Got quote from ZenQuotes API")
    except Exception as e:
        logging.warning(f"ZenQuotes API failed: {e}")

    # Try quotable.io as fallback
    if not quote_data:
        try:
            url = "https://api.quotable.io/random"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            quote_data = {
                'text': data.get('content', ''),
                'author': data.get('author', 'Unknown'),
                'updated': datetime.now().strftime('%Y-%m-%d')
            }
            logging.info("Got quote from quotable.io API")
        except Exception as e:
            logging.warning(f"Quotable.io API failed: {e}")

    # Try Ollama as final fallback
    if not quote_data:
        try:
            ollama_servers = [OLLAMA_URL, OLLAMA_FALLBACK_URL]
            for server_url in ollama_servers:
                try:
                    url = f"{server_url}/api/generate"
                    payload = {
                        "model": OLLAMA_MODEL,
                        "prompt": "Give me one inspiring or thought-provoking quote from a famous person. Format: Quote text | Author Name. Just the quote and author, nothing else.",
                        "stream": False
                    }
                    response = requests.post(url, json=payload, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    quote_text = data.get('response', '').strip()
                    if '|' in quote_text:
                        parts = quote_text.split('|')
                        quote_data = {
                            'text': parts[0].strip().strip('"'),
                            'author': parts[1].strip() if len(parts) > 1 else 'Unknown',
                            'updated': datetime.now().strftime('%Y-%m-%d')
                        }
                        logging.info(f"Got quote from Ollama ({server_url})")
                        break
                except Exception as e:
                    logging.warning(f"Ollama {server_url} quote failed: {e}")
                    continue
        except Exception as e:
            logging.warning(f"All Ollama servers failed for quote: {e}")

    if quote_data:
        # Save to history
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("INSERT INTO quote_history (quote_text, author) VALUES (?, ?)",
                     (quote_data['text'], quote_data['author']))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Error saving quote to history: {e}")

        set_cached_data(cache_key, quote_data)
        return quote_data

    # If all APIs fail, return cached or error
    cached_data = get_cached_data(cache_key)
    if cached_data:
        logging.info("Using cached quote due to all API failures")
        return cached_data

    return {
        'text': 'The only way to do great work is to love what you do.',
        'author': 'Steve Jobs',
        'updated': datetime.now().strftime('%Y-%m-%d')
    }

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
        s = sun(city.observer, date=datetime.now().date())
        
        moon_phase_value = phase(datetime.now().date())
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
        
        ny_tz = pytz.timezone('America/New_York')
        sunrise = s['sunrise'].astimezone(ny_tz)
        sunset = s['sunset'].astimezone(ny_tz)
        
        astronomy_data = {
            'moon_phase': round(moon_phase_value, 2),
            'moon_phase_name': phase_info['name'],
            'moon_icon': phase_info['icon'],
            'moon_percentage': round(percentage),
            'sunrise': sunrise.strftime('%I:%M %p'),
            'sunset': sunset.strftime('%I:%M %p'),
            'updated': datetime.now().strftime('%I:%M %p')
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
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
            # Convert UTC timestamp to local timezone
            try:
                import pytz
                utc_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                utc_time = pytz.utc.localize(utc_time)
                local_tz = pytz.timezone(TIMEZONE)
                local_time = utc_time.astimezone(local_tz)
                last_test_str = local_time.strftime('%I:%M %p')
                timestamp_str = local_time.strftime('%Y-%m-%d %H:%M:%S')
            except:
                last_test_str = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%I:%M %p')
                timestamp_str = timestamp
            return {
                'download_mbps': round(download, 2),
                'upload_mbps': round(upload, 2),
                'ping_ms': round(ping, 2),
                'timestamp': timestamp_str,
                'last_test': last_test_str
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
    
    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
    
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
        # Reduced timeout to 3 seconds and limit to 3 teams for faster response
        for team_entry in teams[:3]:  # Limit to 3 teams for faster loading
            # Handle both dict format {"name": "Team Name"} and plain string format
            if isinstance(team_entry, dict):
                team_name = team_entry.get('name', '')
            else:
                team_name = str(team_entry)

            if not team_name:
                continue

            try:
                # Search for team with shorter timeout
                search_url = f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={team_name}"
                response = requests.get(search_url, timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('teams') and len(data['teams']) > 0:
                        team = data['teams'][0]
                        team_id = team.get('idTeam')
                        
                        # Get next event with shorter timeout
                        # Verify it's actually for this team (API sometimes returns wrong data)
                        try:
                            events_url = f"https://www.thesportsdb.com/api/v1/json/3/eventsnext.php?id={team_id}"
                            response = requests.get(events_url, timeout=3)
                            if response.status_code == 200:
                                events_data = response.json()
                                if events_data.get('events'):
                                    for event in events_data['events'][:5]:
                                        event_str = event.get('strEvent', '')
                                        # Only include if team name appears in the event
                                        if team_name.split()[-1].lower() in event_str.lower():
                                            all_scores.append({
                                                'team': team_name,
                                                'event': event_str,
                                                'date': event.get('dateEvent', ''),
                                                'time': event.get('strTime', ''),
                                                'league': event.get('strLeague', ''),
                                                'status': 'Upcoming'
                                            })
                                            break
                        except requests.exceptions.Timeout:
                            logging.warning(f"Timeout fetching next event for {team_name}")
                        except Exception as e:
                            logging.warning(f"Error fetching next event for {team_name}: {e}")
                        
                        # Get last result with shorter timeout
                        try:
                            results_url = f"https://www.thesportsdb.com/api/v1/json/3/eventslast.php?id={team_id}"
                            response = requests.get(results_url, timeout=3)
                            if response.status_code == 200:
                                results_data = response.json()
                                if results_data.get('results'):
                                    result = results_data['results'][0]
                                    all_scores.append({
                                        'team': team_name,
                                        'event': result.get('strEvent', ''),
                                        'score': f"{result.get('intHomeScore', '?')} - {result.get('intAwayScore', '?')}",
                                        'date': result.get('dateEvent', ''),
                                        'league': result.get('strLeague', ''),
                                        'status': 'Completed'
                                    })
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

# ==================== ROMM INTEGRATION ====================
def get_romm_auth_token():
    """Get authentication token from ROMM server"""
    if not ROMM_URL or not ROMM_USERNAME or not ROMM_PASSWORD:
        return None

    try:
        from urllib.parse import quote
        url = f"{ROMM_URL}/api/token"
        # URL-encode the password to handle special characters like !
        encoded_password = quote(ROMM_PASSWORD, safe='')
        data = f"username={ROMM_USERNAME}&password={encoded_password}"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(url, data=data, headers=headers, timeout=10)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get('access_token')
    except Exception as e:
        logging.error(f"Error getting ROMM auth token: {e}")
        return None

def get_romm_currently_playing(use_cache=True):
    """Fetch ROMM library stats"""
    cache_key = "romm_playing"

    if not ROMM_URL:
        return None

    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data

    try:
        token = get_romm_auth_token()
        if not token:
            logging.warning("Could not authenticate with ROMM server")
            return None

        headers = {'Authorization': f'Bearer {token}'}

        # Get library stats from ROMM
        stats_response = requests.get(f"{ROMM_URL}/api/stats", headers=headers, timeout=10)
        heartbeat_response = requests.get(f"{ROMM_URL}/api/heartbeat", headers=headers, timeout=10)

        if stats_response.status_code == 200:
            stats = stats_response.json()
            heartbeat = heartbeat_response.json() if heartbeat_response.status_code == 200 else {}

            # Get available platforms from heartbeat
            platforms = heartbeat.get('FILESYSTEM', {}).get('FS_PLATFORMS', [])
            platform_names = [p.upper() for p in platforms]

            # Calculate file size in GB
            total_bytes = stats.get('TOTAL_FILESIZE_BYTES', 0)
            total_gb = round(total_bytes / (1024 ** 3), 1)

            library_data = {
                'type': 'library',
                'total_roms': stats.get('ROMS', 0),
                'total_platforms': stats.get('PLATFORMS', 0),
                'total_saves': stats.get('SAVES', 0),
                'total_states': stats.get('STATES', 0),
                'total_size_gb': total_gb,
                'platforms': platform_names[:6],  # Show up to 6 platforms
                'version': heartbeat.get('SYSTEM', {}).get('VERSION', 'Unknown'),
                'updated': datetime.now().strftime('%I:%M %p')
            }

            set_cached_data(cache_key, library_data)
            return library_data

        logging.warning("Could not fetch ROMM stats")
        return None

    except Exception as e:
        logging.error(f"Error fetching ROMM data: {e}")
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        return None

# ==================== RETROACHIEVEMENTS INTEGRATION ====================
def get_retroachievements(use_cache=True):
    """Fetch recent achievements from RetroAchievements.org"""
    cache_key = "retroachievements"

    if not RETROACHIEVEMENTS_API_KEY or not RETROACHIEVEMENTS_USERNAME:
        return None

    if use_cache:
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data

    try:
        # Get recent achievements (last 60 minutes by default)
        url = "https://retroachievements.org/API/API_GetUserRecentAchievements.php"
        params = {
            'z': RETROACHIEVEMENTS_USERNAME,
            'y': RETROACHIEVEMENTS_API_KEY,
            'u': RETROACHIEVEMENTS_USERNAME,
            'm': 1440  # Last 24 hours (in minutes)
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        achievements = response.json()

        if not achievements or not isinstance(achievements, list):
            achievements = []

        # Format the achievements
        formatted_achievements = []
        for ach in achievements[:10]:  # Limit to 10 most recent
            formatted_achievements.append({
                'title': ach.get('Title', 'Unknown Achievement'),
                'description': ach.get('Description', ''),
                'game_title': ach.get('GameTitle', 'Unknown Game'),
                'game_icon': f"https://retroachievements.org{ach.get('GameIcon', '')}",
                'console': ach.get('ConsoleName', 'Unknown'),
                'points': ach.get('Points', 0),
                'badge_url': f"https://retroachievements.org/Badge/{ach.get('BadgeName', '')}.png",
                'date': ach.get('Date', ''),
                'hardcore': ach.get('HardcoreMode', 0) == 1
            })

        # Also get user summary for total stats
        summary_url = "https://retroachievements.org/API/API_GetUserSummary.php"
        summary_params = {
            'z': RETROACHIEVEMENTS_USERNAME,
            'y': RETROACHIEVEMENTS_API_KEY,
            'u': RETROACHIEVEMENTS_USERNAME,
            'g': 5  # Include last 5 games
        }

        summary_response = requests.get(summary_url, params=summary_params, timeout=10)
        summary = {}
        if summary_response.status_code == 200:
            summary_data = summary_response.json()
            # Combine hardcore and softcore points for total
            hardcore_points = summary_data.get('TotalPoints', 0) or 0
            softcore_points = summary_data.get('TotalSoftcorePoints', 0) or 0
            total_points = hardcore_points + softcore_points

            # Handle rank - API returns None if not ranked
            rank = summary_data.get('Rank')
            if rank is None or rank == 'None':
                rank = 'Unranked'

            summary = {
                'total_points': total_points,
                'hardcore_points': hardcore_points,
                'softcore_points': softcore_points,
                'total_true_points': summary_data.get('TotalTruePoints', 0) or 0,
                'rank': rank,
                'user_pic': f"https://retroachievements.org{summary_data.get('UserPic', '')}",
                'recent_games': []
            }

            # Get recent games played
            recent_games = summary_data.get('RecentlyPlayed', [])
            for game in recent_games[:3]:
                summary['recent_games'].append({
                    'title': game.get('Title', 'Unknown'),
                    'console': game.get('ConsoleName', 'Unknown'),
                    'icon': f"https://retroachievements.org{game.get('ImageIcon', '')}",
                    'last_played': game.get('LastPlayed', '')
                })

        ra_data = {
            'achievements': formatted_achievements,
            'summary': summary,
            'updated': datetime.now().strftime('%I:%M %p')
        }

        set_cached_data(cache_key, ra_data)
        return ra_data

    except Exception as e:
        logging.error(f"Error fetching RetroAchievements: {e}")
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        return None

def get_joke(use_cache=True, retry_count=3):
    """Fetch a random joke from Ollama AI with caching and retry logic, with fallback server"""
    cache_key = "joke_data"

    # Try to get cached data first (jokes cache for 2 hours max)
    if use_cache:
        cached_data = get_cached_data(cache_key, max_age_hours=2)
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
                    "prompt": "Tell me a unique, funny, family-friendly joke I haven't heard before. Be creative and original. Keep it short and appropriate for all ages. Just tell the joke, no introduction.",
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
                        'updated': datetime.now().strftime('%I:%M %p')
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
        'updated': datetime.now().strftime('%I:%M %p')
    }

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

    ny_tz = pytz.timezone('America/New_York')
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

    return render_template('index.html', devices=formatted_devices)

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
    """Run speed test every hour, starting immediately"""
    # Run immediately on startup
    logging.info("Running initial speed test...")
    run_speed_test()
    # Then run every hour
    while True:
        time.sleep(60 * 60)  # 1 hour
        logging.info("Running periodic speed test...")
        run_speed_test()

if __name__ == '__main__':
    create_db()
    add_alert_shown_column()
    ensure_joke_history_table()

    scan_thread = threading.Thread(target=periodic_scan)
    scan_thread.daemon = True
    scan_thread.start()
    
    speed_test_thread = threading.Thread(target=periodic_speed_test)
    speed_test_thread.daemon = True
    speed_test_thread.start()

    app.run(host='0.0.0.0', port=5000, debug=True)