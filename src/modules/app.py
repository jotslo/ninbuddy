from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from threading import Thread

app = Flask(__name__, static_url_path="/static")
app.config["SECRET_KEY"] = "ninbuddy"

socketio = SocketIO(app)

Thread(target=lambda: socketio.run(app, host="0.0.0.0", port="8000")).start()
