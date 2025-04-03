#!/bin/bash
touch /app/logs/sync.log
cron
tail -f /app/logs/sync.log
