# main.py
import os
import threading
from flask import Flask
from MarketWatchdog import bot, DISCORD_TOKEN  # assumes bot.py exports these

app = Flask(__name__)

@app.route("/")
def alive():
    return "✅ Bot is running!", 200

def run_webserver():
    port = int(os.environ.get("PORT", 5000))
    app.run(
       host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )

if __name__ == "__main__":
    # 1) start Flask in a background thread
    threading.Thread(target=run_webserver, daemon=True).start()
    # 2) then start your Discord bot
    bot.run(DISCORD_TOKEN)
