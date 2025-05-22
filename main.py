# main.py
import os
import threading
from flask import Flask
from bot import bot, DISCORD_TOKEN  # assumes bot.py exports these

app = Flask(__name__)

@app.route("/")
def alive():
    return "✅ Bot is running!", 200

def run_webserver():
    port = int(os.environ.get("PORT", 5000))
    # bind to 0.0.0.0 so Render can route traffic in
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # 1) start Flask in a background thread
    threading.Thread(target=run_webserver).start()
    # 2) then start your Discord bot
    bot.run(DISCORD_TOKEN)
