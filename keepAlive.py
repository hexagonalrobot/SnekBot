# SnekBot keepAlive webserver for replit
#
# This program allows the python bot to be active on a replit based web server.
#
# @author robot-artificer
# @version 1.5

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I am alive?"

def run():
    app.run(host='0.0.0.0', port=8080)

def keepAlive():
    t = Thread(target=run)
    t.start()