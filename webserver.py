# webserver.py
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    # app.run(host='0.0.0.0', port=8080)
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False, threaded=True)


def start_webserver():
    t = Thread(target=run)
    t.start()
