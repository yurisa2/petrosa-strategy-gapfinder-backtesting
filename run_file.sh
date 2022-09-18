cd /Users/yurisa2/petrosa/petrosa-strategy-gapfinder
export PORT=9091
gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
