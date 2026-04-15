# 🎮 Epic Free Games Telegram Bot (Cloudflare Workers Edition)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Deploy to Cloudflare Workers](https://img.shields.io/badge/Deploy-Cloudflare-f38020?logo=cloudflare)](https://dash.cloudflare.com/)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://t.me/botfather)

A serverless, zero‑cost Telegram bot that notifies subscribers about free games from the Epic Games Store every Thursday. Built on **Cloudflare Workers** using **JavaScript** and **Workers KV** for state management.

> 🚀 **Original Author:** [pavnxet/Epic-Free-Games-Telegram-Bot](https://github.com/pavnxet/Epic-Free-Games-Telegram-Bot)  
> This version adapts the original Python bot to run entirely on Cloudflare's free tier.

---

## ✨ Features

- **Manual Fetching**: Send `/fetch` to get the currently available free games immediately.
- **Automatic Broadcast**: A Cron Trigger runs every Thursday at 21:35 UTC (21:35 IST) and pushes new free games to all subscribers.
- **Smart Tracking**: Never spam! The bot tracks which games have already been broadcast using Workers KV.
- **Rich Media**: Notifications include high‑quality promotional artwork and inline "Claim Game" buttons that open the Epic Store directly.
- **100% Free**: Runs within Cloudflare's generous free tier limits.

---

## 🏗️ Architecture

| Component           | Technology                       |
|---------------------|----------------------------------|
| Runtime             | Cloudflare Workers (JavaScript)  |
| State Storage       | Cloudflare Workers KV            |
| Scheduling          | Cron Triggers                    |
| External APIs       | Epic Games Store API, Telegram Bot API |

- The Worker responds to **Telegram webhooks** for user commands.
- A **Cron Trigger** invokes the `scheduled()` handler every Thursday.
- Subscriber lists and sent‑game IDs are stored in a **KV namespace**.

---

## 📋 Prerequisites

Before deploying, you'll need:

1. **A Cloudflare Account** – [Sign up for free](https://dash.cloudflare.com/sign-up).
2. **A Telegram Bot Token** – Create a new bot by chatting with [@BotFather](https://t.me/botfather).
3. **(Optional)** A GitHub account for forking this repository.

---

## 🚀 Deployment Guide (Cloudflare Dashboard – No CLI)

This entire deployment can be done through the Cloudflare web interface. No terminal or Wrangler CLI is required.

### Step 1: Create a KV Namespace

1. Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. Navigate to **Workers & Pages** → **KV**.
3. Click **Create namespace**.
4. Name it `EPIC_BOT_STATE` (or any name you prefer).
5. Copy the **ID** that appears—you'll need it in a moment.

### Step 2: Create a Worker

1. Go to **Workers & Pages** → **Overview** → **Create application** → **Create Worker**.
2. Give your worker a name, e.g., `epic-free-games-bot`.
3. Click **Deploy** (you can leave the default code for now).

### Step 3: Replace the Worker Code

1. After deployment, click **Edit code** to open the online editor.
2. Delete the existing content and paste the **entire** [`worker.js`](./worker.js) code from this repository.
3. Click **Save and Deploy**.

### Step 4: Set Environment Variables

1. In the worker's page, go to **Settings** → **Variables**.
2. Under **Environment Variables**, click **Add variable**.
3. Add the following variable:
   - **Variable name:** `TELEGRAM_BOT_TOKEN`
   - **Value:** `123456789:ABCDefGhiJkLmNopQRstuVwXyz` *(your actual bot token)*
4. Click **Save**.

### Step 5: Bind the KV Namespace

1. Still in **Settings** → **Variables**, scroll to **KV Namespace Bindings**.
2. Click **Add binding**.
3. Configure the binding:
   - **Variable name:** `BOT_STATE` *(this must match the code)*
   - **KV namespace:** Select the `EPIC_BOT_STATE` namespace you created earlier.
4. Click **Save**.

### Step 6: Add the Cron Trigger

1. Go to **Settings** → **Triggers**.
2. Click **Add Cron Trigger**.
3. Set the schedule:
   - **Cron expression:** `35 21 * * 4`  
     *(Every Thursday at 21:35 UTC, which corresponds to 21:35 IST)*
4. Click **Add Trigger**.

### Step 7: Activate the Telegram Webhook

1. Find your worker's URL. It looks like:  
   `https://epic-free-games-bot.<your-subdomain>.workers.dev`
2. Open a browser tab and visit:  
   `https://epic-free-games-bot.<your-subdomain>.workers.dev/set-webhook`
3. You should see a JSON response like `{"ok":true,"result":true}`. This tells Telegram to send updates to your Worker.

### 🎉 Done!

Your bot is now live. Open Telegram, search for your bot's username, and send `/start`. You'll receive a welcome message. Send `/fetch` to see the current free games.

---

## 💻 Local Development (Optional)

If you prefer to work locally using Wrangler:

1. **Clone the repository**
   ```bash
   git clone https://github.com/pavnxet/epic-free-games-cloudflare-worker.git
   cd epic-free-games-cloudflare-worker
   ```

2. **Install Wrangler**
   ```bash
   npm install -g wrangler
   ```

3. **Authenticate with Cloudflare**
   ```bash
   wrangler login
   ```

4. **Create a `.dev.vars` file** for local secrets:
   ```ini
   TELEGRAM_BOT_TOKEN=your_actual_token_here
   ```

5. **Update `wrangler.toml`** with your KV namespace ID (create the file if needed):
   ```toml
   name = "epic-free-games-bot"
   main = "worker.js"
   compatibility_date = "2026-04-15"

   kv_namespaces = [
     { binding = "BOT_STATE", id = "your-kv-namespace-id" }
   ]

   [triggers]
   crons = ["35 21 * * 4"]
   ```

6. **Run locally**
   ```bash
   wrangler dev
   ```

7. **Deploy**
   ```bash
   wrangler deploy
   ```

---

## 📁 Project Structure

```
.
├── worker.js           # Main Cloudflare Worker code
├── wrangler.toml       # Wrangler configuration (optional for dashboard users)
├── .gitignore          # Ignores .dev.vars and other local files
├── LICENSE             # MIT License
└── README.md           # This file
```

---

## 🤖 Bot Commands

| Command   | Description                                       |
|-----------|---------------------------------------------------|
| `/start`  | Subscribes you to the weekly broadcast.           |
| `/fetch`  | Immediately sends the currently free games.       |

---

## ⚙️ Environment Variables

| Variable            | Required | Description                                 |
|---------------------|----------|---------------------------------------------|
| `TELEGRAM_BOT_TOKEN`| ✅       | The token obtained from @BotFather.         |

---

## 🗓️ Cron Schedule

The bot broadcasts every **Thursday at 21:35 UTC** (which is 21:35 IST year‑round). The cron expression is:

```
35 21 * * 4
```

You can adjust this in the Cloudflare Dashboard (**Triggers** → **Cron Triggers**) or in `wrangler.toml`.

---

## 🔒 Security Notes

- Never commit your `TELEGRAM_BOT_TOKEN` or `.dev.vars` file to version control.
- The `BOT_STATE` KV binding is internal to Cloudflare; it cannot be accessed from the public internet.
- All communication with Telegram and the Epic Games API occurs over HTTPS.

---

## 📜 Credits & License

- **Original Python Bot:** [pavnxet/Epic-Free-Games-Telegram-Bot](https://github.com/pavnxet/Epic-Free-Games-Telegram-Bot)
- **Cloudflare Worker Adaptation:** [Pavneet Singh (@pavnxet)](https://github.com/pavnxet)

This project is licensed under the **MIT License** – see the [LICENSE](./LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.

---

**Enjoy your free games! 🎉**
