#!/bin/bash

# Cron script - triggers batch processing on schedule
# Add to crontab: 0 * * * * /path/to/chat-app/scripts/cron.sh

cd "$(dirname "$0")/.."

echo "$(date): Running scheduled batch processing..."

# Trigger batch via API
curl -s -X POST http://localhost:8000/api/system/batch/trigger \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  || echo "Warning: Could not trigger batch"

# Optional: Clean up old compressed files (older than 30 days)
find storage/data -name "*.zst" -mtime +30 -delete 2>/dev/null || true

echo "$(date): Scheduled batch completed"