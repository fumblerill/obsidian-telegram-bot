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

## 🚀 Deploy Instructions

1. **Clone the repository** to your server:
   ```bash
   git clone git@github.com:yourname/obsidian-telegram-bot.git
   cd obsidian-telegram-bot
   ```

2. **Copy your SSH key** (with write access to the target notes repository) to your server.  
   Example path: `/home/user/.ssh/obsidian_bot_ssh`

3. **Create and edit the `.env` file**:
   ```bash
   cp .env.example .env
   ```
   Fill in the required variables:
   ```
   BOT_TOKEN=...
   ALLOWED_IDS=...
   GIT_REPO_URL=git@github.com:yourname/obsidian-inbox.git
   GIT_SSH_KEY_PATH=/home/user/.ssh/obsidian_bot_ssh
   ```

4. **Edit the Dockerfile** if needed:
   - To switch between bot languages:
     ```dockerfile
     COPY bot.py .      # English version
     # COPY bot.ru.py . # Russian version
     ```
   - Set Git commit identity:
     ```dockerfile
     RUN git config --global user.name "Your Name"
     RUN git config --global user.email "you@example.com"
     ```

5. **Build and run** the container:
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
