import os
import re
import subprocess
from datetime import datetime
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes
from telegram import Update
from telegram.ext import filters

# === Конфигурация ===
TOKEN = os.getenv("BOT_TOKEN")
FOLDER = '/app/InboxIdeas'

# Разрешённые ID пользователей из переменной окружения
allowed_ids_raw = os.getenv("ALLOWED_IDS", "")
ALLOWED_USERS = set(int(uid.strip()) for uid in allowed_ids_raw.split(",") if uid.strip().isdigit())

def slugify(text: str) -> str:
    """
    Преобразует текст сообщения в безопасное имя файла: строчные буквы, первые 5 слов, без спецсимволов.
    """
    text = re.sub(r'[^\w\s-]', '', text)
    words = text.strip().lower().split()[:5]
    return '_'.join(words) or 'idea'

async def ensure_git_repo(update: Update = None):
    """
    Клонирует репозиторий, если он ещё не инициализирован.
    """
    repo_url = os.getenv("GIT_REPO_URL")
    if not repo_url:
        print("❌ GIT_REPO_URL не задан.")
        return

    ssh_key_path = "/root/.ssh/obsidian_bot_ssh"
    os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key_path} -o StrictHostKeyChecking=no"

    if not os.path.isdir(os.path.join(FOLDER, ".git")):
        print("📥 Репозиторий не найден. Клонируем...")
        if os.path.isdir(FOLDER):
            print(f"⚠️ Папка {FOLDER} уже существует. Удаляем её перед клонированием...")
            subprocess.run(["rm", "-rf", FOLDER], check=True)
        try:
            subprocess.run(["git", "clone", repo_url, FOLDER], check=True)
            print("✅ Репозиторий успешно клонирован.")
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ Не удалось клонировать репозиторий: {e}"
            print(error_msg)
            if update:
                await update.message.reply_text(error_msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    print(f"🔍 Получено сообщение от {user_id}: {text}")

    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔️ У вас нет доступа к этому боту.")
        print(f"❌ Попытка несанкционированного доступа от {user_id}")
        return

    if not text:
        await update.message.reply_text("⚠️ Пустое сообщение проигнорировано.")
        return

    await ensure_git_repo(update)

    os.makedirs(FOLDER, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    filename = slugify(text) + '.md'
    filepath = os.path.join(FOLDER, filename)

    # Сохраняем сообщение в Markdown-файл
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {text[:60]}\n\n")
        f.write(f"*🕒 {timestamp}*\n\n")
        f.write(text)

    await update.message.reply_text(f"✅ Идея сохранена в файл `{filename}`")
    await git_commit_push(filename, update)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Ответ на команду /start.
    """
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔️ У вас нет доступа к этому боту.")
        return
    await update.message.reply_text("👋 Отправь мне сообщение, и я сохраню его как Markdown-файл с идеей!")

async def git_commit_push(changed_file: str, update: Update = None):
    """
    Коммит и пуш нового файла в Git-репозиторий.
    """
    ssh_key_path = "/root/.ssh/obsidian_bot_ssh"
    os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key_path} -o StrictHostKeyChecking=no"

    try:
        print(f"🧠 Коммитим файл: {changed_file}")
        subprocess.run(["git", "add", changed_file], cwd=FOLDER, check=True)
        subprocess.run(["git", "commit", "-m", f"Добавлена идея: {changed_file}"], cwd=FOLDER, check=True)

        print("📥 Выполняем git pull --rebase...")
        subprocess.run(["git", "pull", "--rebase"], cwd=FOLDER, check=True)

        print("📤 Отправляем изменения в удалённый репозиторий...")
        subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=FOLDER, check=True)
        print("✅ Пуш успешно завершён.")

    except subprocess.CalledProcessError as e:
        error_msg = f"❌ Ошибка Git: {e}"
        print(error_msg)
        if update:
            await update.message.reply_text(error_msg)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("📬 Бот запущен. Жду идеи...")
    app.run_polling()

if __name__ == '__main__':
    main()