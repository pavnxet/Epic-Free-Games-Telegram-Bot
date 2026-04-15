# 🎮 Epic Free Games Telegram Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Deploy to Cloudflare Workers](https://deploy.workers.cloudflare.com/button)](https://github.com/pavnxet/Epic-Free-Games-Telegram-Bot/tree/cloudfare-deploy)

A lightweight, asynchronous Telegram bot built with Python that fetches and broadcasts currently free games from the Epic Games Store. It automatically notifies subscribers every Thursday, avoiding duplicate notifications through local JSON state management.

🚀 **Author/Source:** [pavnxet/Epic-Free-Games-Telegram-Bot](https://github.com/pavnxet/Epic-Free-Games-Telegram-Bot)

## ✨ Features

- **Manual Fetching**: Send `/fetch` to get the currently available free games immediately.
- **Auto Broadcast**: Runs silently in the background, automatically messaging subscribers every Thursday at `21:35 IST` with the newest free games.
- **Smart Tracking**: Never spam! The bot tracks which games it has already broadcast to ensure you only get notified once per game.
- **Rich Media**: Notifications include high-quality promotional artwork and inline "Claim Game" buttons that open the Epic Store directly.

## 🛠 Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (Get one by talking to [@BotFather](https://t.me/botfather) on Telegram)

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pavnxet/Epic-Free-Games-Telegram-Bot.git
   cd Epic-Free-Games-Telegram-Bot
   ```

2. **Create and activate a virtual environment (Recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Environment Variables

The bot requires the `TELEGRAM_TOKEN` environment variable to authenticate with the Telegram API.

### Option 1: Export directly in your terminal
```bash
export TELEGRAM_TOKEN="YOUR_BOT_TOKEN_HERE"
```

### Option 2: Using a `.env` file (Optional but recommended)
You can create a `.env` file in the root directory and define the variable there if you are using a loader like `python-dotenv`:
```ini
TELEGRAM_TOKEN=123456789:ABCDefGhiJkLmNopQRstuVwXyz
```

## ▶️ Running the Bot

Once the dependencies are installed and the environment variable is set, simply run:

```bash
python3 bot.py
```

The bot will print `Bot started and scheduler initialized.` to the console indicating it's ready.

## 🗃️ State Management
The bot utilizes local JSON files to keep track of its state across restarts:
- `subscribers.json`: Stores the Chat IDs of users interacting with the bot.
- `sent_games.json`: Stores the unique IDs of games that have already been broadcast.

*Note: These files are automatically generated when the bot starts and are ignored via `.gitignore` to prevent committing live user data.*

## 🧪 Running Tests
The project includes automated tests to verify the core scraping, markdown parsing, and formatting functions. To execute them:
```bash
python3 -m pytest bot_test.py
```

---
*Developed by [pavnxet](https://github.com/pavnxet)*
