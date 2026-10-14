# 📻 Dunlow • 24/7 Soothing Lofi Radio Discord Bot

[![Discord.py](https://img.shields.io/badge/discord.py-v2.7.1-blue.svg)](https://github.com/Rapptz/discord.py)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-yellow.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Stream Source](https://img.shields.io/badge/source-lofi.radio-teal.svg)](https://lofi.radio/)

A clean, modern Discord bot that streams 24/7 continuous, non-lyrical soothing instrumental melodies directly from **[lofi.radio](https://lofi.radio/)** (featuring 220+ original tracks produced by **Purrple Cat**). 

Built with native Discord voice streaming, Discord's newest **DAVE voice encryption**, and an interactive **Single-Message Session Player** that prevents text channel clutter.

---

## ✨ Key Features

- 📻 **Multi-Station Radio (308+ Tracks)**: Switch seamlessly between **☕ Lofi Beats** (lofi.radio), **🎮 Iconic Gaming Themes** (Minecraft, Zelda, Undertale, Mario, Hollow Knight, Chrono Trigger, Pokemon, Halo), **🎬 Cinema & Anime Themes** (Studio Ghibli, Interstellar, Star Wars), and **🔀 All-in-One Shuffle**!
- ☕ **100% Non-Lyrical & Chill**: Dreamy beats and melodic instruments designed for studying, coding, gaming, relaxing, and sleeping. Zero ads, zero lyrics, zero interruptions.
- 🎛️ **Single Persistent Session Message**: Unlike typical music bots that spam a new message every 2–3 minutes for every song, this bot edits a **single interactive embed** in real-time for the entire session.
- 🔘 **Interactive UI Controller & Station Switcher**: Built-in dropdown to switch stations on the fly, plus control buttons for **Play/Pause**, **Next Melody**, **Shuffle**, **Vol -**, **Vol +**, and **Stop & Leave**.
- 🔒 **DAVE End-to-End Encryption**: Fully compatible with Discord's mandatory voice encryption protocol using `davey` and `PyNaCl`.
- ⚡ **No Lavalink Required**: Direct FFmpeg audio stream decoding without needing heavy Java servers or unstable external nodes.
- 🕒 **24/7 Voice Persistence & Self-Healing Watchdog**: Auto-rejoins if disconnected and features an automatic background watchdog to revive stalled playback.
- 🌐 **Built-in Uptime Web Server**: Runs a lightweight HTTP server (`keep_alive.py`) on port 8080 to support 24/7 pingers (UptimeRobot, Cron-job, etc.).

---

## 🎵 How It Works

```
                 +-------------------+
                 |   lofi.radio      |
                 | (224+ MP3 Tracks) |
                 +---------+---------+
                           |
                           v Direct HTTP Audio Stream
+-------------------------------------------------------+
|  Dunlow Discord Bot                                   |
|                                                       |
|  1. FFmpeg PCMAudio Streamer                          |
|  2. PCMVolumeTransformer (Dynamic 1-100% Volume)      |
|  3. Discord.py VoiceClient + DAVE Encryption (davey)  |
|  4. In-Place Single Session UI Message Manager        |
+--------------------------+----------------------------+
                           |
                           v
              +--------------------------+
              | Discord Voice Channel    |
              | (Encrypted 24/7 Playback)|
              +--------------------------+
```

1. When a user runs `f#radio`, the bot connects to their voice channel.
2. It sends an initial player card with interactive buttons and registers it as the **Session Message**.
3. It draws randomly from a curated queue of 224+ non-lyrical tracks from `https://lofi.radio/songs/`.
4. As each track finishes or when a user clicks **Next Melody**, the bot **edits the same message** with the new track title, artwork, and updated queue status.
5. When stopped (`f#stop` or the red **Stop & Leave** button), the single message cleanly transitions to a **Session Ended** state and removes interactive buttons.

---

## 📜 Commands Reference

All commands use the default prefix `f#`:

| Command | Aliases | Description |
| :--- | :--- | :--- |
| `f#radio [station]` | `join`, `start`, `play`, `p` | Joins your voice channel and starts 24/7 radio (lofi, gaming, cinema, all). |
| `f#station [name]` | `stations`, `mode` | Switches radio station (lofi, gaming, cinema, all) or lists stations. |
| `f#next` | `skip`, `s` | Skips to the next melody in the queue. |
| `f#previous` | `prev` | Replays the previously played melody from history. |
| `f#shuffle` | — | Randomizes all upcoming melodies in the active station queue. |
| `f#pause` | — | Pauses the radio stream. |
| `f#resume` | — | Resumes playing the paused stream. |
| `f#volume <1-100>`| `vol`, `v` | Sets the radio volume percentage (e.g. `f#volume 50`). |
| `f#nowplaying` | `np` | Refreshes and brings the active session player card into view. |
| `f#queue` | `q` | Displays upcoming melodies with paginated navigation. |
| `f#247` | — | Toggles 24/7 persistence mode (auto-reconnect on disconnect). |
| `f#stop` | `leave`, `dc`, `disconnect` | Stops the radio, ends the session, and leaves the voice channel. |
| `f#help` | — | Displays an interactive, paginated command guide. |
| `f#restart` | — | Restarts the bot internally (Administrators/Owner only). |

---

## 🔑 Getting Your Discord Bot Token

To run this bot, you need to create an application and bot token in the Discord Developer Portal:

1. Go to the **[Discord Developer Portal](https://discord.com/developers/applications)** and sign in.
2. Click **New Application** in the top-right corner. Give it a name (e.g., `Dunlow Radio`) and click **Create**.
3. In the left navigation menu, click **Bot**.
4. Click **Reset Token** (or **Add Bot** if prompted) and confirm.
5. **Copy the token immediately** and save it safely.
   > ⚠️ **IMPORTANT**: Never share your token or push it to GitHub! Discord automatically revokes leaked tokens.
6. Scroll down on the **Bot** page to **Privileged Gateway Intents**:
   - Enable **Message Content Intent** (required so the bot can read `f#` prefix commands).
   - Click **Save Changes**.
7. Navigate to **OAuth2** -> **URL Generator** in the left sidebar:
   - Under **Scopes**, select: `bot`.
   - Under **Bot Permissions**, select:
     - `Connect`
     - `Speak`
     - `Send Messages`
     - `Embed Links`
     - `Attach Files`
     - `Read Message History`
     - `Manage Messages` (optional, used to auto-clean trigger commands)
8. Copy the generated URL at the bottom, paste it into your browser, and select your Discord server to invite the bot.

---

## 🚀 Local Installation & Quickstart

### Prerequisites
- **Python 3.10+** (Tested up to Python 3.14)
- **FFmpeg** installed and accessible in your system's `PATH`:
  - *Windows*: `winget install Gyan.FFmpeg`
  - *Ubuntu/Debian*: `sudo apt update && sudo apt install -y ffmpeg`
  - *macOS*: `brew install ffmpeg`

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/OrionInspiron/Dunlow-Discord-Bot.git
   cd Dunlow-Discord-Bot
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your `.env` file:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and paste your bot token:
     ```env
     DISCORD_TOKEN=your_actual_bot_token_here
     ```

5. Start the bot:
   - On Windows, double-click **`start.bat`** (features automatic crash recovery & restarts).
   - Or run via terminal:
     ```bash
     python main.py
     ```

---

## ☁️ Deployment Guide

### A. Deploying via Vercel (Web / Keep-Alive Dashboard)

> ℹ️ **Understanding Discord Bots on Vercel**:  
> Vercel is a **Serverless Platform** designed for ephemeral HTTP request/response lifecycles (with execution limits between 10s to 60s). Standard Discord voice bots maintain a **persistent WebSocket gateway connection** and a **continuous UDP voice stream**, which serverless functions cannot keep open permanently.  
> 
> However, you can deploy the bot's health check/monitoring API and web dashboard to Vercel, or trigger webhook interactions!

#### To deploy the web project to Vercel:
1. Fork or push this repository to your GitHub account.
2. Log into **[Vercel](https://vercel.com/)** and click **Add New...** -> **Project**.
3. Import your `Dunlow-Discord-Bot` repository.
4. In the **Environment Variables** section:
   - Add `DISCORD_TOKEN` with your bot token value.
5. In your project, create a `vercel.json` if configuring serverless routes:
   ```json
   {
     "rewrites": [
       { "source": "/(.*)", "destination": "/keep_alive.py" }
     ]
   }
   ```
6. Click **Deploy**. Vercel will build and assign you a live `.vercel.app` URL.

---

### B. Deploying the 24/7 Voice Bot (Render, Railway, Fly.io, or VPS)

For a continuous, uninterrupted 24/7 radio stream in Discord voice channels, use a persistent container host:

#### Option 1: Render.com (Recommended Free/Low-Cost Cloud Host)
1. Push your code to GitHub.
2. Go to **[Render.com](https://render.com)** and create a **Web Service** (connected to your repository).
3. Set the following settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
4. Under **Advanced** -> **Environment Variables**:
   - `DISCORD_TOKEN`: `<your_bot_token>`
   - `PORT`: `8080`
5. Click **Deploy Web Service**.
6. Render will automatically detect the web server in `keep_alive.py` on port 8080 and keep the bot running 24/7! You can plug the URL into [UptimeRobot](https://uptimerobot.com) to prevent free tiers from idling.

#### Option 2: Railway.app / Fly.io / VPS
1. Run natively on any Linux server (Ubuntu/Debian) using `systemd` or `pm2`:
   ```bash
   npm install -g pm2
   pm2 start main.py --name "lofi-bot" --interpreter python3
   pm2 save
   pm2 startup
   ```

---

## 🛠️ Project Structure

```text
Dunlow-Discord-Bot/
├── .env                  # Private bot secrets (git-ignored)
├── .env.example          # Environment variables template
├── .gitignore            # Git exclusions
├── keep_alive.py         # Lightweight aiohttp web server for 24/7 uptime pinging
├── main.py               # Bot entrypoint, gateway configuration, & dynamic cog loader
├── requirements.txt      # Clean, minimal dependencies manifest
├── start.bat             # Windows auto-restarting script
└── cogs/
    ├── help.py           # Paginated command guide
    ├── music.py          # Complete 24/7 Lofi Radio & single-message player engine
    └── owner.py          # Admin/moderator maintenance & internal restart commands
```

---

## 🤝 Credits & Acknowledgements

- **Music & Stream**: All soothing melodies streamed by this bot are created by the talented artist **[Purrple Cat](https://purrplecat.com/)** and provided via **[lofi.radio](https://lofi.radio/)**.
- **Discord Voice**: Powered by **[discord.py](https://github.com/Rapptz/discord.py)** and **[davey](https://github.com/discord/davey)**.

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
