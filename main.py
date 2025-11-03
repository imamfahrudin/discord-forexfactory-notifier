# Standard library imports
import os
import requests
import xml.etree.ElementTree as ET
import time
import json
from datetime import datetime, timedelta
from datetime import timezone
import calendar
import logging
import traceback

# Third-party imports for scheduling and timezone handling
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# Configure logging with timestamp, level, and message formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load Discord webhook URL from environment variables (required)
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK_URL')
if not DISCORD_WEBHOOK:
    raise ValueError("Set DISCORD_WEBHOOK_URL in .env—let's get connected! 🕊️")

# Filter settings: control which events to show
MAX_UPCOMING = int(os.getenv('MAX_UPCOMING', '5'))  # Max number of upcoming events to display
MIN_IMPACT = os.getenv('MIN_IMPACT', 'all').lower()  # Filter by impact: 'high', 'medium', 'low', or 'all'
CURRENCIES_STR = os.getenv('CURRENCIES', '')  # Comma-separated list of currencies to filter (e.g., 'USD,EUR,GBP')
CURRENCIES = [c.strip().upper() for c in CURRENCIES_STR.split(',') if c.strip()]  # Parse into list

# Parameterized settings for customization
TIMEZONE = os.getenv('TIMEZONE', 'Asia/Jakarta')  # Timezone for displaying times and grouping events
WEBHOOK_USERNAME = os.getenv('WEBHOOK_USERNAME', 'Forex Notifier')  # Bot username in Discord
EMBED_TITLE = os.getenv('EMBED_TITLE', 'Forex Alerts')  # Title for Discord embed
SERVER_NAME = os.getenv('SERVER_NAME', 'Forex News')  # Server name shown in footer

# Advanced settings with sensible defaults
SCHEDULE_HOUR = int(os.getenv('SCHEDULE_HOUR', '7'))  # Hour to run daily (0-23)
SCHEDULE_MINUTE = int(os.getenv('SCHEDULE_MINUTE', '0'))  # Minute to run daily (0-59)
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))  # Number of retry attempts for failed requests
INITIAL_SLEEP_SECONDS = int(os.getenv('INITIAL_SLEEP_SECONDS', '5'))  # Sleep before fetching (seconds)
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))  # HTTP request timeout (seconds)
EMBED_COLOR = int(os.getenv('EMBED_COLOR', 'FF4500'), 16)  # Discord embed color (hex without 0x)
MAX_EVENT_TITLE_LENGTH = int(os.getenv('MAX_EVENT_TITLE_LENGTH', '30'))  # Max chars for event titles
USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')  # User agent for HTTP requests

# Log all configuration settings for debugging
logger.info(f"Env debug: MAX_UPCOMING raw='{os.getenv('MAX_UPCOMING')}', parsed={MAX_UPCOMING}")
logger.info(f"Env debug: MIN_IMPACT raw='{os.getenv('MIN_IMPACT')}', parsed={MIN_IMPACT}")
logger.info(f"Env debug: CURRENCIES raw='{CURRENCIES_STR}', parsed={CURRENCIES or 'all'}")
logger.info(f"Env debug: TIMEZONE='{TIMEZONE}', WEBHOOK_USERNAME='{WEBHOOK_USERNAME}'")
logger.info(f"Env debug: EMBED_TITLE='{EMBED_TITLE}', SERVER_NAME='{SERVER_NAME}'")
logger.info(f"Env debug: SCHEDULE={SCHEDULE_HOUR}:{SCHEDULE_MINUTE:02d}, MAX_RETRIES={MAX_RETRIES}, REQUEST_TIMEOUT={REQUEST_TIMEOUT}s")
logger.info(f"Env debug: INITIAL_SLEEP={INITIAL_SLEEP_SECONDS}s, EMBED_COLOR=0x{EMBED_COLOR:06X}, MAX_TITLE_LEN={MAX_EVENT_TITLE_LENGTH}")

# Forex Factory XML feed URL containing this week's economic calendar events
XML_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"

# Initialize timezone object for converting UTC times to user's preferred timezone
tz_wib = pytz.timezone(TIMEZONE)

def fetch_all_news():
    """
    Fetch and parse forex news events from the XML feed.
    
    Returns:
        Dictionary containing 'today' events, 'upcoming' events, and 'today_str' date string
    """
    # Brief delay to be polite to the server
    logger.info(f"⏳ Napping {INITIAL_SLEEP_SECONDS}s before fetch—polite mode on! 🌱")
    time.sleep(INITIAL_SLEEP_SECONDS)
    
    # Set user agent to mimic a real browser request
    headers = {
        'User-Agent': USER_AGENT
    }
    
    # Retry loop with exponential backoff
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"🚀 XML fetch (attempt {attempt + 1}/{MAX_RETRIES})...")
            response = requests.get(XML_URL, headers=headers, timeout=REQUEST_TIMEOUT)
            logger.info(f"Status: {response.status_code}")
            
            # Handle non-200 status codes
            if response.status_code != 200:
                if response.status_code == 429:  # Rate limited
                    wait_time = 10 * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"429—napping {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                logger.error(f"Fetch fail: {response.status_code} - {response.text[:200]}...")
                return {'today': [], 'upcoming': [], 'today_str': ''}
            
            # Parse XML response
            root = ET.fromstring(response.content)
            all_events = root.findall('event')
            logger.info(f"Parsed {len(all_events)} events.")
            
            # Log a sample event for debugging
            if all_events:
                sample = ET.tostring(all_events[0], encoding='unicode')
                logger.info(f"🕵️ Sample: {sample[:500]}...")
            
            # Get current time in user's timezone for event grouping
            now_wib = datetime.now(tz_wib)
            today_date_wib = now_wib.date()
            today_str_for_embed = now_wib.strftime('%Y-%m-%d')
            tz_display = now_wib.strftime('%Z')
            logger.info(f"🎯 Grouping by {tz_display} Date: {today_date_wib}")

            # Initialize containers for events and counters for filtering stats
            events = {'today': [], 'upcoming': []}
            total_events = 0
            skipped_past_days = 0  # Events in the past
            skipped_fuzzy = 0  # Events with unclear/TBA times
            skipped_filter = 0  # Events filtered by impact/currency settings
            
            # Process each event from the XML feed
            for i, event_elem in enumerate(all_events):
                try:
                    # Extract date from event
                    date_elem = event_elem.find('date')
                    if date_elem is None or date_elem.text is None or not date_elem.text.strip():
                        continue
                    
                    event_date_str = date_elem.text.strip()
                    
                    # Extract time from event
                    time_elem = event_elem.find('time')
                    time_str = time_elem.text.strip() if time_elem is not None else ''
                    
                    # Skip events with fuzzy/unclear times (TBA, Tentative, All Day)
                    if not time_str or time_str in ['TBA', 'Tentative'] or 'All Day' in time_str:
                        skipped_fuzzy += 1
                        if i < 3: logger.warning(f"⏳ Fuzzy time skip: '{time_str}'")
                        continue

                    # Try multiple time formats to parse the time string
                    event_time = None
                    for fmt in ['%I:%M%p', '%H:%M', '%I:%M %p']:
                        try:
                            event_time = datetime.strptime(time_str, fmt)
                            logger.debug(f"Time parsed with {fmt}: {event_time.time()}")
                            break
                        except ValueError:
                            continue
                    
                    # Skip if time couldn't be parsed
                    if event_time is None:
                        skipped_fuzzy += 1
                        if i < 3: logger.warning(f"⏳ Time parse fail skip: '{time_str}'")
                        continue
                    
                    # Combine date and time, assuming UTC timezone from the feed
                    event_date_full = datetime.strptime(event_date_str, '%m-%d-%Y')
                    event_utc = event_date_full.replace(
                        hour=event_time.hour, minute=event_time.minute, second=0, microsecond=0, tzinfo=timezone.utc
                    )
                    
                    # Convert to user's timezone
                    event_wib = event_utc.astimezone(tz_wib)
                    
                    # Extract date components for display and filtering
                    event_date_obj_wib = event_wib.date()
                    tz_abbrev = event_wib.strftime('%Z')
                    time_wib_str = event_wib.strftime(f"%H:%M {tz_abbrev}")
                    pretty_date_wib = event_wib.strftime("%d %B %Y")

                    # Skip events in the past (based on user's timezone date)
                    if event_date_obj_wib < today_date_wib:
                        skipped_past_days += 1
                        if i < 3: logger.info(f"⏪ Past WIB day skip: {event_date_obj_wib} < {today_date_wib}")
                        continue
                    
                    # Extract event details
                    title_elem = event_elem.find('title')
                    title = title_elem.text.strip() if title_elem is not None else 'Unknown'
                    
                    country_elem = event_elem.find('country')
                    currency = country_elem.text.strip().upper() if country_elem is not None else 'USD'
                    
                    impact_elem = event_elem.find('impact')
                    impact = impact_elem.text.strip().lower() if impact_elem is not None else 'medium'
                    
                    # Apply impact filter if set
                    if MIN_IMPACT != 'all' and impact != MIN_IMPACT:
                        skipped_filter += 1
                        if i < 3: logger.info(f"🚫 Impact skip: {title} ({impact}) < {MIN_IMPACT}")
                        continue
                    
                    # Apply currency filter if set
                    if CURRENCIES and currency not in CURRENCIES:
                        skipped_filter += 1
                        if i < 3: logger.info(f"🚫 Currency skip: {title} ({currency}) not in {CURRENCIES}")
                        continue
                    
                    # Format UTC time for display
                    time_utc_str = event_utc.strftime("%H:%M UTC")
                    
                    # Extract or construct event URL
                    url_elem = event_elem.find('url')
                    link = url_elem.text.strip() if url_elem is not None and url_elem.text else ''
                    if not link:
                        # Construct URL from date if not provided
                        parts = event_date_str.split('-')
                        month_num = int(parts[0])
                        day_str = parts[1]
                        year_str = parts[2]
                        month_abbr = calendar.month_abbr[month_num].lower()
                        link = f"https://www.forexfactory.com/calendar.php?day={month_abbr}{day_str}.{year_str}"
                    
                    # Create event data structure with all relevant information
                    event_data = {
                        'time_utc': time_utc_str,
                        'time_wib': time_wib_str,
                        'currency': currency,
                        'event': title,
                        'impact': impact,
                        'date_str': pretty_date_wib,
                        'sort_time': time_utc_str,
                        'sort_date': event_date_obj_wib,
                        'link': link
                    }
                    
                    # Categorize event as 'today' or 'upcoming' based on user's timezone date
                    if event_date_obj_wib == today_date_wib:
                        events['today'].append(event_data)
                        if len(events['today']) <= 3:
                            logger.info(f"   → Today ({tz_abbrev}) News: {title} ({impact}) {time_wib_str} ({pretty_date_wib})")
                    else:
                        events['upcoming'].append(event_data)
                        if len(events['upcoming']) <= 3:
                            logger.info(f"   → Upcoming ({tz_abbrev}): {title} ({impact}) {time_wib_str} ({pretty_date_wib})")

                    total_events += 1

                except Exception as e:
                    # Handle parsing errors gracefully
                    skipped_fuzzy += 1
                    title_for_error = event_elem.find('title')
                    title_text = title_for_error.text if title_for_error is not None else "Unknown Event"
                    logger.error(f"❌ Parse error on event {i} ({title_text}): {e}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    continue
            
            # Log summary statistics
            logger.info(f"📊 Summary: Processed {total_events} | Past Days Skipped: {skipped_past_days} | Fuzzy: {skipped_fuzzy} | Filtered: {skipped_filter}")
            logger.info(f"Counts | Today News: {len(events['today'])} | Upcoming: {len(events['upcoming'])}")
            
            return {'today': events['today'], 'upcoming': events['upcoming'], 'today_str': today_str_for_embed}
            
        except requests.RequestException as e:
            # Handle network errors with retry logic
            logger.error(f"Network attempt {attempt + 1}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(10 * (2 ** attempt))  # Exponential backoff
                continue
            return {'today': [], 'upcoming': [], 'today_str': ''}
        except ET.ParseError as e:
            # Handle XML parsing errors
            logger.error(f"XML parse: {e}")
            return {'today': [], 'upcoming': [], 'today_str': ''}
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Fetch surprise: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {'today': [], 'upcoming': [], 'today_str': ''}
    
    # All retries exhausted
    logger.error("Retries exhausted—XML snoozing, try later!")
    return {'today': [], 'upcoming': [], 'today_str': ''}

def build_embed(events_data):
    """
    Build a Discord embed message from the events data.
    
    Args:
        events_data: Dictionary containing 'today' events, 'upcoming' events, and 'today_str'
        
    Returns:
        Discord embed object formatted for webhook posting
    """
    # Get today's date string or use current date as fallback
    today_str_ymd = events_data.get('today_str')
    if not today_str_ymd:
        logger.warning("today_str not in events_data! Using system timezone date.")
        today_str_ymd = datetime.now(tz_wib).strftime('%Y-%m-%d')
    
    # Get timezone information for display
    tz_display = datetime.now(tz_wib).strftime('%Z')
    tz_offset = datetime.now(tz_wib).strftime('%z')
    tz_offset_formatted = f"UTC{tz_offset[:3]}:{tz_offset[3:]}"
    
    # Format currency filter for footer
    currencies_display = ', '.join(CURRENCIES) if CURRENCIES else 'All'

    # Create base embed structure
    embed = {
        "title": f"🚨 {EMBED_TITLE} - {today_str_ymd} ({tz_display})",
        "description": "Filtered weekly deets—stay sharp! 📈",
        "color": EMBED_COLOR,
        "fields": [],
        "footer": {"text": f"{SERVER_NAME} | Grouped by {tz_display} Day ({tz_offset_formatted}) | Min Impact: {MIN_IMPACT.upper()} | Lines: {MAX_UPCOMING} | Currencies: {currencies_display}"}
    }
    
    # Sort today's events by time
    today_sorted = sorted(events_data['today'], key=lambda x: x['time_wib'])
    total_today = len(today_sorted)
    
    # Build today's news section
    if not today_sorted:
        embed["fields"].append({"name": "📊 Today's News (0 total)", "value": "No high-impact news found for today. 😌", "inline": False})
    else:
        # Split into multiple fields if there are many events (Discord has field value limits)
        lines_per_field = 5
        num_fields = (total_today + lines_per_field - 1) // lines_per_field
        
        for field_idx in range(num_fields):
            field_start = field_idx * lines_per_field
            field_end = min(field_start + lines_per_field, len(today_sorted))
            field_events = today_sorted[field_start:field_end]
            
            # Build field text with event details
            field_text = ""
            for e in field_events:
                # Choose emoji based on impact level
                impact_emoji = "🔴" if e['impact'] == 'high' else "🟡" if e['impact'] == 'medium' else "🟢"
                short_event = e['event'][:MAX_EVENT_TITLE_LENGTH] + '...' if len(e['event']) > MAX_EVENT_TITLE_LENGTH else e['event']
                field_text += f"• {e['date_str']} | {e['time_wib']} | {e['time_utc']} {impact_emoji} {e['currency']}: [{short_event}]({e['link']})\n"
            
            # Use full name for first field, empty name for continuation fields
            field_name = f"📊 Today's News ({total_today} total)"
            if num_fields > 1 and field_idx > 0:
                field_name = "\u200b"  # Zero-width space for blank field name
            
            embed["fields"].append({"name": field_name, "value": field_text, "inline": False})
    
    # Build upcoming events section
    upcoming_text = "Clear ahead—strategize! 🌤️" if not events_data['upcoming'] else ""
    upcoming_sorted = sorted(events_data['upcoming'], key=lambda x: (x['sort_date'], x['time_wib']))
    total_upcoming = len(upcoming_sorted)
    
    # Show only MAX_UPCOMING events to avoid overwhelming the embed
    for e in upcoming_sorted[:MAX_UPCOMING]:
        impact_emoji = "🔴" if e['impact'] == 'high' else "🟡" if e['impact'] == 'medium' else "🟢"
        short_event = e['event'][:MAX_EVENT_TITLE_LENGTH] + '...' if len(e['event']) > MAX_EVENT_TITLE_LENGTH else e['event']
        upcoming_text += f"• {e['date_str']} | {e['time_wib']} | {e['time_utc']} {impact_emoji} {e['currency']}: [{short_event}]({e['link']})\n"
    
    # Add indicator if there are more events than shown
    if total_upcoming > MAX_UPCOMING:
        remaining = total_upcoming - MAX_UPCOMING
        full_link = "https://www.forexfactory.com/calendar"
        upcoming_text += f"\n**+{remaining} more!** [Full]({full_link})"
    
    embed["fields"].append({"name": f"🔮 Upcoming ({total_upcoming} total)", "value": upcoming_text, "inline": False})
    
    # Log field sizes for debugging (Discord has character limits)
    for field in embed['fields']:
        field_chars = len(field['value'])
        logger.info(f"Field '{field['name']}': {field_chars} chars")
    
    logger.info(f"Embed: {total_today} today news + {total_upcoming} upcoming (top {min(total_upcoming, MAX_UPCOMING)} in 1 field)")
    return embed

def send_to_discord(events_data):
    """
    Send formatted events data to Discord via webhook.
    
    Args:
        events_data: Dictionary containing 'today' events, 'upcoming' events, and 'today_str'
    """
    logger.info("📤 Sending...")
    
    try:
        # Validate events data exists
        if not events_data:
             logger.warning("No events data found. Skipping Discord post.")
             return
        
        # Build the Discord embed
        embed = build_embed(events_data)
        
        # Validate embed was created successfully
        if not embed or not embed['fields']:
             logger.warning("No embed generated (e.g., no news). Skipping Discord post.")
             return

        # Prepare webhook payload
        payload = {"username": WEBHOOK_USERNAME, "embeds": [embed]}
        
        # Send to Discord
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        logger.info(f"Status: {response.status_code}")
        
        # Check response status
        if response.status_code == 204:
            logger.info(f"✅ Sent single embed—high-five! ✋")
        else:
            logger.error(f"Fail {response.status_code}: {response.text}")
            logger.error(f"Payload: {json.dumps(payload, indent=2)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
    except Exception as e:
        logger.error(f"Send oof: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

def run_notifier():
    """
    Main function that runs the notifier service.
    Performs an initial fetch at startup, then schedules daily updates at 7 AM.
    """
    logger.info("🌅 Waking up—alerts incoming! 💼")
    
    # Perform initial fetch and send on startup
    try:
        logger.info("🔄 Startup fetch...")
        events_data = fetch_all_news()
        send_to_discord(events_data)
        logger.info("✅ Startup win!")
    except Exception as e:
        logger.error(f"Startup oof: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Set up scheduled daily notifications
    try:
        scheduler = BlockingScheduler()
        tz_schedule = pytz.timezone(TIMEZONE)
        
        # Schedule job to run daily at configured time in the configured timezone
        scheduler.add_job(
            lambda: (logger.info(f"⏰ {SCHEDULE_HOUR}:{SCHEDULE_MINUTE:02d}! Fetching new data..."), send_to_discord(fetch_all_news())),
            CronTrigger(hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE, timezone=tz_schedule),
            id='daily_ping',
            replace_existing=True
        )
        logger.info(f"Scheduler ready—{SCHEDULE_HOUR}:{SCHEDULE_MINUTE:02d} {TIMEZONE} vibes! 🛡️")
        scheduler.start()  # Blocks here, running indefinitely
    except Exception as e:
        logger.error(f"Scheduler oof: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

# Entry point: run the notifier when script is executed directly
if __name__ == "__main__":
    run_notifier()

