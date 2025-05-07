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
COPY bot.py .

# Clone the target notes repository using SSH
ARG GIT_SSH_KEY_PATH
ENV GIT_SSH_COMMAND="ssh -i ${GIT_SSH_KEY_PATH} -o StrictHostKeyChecking=no"
RUN git clone git@github.com:your_name/your_repo.git InboxIdeas

# Start the bot
CMD ["python", "-u", "bot.py"]