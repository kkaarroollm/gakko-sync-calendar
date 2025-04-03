#!/bin/bash

mkdir -p /app/logs
touch /app/logs/sync.log

grep -E "^(GAKKO_USERNAME|GAKKO_PASSWORD)=" < <(printenv) >> /etc/environment

{
  echo "SHELL=/bin/bash"
  echo "PATH=$PATH"
  echo "12 12 * * * root cd /app && /usr/local/bin/python3 /app/sync.py >> /app/logs/sync.log 2>&1"
  echo "0 3 */3 * * root find /app/logs -type f -name '*.log' -mtime +2 -delete"
} > /etc/cron.d/gakko-sync

chmod 0644 /etc/cron.d/gakko-sync
crontab /etc/cron.d/gakko-sync
