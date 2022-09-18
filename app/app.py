import os
from app import petrosa_backtesting
from datetime import datetime
import threading


from flask import Flask

app = Flask(__name__)

start_datetime = datetime.utcnow()

threading.Thread(target=petrosa_backtesting.continuous_run).start()


@app.route("/")
def default():

    return "ok", 200


@app.route("/status")
def queues():
    queues = {}

    queues['start_datetime'] = start_datetime

    return queues, 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
