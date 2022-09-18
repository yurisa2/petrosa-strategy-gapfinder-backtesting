import os
from app import sender
from app import binance_backfiller
from datetime import datetime
import threading


from flask import Flask

app = Flask(__name__)

start_datetime = datetime.utcnow()

sender = sender.PETROSASender('binance_socket_raw')

backfiller = binance_backfiller.BinanceBackfiller(sender)

threading.Thread(target=backfiller.continuous_run).start()


@app.route("/")
def default():

    return "ok", 200


@app.route("/status")
def queues():
    queues = {}

    queues['start_datetime'] = start_datetime
    queues['total_sent'] = sender.total_sent

    return queues, 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
