# Obsidian Inbox Bot

A minimal working Python bot for Telegram that saves messages as Markdown files and pushes them to Git.

Built with only one dependency: [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot)

---

## ✨ Features

- Accepts messages via Telegram  
- Saves each message as a Markdown `.md` file  
- Filenames are based on the first 5 words  
- Automatically commits and pushes to a Git repository (via SSH)  
- Dockerized for easy deployment

---

## 🚀 Quick Start

### 1. SSH into your server and prepare the directory

```bash
ssh youruser@yourserver
mkdir obsidian-telegram-bot
cd obsidian-telegram-bot
```

### 2. Clone the repository

```bash
git clone https://github.com/fumblerill/obsidian-telegram-bot.git .
```

### 3. Add your private SSH key

Place your SSH private key (with write access to your notes repository) into the server filesystem. For example:

```bash
mkdir -p /root/.ssh
mv your_private_key /root/.ssh/obsidian_bot_ssh
chmod 600 /root/.ssh/obsidian_bot_ssh
```

> ⚠️ This key must be in place **before building the Docker image**, as the image uses it to clone the Git repository.

### 4. Create `.env` file

```bash
cp .env.example .env
```

Edit `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
ALLOWED_IDS=123456789,987654321
GIT_SSH_KEY_PATH=/root/.ssh/obsidian_bot_ssh
```

### 5. Build and start the bot

```bash
docker-compose up --build -d
```

---

## 🛠 Environment Variables

| Variable            | Description                                      |
|---------------------|--------------------------------------------------|
| `BOT_TOKEN`         | Your Telegram bot token                          |
| `ALLOWED_IDS`       | Comma-separated list of allowed Telegram user IDs |
| `GIT_SSH_KEY_PATH`  | Absolute path to your private SSH key (on host)  |

---

## 📁 File Structure

Markdown files are stored in the `InboxIdeas/` folder (cloned from your Git repository).  
Each message becomes a separate `.md` file named after its first 5 words (or "idea" if empty).

> 🧠 Make sure that your Obsidian vault is also connected to the same Git repository.
> Run `git pull` inside Obsidian to receive incoming idea files.

To remove processed idea files, just delete them on GitHub (via the web UI or manually) — they won't be recreated.

---

## 🔐 Git Setup

- The Git repository is cloned at build time using SSH.
- Your SSH key must have write access.
- You can edit Git username/email inside the Dockerfile.

---

## 📜 License

MIT — use it freely.

---

## 🤖 Example

**User sends:**  
`Try building a personal knowledge bot...`

Saved as file:  
`try_building_a_personal_knowledge.md`

File contents:

\`\`\`markdown
# Try building a personal knowledge bot...

*🕒 2025-05-07 13:45*

Try building a personal knowledge bot...
\`\`\`
