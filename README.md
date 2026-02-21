# FileToLink 🔗

<p align="center">
  <b>Transform Any Telegram File into a Shareable Direct Download & Streaming Link</b><br/>
  <a href="https://t.me/file2linkkuttu_bot">🤖 Try the Live Bot</a> •
  <a href="#-getting-started">🚀 Deploy</a> •
  <a href="#-configuration">⚙️ Config</a> •
  <a href="#-usage">📖 Usage</a>
</p>

<p align="center">
  <a href="https://github.com/GouthamSER/FileToLink/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-AGPL--3.0-blue.svg" alt="License"/>
  </a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-yellow?logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/Pyrogram-2.x-blue?logo=telegram" alt="Pyrogram"/>
  <img src="https://img.shields.io/badge/MongoDB-Atlas-green?logo=mongodb" alt="MongoDB"/>
</p>

---

## 📖 About

**FileToLink** is a Python-based Telegram bot that instantly converts any file uploaded to Telegram into a **permanent HTTP/HTTPS direct download and streaming link**. It leverages Telegram's file storage infrastructure, making it effortless to share media, documents, and more — no cloud storage account required.

> 🔴 **Live Demo:** [@file2linkkuttu_bot](https://t.me/file2linkkuttu_bot)

---

## ✨ Features

- **⚡ Instant Link Generation** — Upload any file and receive a direct download link within seconds.
- **🎥 Streaming Support** — Media files (video, audio) can be streamed directly in a browser or media player.
- **🚀 High-Speed Downloads** — Direct links bypass Telegram client limitations for rapid retrieval.
- **💾 Large File Support** — Handles files up to Telegram's maximum limit (up to 4 GB).
- **🗃️ MongoDB Integration** — Persistent storage for user data and file indexing.
- **👑 Admin Controls** — Broadcast messages, view stats, and manage files via admin commands.
- **📦 Plugin System** — Modular plugin architecture makes it easy to extend functionality.
- **🐳 Docker & Cloud Ready** — Deploy on Docker, Render, Koyeb, or any VPS with ease.

---

## 📂 Project Structure

```
FileToLink/
├── bot.py               # Main entry point — initializes and starts the bot
├── info.py              # Configuration — API keys, tokens, and env variables
├── utils.py             # Utility/helper functions shared across the project
├── Script.py            # Additional scripting or startup logic
├── database/            # MongoDB interaction — user management & file indexing
├── plugins/             # Modular command handlers (stats, broadcast, etc.)
├── lib/                 # Core library/helper modules
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker deployment configuration
├── Procfile             # Process file for platforms like Heroku/Railway
├── logging.conf         # Logging configuration
└── .python-version      # Specifies the required Python version
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** 🐍
- **Telegram Account** 👤
- **Telegram API credentials** from [my.telegram.org](https://my.telegram.org)
- **A Bot Token** from [@BotFather](https://t.me/BotFather)
- **MongoDB URI** (e.g., [MongoDB Atlas](https://www.mongodb.com/atlas) — free tier works fine)
- A **private Telegram channel** where the bot is admin (used to store files)

---

### 🖥️ Local / VPS Deployment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/GouthamSER/FileToLink
   cd FileToLink
   ```

2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure environment variables** — fill in your values in `info.py` or set them as environment variables (see [Configuration](#-configuration) below).

4. **Run the bot:**
   ```bash
   python3 bot.py
   ```

---

### 🐳 Docker Deployment

```bash
docker build -t filetolink .
docker run -d \
  -e BOT_TOKEN="your_bot_token" \
  -e API_ID="your_api_id" \
  -e API_HASH="your_api_hash" \
  -e DATABASE_URI="your_mongodb_uri" \
  -e LOG_CHANNEL="-100xxxxxxxxxx" \
  filetolink
```

---

### ☁️ One-Click Cloud Deployment

Deploy instantly to your preferred cloud platform:

| Platform | Button |
|----------|--------|
| **Koyeb** | [![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=https://github.com/GouthamSER/FileToLink&branch=main) |
| **Render** | [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/GouthamSER/FileToLink) |

---

## ⚙️ Configuration

Set the following variables in `info.py` or as environment variables on your hosting platform:

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ | Your bot token from [@BotFather](https://t.me/BotFather) |
| `API_ID` | ✅ | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ | Telegram API Hash from [my.telegram.org](https://my.telegram.org) |
| `LOG_CHANNEL` | ✅ | ID of the private channel where files are stored (bot must be admin) |
| `DATABASE_URI` | ✅ | MongoDB connection string for user data and file indexing |
| `ADMINS` | ⬜ | Space-separated list of Telegram User IDs with admin access |

> ⚠️ **Security Warning:** Never commit `info.py` with real credentials to a public repository. Use environment variables or a `.env` file and add it to `.gitignore`.

---

## 📖 Usage

### User Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and receive a welcome message |
| *(Upload any file)* | Send or forward any file to instantly receive a direct download link |

### Admin Commands

| Command | Description |
|---------|-------------|
| `/stats` | View bot statistics (total users, files indexed, etc.) |
| `/broadcast` | Broadcast a message to all bot users |
| `/delete` | Reply to a file message to remove it from the index |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.
See the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

Made with ❤️ by [GouthamSER](https://github.com/GouthamSER)

> ⭐ If you find this project useful, please consider giving it a star!
