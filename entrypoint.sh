#!/bin/bash

mkdir -p /app/logs

# Auto-detect Chrome/Chromium binary for arm64 compatibility
if [ -z "$GAKKO_CHROME_BINARY_PATH" ]; then
  if command -v google-chrome-stable >/dev/null 2>&1; then
    export GAKKO_CHROME_BINARY_PATH="$(command -v google-chrome-stable)"
  elif command -v chromium >/dev/null 2>&1; then
    export GAKKO_CHROME_BINARY_PATH="$(command -v chromium)"
  fi
fi

printenv | grep -E "^(GAKKO_USERNAME|GAKKO_PASSWORD|GAKKO_CLIENT_ID|GAKKO_CHROME_BINARY_PATH|PYTHONPATH)=" >> /etc/environment

cat <<EOF > /etc/cron.d/gakko-sync
SHELL=/bin/bash
PATH=$PATH

##################
# Daily at 12:00.#
##################
0 12 * * * cd /app && uv run python src/main.py

##############################################################
# Clean up logs. Every 3 days removes logs older than 5 days.#
##############################################################
0 3 */3 * * root find /app/logs -type f -name 'sync_*.log' -mtime +4 -delete
EOF

chmod 0644 /etc/cron.d/gakko-sync
crontab /etc/cron.d/gakko-sync

service cron start >/dev/null 2>&1 || cron
tail -F /dev/null
