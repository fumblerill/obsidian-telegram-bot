FROM python:3.11-slim

WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y git openssh-client && apt-get clean

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Configure Git user for commits
RUN git config --global user.name "change_to_you"
RUN git config --global user.email "you@mail.com"

# Copy the bot source code
COPY . .

# Start the bot
CMD ["python", "-u", "bot.py"]