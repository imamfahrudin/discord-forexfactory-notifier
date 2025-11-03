# Discord Forex Factory Notifier 🚀

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/imamfahrudin/discord-forexfactory-notifier/graphs/commit-activity)
[![GitHub stars](https://img.shields.io/github/stars/imamfahrudin/discord-forexfactory-notifier.svg)](https://github.com/imamfahrudin/discord-forexfactory-notifier/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/imamfahrudin/discord-forexfactory-notifier.svg)](https://github.com/imamfahrudin/discord-forexfactory-notifier/network)
[![GitHub issues](https://img.shields.io/github/issues/imamfahrudin/discord-forexfactory-notifier.svg)](https://github.com/imamfahrudin/discord-forexfactory-notifier/issues)

A sophisticated, automated Discord bot that monitors Forex Factory's economic calendar and delivers real-time notifications about high-impact forex events directly to your Discord server. Stay ahead of market-moving news with customizable filters, timezone support, and beautiful embed formatting.

## 📋 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Method 1: Docker (Recommended)](#method-1-docker-recommended)
  - [Method 2: Manual Setup](#method-2-manual-setup)
- [Configuration](#-configuration)
- [Environment Variables](#-environment-variables)
- [Filtering Options](#-filtering-options)
- [Scheduling](#-scheduling)
- [Docker Deployment](#-docker-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)
- [Support](#-support)

## ✨ Features

- 🎯 **Real-time Forex News**: Fetches economic calendar events from Forex Factory's XML feed
- 🌍 **Timezone Support**: Automatically converts UTC times to your preferred timezone (default: Asia/Jakarta)
- 🎨 **Beautiful Discord Embeds**: Rich, color-coded notifications with clickable event links
- 🔥 **Impact Filtering**: Filter events by impact level (high/medium/low) to focus on what matters
- 💱 **Currency Filtering**: Monitor specific currencies (USD, EUR, GBP, etc.) or track all
- ⏰ **Scheduled Updates**: Automated daily notifications at your preferred time
- 🐳 **Docker Ready**: Easy deployment with Docker and Docker Compose
- 🔄 **Auto-retry Logic**: Robust error handling with exponential backoff
- 📊 **Detailed Logging**: Comprehensive logs for monitoring and debugging
- ⚡ **Lightweight**: Minimal resource usage with Python 3.12 slim image
- 🎭 **Customizable**: Extensive configuration options via environment variables
- 📈 **Event Categorization**: Separates today's news from upcoming events

## 🎬 Demo

### Discord Notification Example

The bot sends elegantly formatted embed messages to your Discord channel:

```
🚨 Forex Alerts - 2025-11-03 (WIB)
Filtered weekly deets—stay sharp! 📈

📊 Today's News (3 total)
• 03 November 2025 | 14:30 WIB | 07:30 UTC 🔴 USD: [Non-Farm Employment Change](https://www.forexfactory.com/...)
• 03 November 2025 | 14:30 WIB | 07:30 UTC 🔴 USD: [Unemployment Rate](https://www.forexfactory.com/...)
• 03 November 2025 | 21:00 WIB | 14:00 UTC 🟡 USD: [ISM Non-Manufacturing PMI](https://www.forexfactory.com/...)

🔮 Upcoming (5 total)
• 04 November 2025 | 15:00 WIB | 08:00 UTC 🔴 EUR: [ECB Interest Rate Decision](https://www.forexfactory.com/...)
• 05 November 2025 | 09:30 WIB | 02:30 UTC 🟡 AUD: [RBA Statement](https://www.forexfactory.com/...)
...
```

### Impact Level Indicators

- 🔴 **High Impact**: Events that typically cause significant market volatility
- 🟡 **Medium Impact**: Moderate market-moving events
- 🟢 **Low Impact**: Minor events with limited market impact

## 📦 Prerequisites

Before you begin, ensure you have one of the following:

### For Docker Deployment (Recommended)
- [Docker](https://www.docker.com/get-started) (version 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 1.29+)

### For Manual Setup
- [Python](https://www.python.org/downloads/) (version 3.12 or higher)
- pip (Python package manager)

### Required for Both
- A Discord webhook URL ([How to create a webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks))

## 🚀 Installation

### Method 1: Docker (Recommended)

Docker provides the easiest and most reliable deployment method.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/imamfahrudin/discord-forexfactory-notifier.git
   cd discord-forexfactory-notifier
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   ```
   Or create a new `.env` file with the following content:
   ```env
   # Required
   DISCORD_WEBHOOK_URL=your_discord_webhook_url_here

   # Optional (defaults shown)
   MAX_UPCOMING=5
   MIN_IMPACT=all
   CURRENCIES=
   TIMEZONE=Asia/Jakarta
   WEBHOOK_USERNAME=Forex Notifier
   EMBED_TITLE=Forex Alerts
   SERVER_NAME=Forex News
   SCHEDULE_HOUR=7
   SCHEDULE_MINUTE=0
   MAX_RETRIES=3
   INITIAL_SLEEP_SECONDS=5
   REQUEST_TIMEOUT=10
   EMBED_COLOR=FF4500
   MAX_EVENT_TITLE_LENGTH=30
   ```

3. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

4. **View logs**:
   ```bash
   docker-compose logs -f
   ```

### Method 2: Manual Setup

If you prefer to run without Docker:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/imamfahrudin/discord-forexfactory-notifier.git
   cd discord-forexfactory-notifier
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Discord webhook URL.

5. **Run the notifier**:
   ```bash
   python main.py
   ```

## ⚙️ Configuration

The bot is highly customizable through environment variables. All configuration is done via the `.env` file.

### Quick Start Configuration

Minimal `.env` file to get started:

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your/webhook/url
```

### Advanced Configuration

For advanced users, here's a fully configured example:

```env
# ============================================
# REQUIRED SETTINGS
# ============================================
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/your-webhook-token

# ============================================
# FILTERING OPTIONS
# ============================================
# Maximum number of upcoming events to display (default: 5)
MAX_UPCOMING=5

# Minimum impact level to show: 'high', 'medium', 'low', or 'all' (default: all)
MIN_IMPACT=high

# Comma-separated currency codes to monitor (empty = all currencies)
# Examples: USD, EUR,USD,GBP, JPY,AUD
CURRENCIES=USD,EUR

# ============================================
# DISPLAY SETTINGS
# ============================================
# Timezone for event times (default: Asia/Jakarta)
# Find your timezone: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIMEZONE=America/New_York

# Bot username shown in Discord (default: Forex Notifier)
WEBHOOK_USERNAME=My Forex Bot

# Title of the embed message (default: Forex Alerts)
EMBED_TITLE=Economic Calendar

# Server name shown in footer (default: Forex News)
SERVER_NAME=My Trading Server

# ============================================
# SCHEDULING
# ============================================
# Hour to run daily notifications (0-23, default: 7)
SCHEDULE_HOUR=7

# Minute to run daily notifications (0-59, default: 0)
SCHEDULE_MINUTE=0

# ============================================
# ADVANCED SETTINGS
# ============================================
# Number of retry attempts for failed requests (default: 3)
MAX_RETRIES=3

# Sleep duration before fetching data in seconds (default: 5)
INITIAL_SLEEP_SECONDS=5

# HTTP request timeout in seconds (default: 10)
REQUEST_TIMEOUT=10

# Discord embed color in hex format without 0x (default: FF4500 - OrangeRed)
EMBED_COLOR=FF4500

# Maximum characters for event titles before truncation (default: 30)
MAX_EVENT_TITLE_LENGTH=30
```

## 🌐 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_WEBHOOK_URL` | ✅ Yes | - | Your Discord webhook URL |
| `MAX_UPCOMING` | ❌ No | `5` | Maximum upcoming events to display |
| `MIN_IMPACT` | ❌ No | `all` | Filter by impact: `high`, `medium`, `low`, or `all` |
| `CURRENCIES` | ❌ No | (all) | Comma-separated currency codes (e.g., `USD,EUR,GBP`) |
| `TIMEZONE` | ❌ No | `Asia/Jakarta` | Timezone for event times (see [tz database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)) |
| `WEBHOOK_USERNAME` | ❌ No | `Forex Notifier` | Bot display name in Discord |
| `EMBED_TITLE` | ❌ No | `Forex Alerts` | Title of embed messages |
| `SERVER_NAME` | ❌ No | `Forex News` | Server name in footer |
| `SCHEDULE_HOUR` | ❌ No | `7` | Hour to run daily (0-23) |
| `SCHEDULE_MINUTE` | ❌ No | `0` | Minute to run daily (0-59) |
| `MAX_RETRIES` | ❌ No | `3` | Request retry attempts |
| `INITIAL_SLEEP_SECONDS` | ❌ No | `5` | Sleep before fetching (seconds) |
| `REQUEST_TIMEOUT` | ❌ No | `10` | HTTP timeout (seconds) |
| `EMBED_COLOR` | ❌ No | `FF4500` | Embed color (hex without 0x) |
| `MAX_EVENT_TITLE_LENGTH` | ❌ No | `30` | Max event title length |

## 🎯 Filtering Options

### Impact Level Filtering

Control which events to display based on their market impact:

```env
# Show only high-impact events
MIN_IMPACT=high

# Show high and medium-impact events
MIN_IMPACT=medium

# Show all events
MIN_IMPACT=all
```

### Currency Filtering

Monitor specific currency pairs:

```env
# Monitor only USD events
CURRENCIES=USD

# Monitor multiple currencies
CURRENCIES=USD,EUR,GBP,JPY

# Monitor all currencies (leave empty)
CURRENCIES=
```

### Common Currency Codes

- **USD**: US Dollar
- **EUR**: Euro
- **GBP**: British Pound
- **JPY**: Japanese Yen
- **AUD**: Australian Dollar
- **CAD**: Canadian Dollar
- **CHF**: Swiss Franc
- **NZD**: New Zealand Dollar
- **CNY**: Chinese Yuan

## ⏰ Scheduling

The bot runs on two occasions:

1. **Startup**: Immediately fetches and sends notifications when the bot starts
2. **Daily Schedule**: Automatically fetches and sends updates at your configured time

### Configure Schedule Time

```env
# Run at 7:00 AM
SCHEDULE_HOUR=7
SCHEDULE_MINUTE=0

# Run at 2:30 PM
SCHEDULE_HOUR=14
SCHEDULE_MINUTE=30

# Run at midnight
SCHEDULE_HOUR=0
SCHEDULE_MINUTE=0
```

The schedule uses your configured `TIMEZONE`, so 7 AM means 7 AM in your timezone.

## 🐳 Docker Deployment

### Docker Compose (Recommended)

The included `docker-compose.yml` makes deployment simple:

```bash
# Start the bot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the bot
docker-compose down

# Restart the bot
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build
```

### Manual Docker Commands

If you prefer not to use Docker Compose:

```bash
# Build the image
docker build -t discord-forexfactory-notifier .

# Run the container
docker run -d \
  --name forex-notifier \
  --env-file .env \
  --restart unless-stopped \
  discord-forexfactory-notifier

# View logs
docker logs -f forex-notifier

# Stop the container
docker stop forex-notifier

# Remove the container
docker rm forex-notifier
```

### Docker Best Practices

- **Persistent Logs**: Mount a volume for logs if needed
  ```yaml
  volumes:
    - ./logs:/app/logs
  ```

- **Resource Limits**: Set resource constraints in `docker-compose.yml`
  ```yaml
  deploy:
    resources:
      limits:
        cpus: '0.5'
        memory: 256M
  ```

- **Health Checks**: Add health monitoring
  ```yaml
  healthcheck:
    test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
    interval: 30s
    timeout: 10s
    retries: 3
  ```

## 🔧 Troubleshooting

### Common Issues

#### 1. Bot not sending messages

**Check webhook URL**:
```bash
# Test webhook manually
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content":"Test message"}'
```

**Check logs**:
```bash
# Docker Compose
docker-compose logs -f

# Manual setup
python main.py
```

#### 2. Wrong timezone

Make sure your timezone is valid. Check the [tz database list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

Common timezones:
- `America/New_York` (EST/EDT)
- `Europe/London` (GMT/BST)
- `Asia/Tokyo` (JST)
- `Asia/Jakarta` (WIB)
- `Australia/Sydney` (AEDT/AEST)

#### 3. No events showing

**Check filters**:
```env
# Ensure filters aren't too restrictive
MIN_IMPACT=all
CURRENCIES=
MAX_UPCOMING=10
```

**Check Forex Factory status**: The XML feed might be temporarily unavailable.

#### 4. Container keeps restarting

**Check environment variables**:
```bash
docker-compose logs
```

Ensure `DISCORD_WEBHOOK_URL` is set correctly.

#### 5. Permission denied errors

**Linux/macOS**:
```bash
sudo chown -R $USER:$USER .
chmod +x main.py
```

### Debug Mode

Enable detailed logging by checking the console output:

```bash
# Docker
docker-compose logs -f discord-forexfactory-notifier

# Manual
python main.py
```

Look for:
- ✅ Success indicators
- ❌ Error messages
- 📊 Event counts
- 🚫 Filter statistics

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Bugs

1. Check [existing issues](https://github.com/imamfahrudin/discord-forexfactory-notifier/issues)
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Logs (if applicable)

### Suggesting Enhancements

1. Open an issue with the `enhancement` label
2. Describe your idea clearly
3. Explain why it would be useful

### Pull Requests

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Make your changes
4. Commit with clear messages:
   ```bash
   git commit -m "Add amazing feature"
   ```
5. Push to your fork:
   ```bash
   git push origin feature/amazing-feature
   ```
6. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/discord-forexfactory-notifier.git
cd discord-forexfactory-notifier

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest

# Run the bot
python main.py
```

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and small

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### What This Means

You are free to:
- ✅ Use commercially
- ✅ Modify the code
- ✅ Distribute
- ✅ Use privately

Under the conditions:
- 📝 Include license and copyright notice
- ⚠️ No liability or warranty

## 🙏 Acknowledgments

- [Forex Factory](https://www.forexfactory.com/) for providing the economic calendar XML feed
- [Discord](https://discord.com/) for their excellent webhook API
- [APScheduler](https://apscheduler.readthedocs.io/) for reliable job scheduling
- [Requests](https://requests.readthedocs.io/) for HTTP simplicity
- The open-source community for inspiration and tools

## 💬 Support

Need help? Here are your options:

### GitHub Issues
Open an issue for:
- 🐛 Bug reports
- 💡 Feature requests
- 📖 Documentation improvements

[Create an Issue](https://github.com/imamfahrudin/discord-forexfactory-notifier/issues/new)

### Discord Webhook Help
- [Discord Webhook Documentation](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)
- [Discord Developer Portal](https://discord.com/developers/docs/resources/webhook)

### Forex Factory
- [Forex Factory Calendar](https://www.forexfactory.com/calendar)
- [Forex Factory Forum](https://www.forexfactory.com/forum)

## 📊 Project Status

This project is actively maintained. Check the [commit history](https://github.com/imamfahrudin/discord-forexfactory-notifier/commits/main) for recent updates.

### Roadmap

Planned features:
- [ ] Web dashboard for configuration
- [ ] Multiple webhook support
- [ ] Historical event tracking
- [ ] Custom event alerts
- [ ] REST API for manual triggers
- [ ] Unit tests
- [ ] CI/CD pipeline

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=imamfahrudin/discord-forexfactory-notifier&type=Date)](https://star-history.com/#imamfahrudin/discord-forexfactory-notifier&Date)

---

<div align="center">

**Made with ❤️ by [Imam Fahrudin](https://github.com/imamfahrudin)**

If this project helped you, please consider giving it a ⭐!

[Report Bug](https://github.com/imamfahrudin/discord-forexfactory-notifier/issues) · [Request Feature](https://github.com/imamfahrudin/discord-forexfactory-notifier/issues) · [Contribute](https://github.com/imamfahrudin/discord-forexfactory-notifier/pulls)

</div>
