cd /Users/yurisa2/petrosa/petrosa-data-crypto/petrosa-backfiller-binance
export PORT=8081
export ENABLE_RUN=yes
gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
