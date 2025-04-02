FROM python:3.11

USER root

ENV PYTHONUNBUFFERED=1

RUN apt update && \
    apt install -y cron chromium chromium-driver && \
    apt clean && \
    ln -s /usr/bin/chromium /usr/bin/google-chrome

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN echo "0 7 * * * python /app/sync.py >> /var/log/cron.log 2>&1" > /etc/cron.d/gakko-cron
RUN chmod 0644 /etc/cron.d/gakko-cron && crontab /etc/cron.d/gakko-cron
RUN touch /var/log/cron.log

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
