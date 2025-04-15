#!/bin/bash

mkdir -p /app/logs
touch /app/logs/sync.log

printenv | grep -E "^(GAKKO_USERNAME|GAKKO_PASSWORD|GAKKO_CLIENT_ID)=" >> /etc/environment


cat <<EOF > /etc/cron.d/gakko-sync
SHELL=/bin/bash
PATH=$PATH


##################
# Daily at 12:00.#
##################
* 12 * * * root cd /app && /usr/local/bin/python3 /app/main.py >> /app/logs/sync.log 2>&1


##############################################################
# Clean up logs. Every 3 days removes logs older than 5 days.#
##############################################################
0 3 */3 * * root find /app/logs -type f -name 'sync_*.log' -mtime +4 -delete
EOF

chmod 0644 /etc/cron.d/gakko-sync
crontab /etc/cron.d/gakko-sync

service cron start >/dev/null 2>&1 || cron
tail -F /app/logs/sync.log
