FROM python:3.13
WORKDIR /app

RUN apt update && apt install -y \
    cron wget unzip curl gnupg ca-certificates \
    libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 \
    libxss1 libappindicator3-1 libasound2 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libgbm1 && \
    apt clean

RUN LATEST=$(curl -s https://commondatastorage.googleapis.com/chromium-browser-snapshots/Linux_x64/LAST_CHANGE) && \
    wget https://commondatastorage.googleapis.com/chromium-browser-snapshots/Linux_x64/${LATEST}/chrome-linux.zip && \
    unzip chrome-linux.zip && \
    mv chrome-linux /opt/chromium && \
    ln -s /opt/chromium/chrome /usr/bin/google-chrome

ENV PATH="/opt/chromium:${PATH}"

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN mkdir -p ./logs && \
    echo "30 9 * * * python /app/sync.py >> /app/logs/sync.log 2>&1" > /etc/cron.d/gakko-sync && \
    echo "0 3 */3 * * find /app/logs -type f -name '*.log' -mtime +2 -delete" >> /etc/cron.d/gakko-sync && \
    chmod 0644 /etc/cron.d/gakko-sync && \
    crontab /etc/cron.d/gakko-sync

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
