import os
import re
import subprocess
import shutil
from datetime import datetime
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes
from telegram import Update
from telegram.ext import filters

# === Configuration ===
TOKEN = os.getenv("BOT_TOKEN")
FOLDER = '/app/InboxIdeas'

# Allowed user IDs from environment variable
allowed_ids_raw = os.getenv("ALLOWED_IDS", "")
ALLOWED_USERS = set(int(uid.strip()) for uid in allowed_ids_raw.split(",") if uid.strip().isdigit())


def slugify(text: str) -> str:
    """
    Convert a message text into a safe filename: lowercase, first 5 words, no special characters.
    """
    text = re.sub(r'[^\w\s-]', '', text)
    words = text.strip().lower().split()[:5]
    return '_'.join(words) or 'idea'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    print(f"🔍 Message from {user_id}: {text}")

    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔️ You are not authorized to use this bot.")
        print(f"❌ Unauthorized access attempt by {user_id}")
        return

    if not text:
        await update.message.reply_text("⚠️ Empty message ignored.")
        return

    os.makedirs(FOLDER, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    filename = slugify(text) + '.md'
    filepath = os.path.join(FOLDER, filename)

    # Write content to Markdown file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {text[:60]}\n\n")
        f.write(f"*🕒 {timestamp}*\n\n")
        f.write(text)

    await update.message.reply_text(f"✅ Idea saved as `{filename}`")
    await git_commit_push(filename, update)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Respond to /start command.
    """
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔️ You are not authorized to use this bot.")
        return
    await update.message.reply_text("👋 Send me a message and I'll save it as a Markdown idea!")

async def git_commit_push(changed_file: str, update: Update = None):
    """
    Commit and push the new idea file to the Git repository.
    """
    ssh_key_path = "/root/.ssh/obsidian_bot_ssh"
    os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key_path} -o StrictHostKeyChecking=no"

    repo_url = os.getenv("GIT_REPO_URL")
    if not repo_url:
        print("❌ GIT_REPO_URL is not set.")
        return

    # Clone the repository if it's not initialized
    if not os.path.isdir(os.path.join(FOLDER, ".git")):
        print("📥 Repository not found. Cloning...")
        try:
            if os.path.exists(FOLDER):
                print(f"⚠️ Folder {FOLDER} exists, removing it before clone...")
                shutil.rmtree(FOLDER)
            subprocess.run(["git", "clone", repo_url, FOLDER], check=True)
            print("✅ Repository successfully cloned.")
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ Failed to clone the repository: {e}"
            print(error_msg)
            if update:
                await update.message.reply_text(error_msg)
            return

    try:
        print(f"🧠 Committing file: {changed_file}")
        subprocess.run(["git", "add", changed_file], cwd=FOLDER, check=True)
        subprocess.run(["git", "commit", "-m", f"Added idea: {changed_file}"], cwd=FOLDER, check=True)

        print("📥 Running git pull --rebase...")
        subprocess.run(["git", "pull", "--rebase"], cwd=FOLDER, check=True)

        print("📤 Pushing to remote...")
        subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=FOLDER, check=True)
        print("✅ Push completed.")

    except subprocess.CalledProcessError as e:
        error_msg = f"❌ Git error: {e}"
        print(error_msg)
        if update:
            await update.message.reply_text(error_msg)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("📬 Bot started. Waiting for ideas...")
    app.run_polling()

if __name__ == '__main__':
    main()