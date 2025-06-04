import os
import re
import subprocess
import shutil
from datetime import datetime
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes
from telegram import Update
from telegram.ext import filters

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN")
FOLDER = '/app/InboxIdeas'

# Разрешённые ID пользователей
allowed_ids_raw = os.getenv("ALLOWED_IDS", "")
ALLOWED_USERS = set(int(uid.strip()) for uid in allowed_ids_raw.split(",") if uid.strip().isdigit())


def slugify(text: str) -> str:
    """
    Преобразует сообщение в безопасное имя файла: первые 5 слов, строчные буквы, без спецсимволов.
    """
    text = re.sub(r'[^\w\s-]', '', text)
    words = text.strip().lower().split()[:5]
    return '_'.join(words) or 'идея'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    print(f"🔍 Сообщение от {user_id}: {text}")

    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔️ У тебя нет доступа к этому боту.")
        print(f"❌ Попытка доступа от {user_id}")
        return

    if not text:
        await update.message.reply_text("⚠️ Пустое сообщение проигнорировано.")
        return

    os.makedirs(FOLDER, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    filename = slugify(text) + '.md'
    filepath = os.path.join(FOLDER, filename)

    # Запись содержимого в Markdown-файл
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {text[:60]}\n\n")
        f.write(f"*🕒 {timestamp}*\n\n")
        f.write(text)

    await update.message.reply_text(f"✅ Идея сохранена в файл `{filename}`")
    await git_commit_push(filename, update)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /start
    """
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔️ У тебя нет доступа к этому боту.")
        return
    await update.message.reply_text("👋 Отправь мне сообщение, и я сохраню его как Markdown-файл.")

async def git_commit_push(changed_file: str, update: Update = None):
    """
    Коммит и пуш нового файла в Git-репозиторий.
    """
    ssh_key_path = os.getenv("GIT_SSH_KEY_PATH", "/root/.ssh/obsidian_bot_ssh")
    os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key_path} -o StrictHostKeyChecking=no"

    repo_url = os.getenv("GIT_REPO_URL")
    if not repo_url:
        print("❌ Переменная GIT_REPO_URL не указана.")
        return

    # Клонируем репозиторий, если он ещё не инициализирован
    if not os.path.isdir(os.path.join(FOLDER, ".git")):
        print("📥 Репозиторий не найден. Клонируем...")
        try:
            if os.path.exists(FOLDER):
                print(f"⚠️ Папка {FOLDER} уже существует. Удаляем её перед клонированием...")
                shutil.rmtree(FOLDER)
            subprocess.run(["git", "clone", repo_url, FOLDER], check=True)
            print("✅ Репозиторий успешно клонирован.")
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ Не удалось клонировать репозиторий: {e}"
            print(error_msg)
            if update:
                await update.message.reply_text(error_msg)
            return

    try:
        print(f"🧠 Коммитим файл: {changed_file}")
        subprocess.run(["git", "add", changed_file], cwd=FOLDER, check=True)
        subprocess.run(["git", "commit", "-m", f"Добавлена идея: {changed_file}"], cwd=FOLDER, check=True)

        print("📥 Делаем git pull --rebase...")
        subprocess.run(["git", "pull", "--rebase"], cwd=FOLDER, check=True)

        print("📤 Пушим в удалённый репозиторий...")
        subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=FOLDER, check=True)
        print("✅ Пуш выполнен.")

    except subprocess.CalledProcessError as e:
        error_msg = f"❌ Ошибка Git: {e}"
        print(error_msg)
        if update:
            await update.message.reply_text(error_msg)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("📬 Бот запущен. Ждёт идей...")
    app.run_polling()

if __name__ == '__main__':
    main()