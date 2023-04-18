from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

from modules import controller
from threading import Thread
import time

# clamp a number between a min and max
clamp = lambda n, _min, _max: max(min(n, _max), _min)

last_mobile_ping = 0

app = Flask(__name__, static_url_path="/static")
app.config["SECRET_KEY"] = "ninbuddy"
socketio = SocketIO(app)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route('/ping-server')
def get_data():
    is_mobile = request.args.get("is_mobile", default = False) == "true"
    uuid = request.args.get("uuid")

    if not is_mobile:
        return jsonify({"message": controller.state})
    
    if uuid not in controller.input_devices:
        Thread(target=controller.connect, args=(uuid,)).start()
        return jsonify({"message": controller.state})
    
    Thread(target=track_last_ping, args=(uuid,)).start()
    return jsonify({"message": controller.state})


def track_last_ping(uuid):
    global last_mobile_ping
    last_mobile_ping = time.time()
    time.sleep(5)

    if time.time() - last_mobile_ping >= 5:
        controller.disconnect(uuid)


@socketio.on("joystick-input")
def joystick_input(packet):
    packet["L_STICK"][0] = clamp(packet["L_STICK"][0], -100, 100)
    packet["L_STICK"][1] = clamp(packet["L_STICK"][1], -100, 100)
    packet["R_STICK"][0] = clamp(packet["R_STICK"][0], -100, 100)
    packet["R_STICK"][1] = clamp(packet["R_STICK"][1], -100, 100)

    controller.update_packet(["L_STICK", "X_VALUE"], packet["L_STICK"][0])
    controller.update_packet(["L_STICK", "Y_VALUE"], -packet["L_STICK"][1])
    controller.update_packet(["R_STICK", "X_VALUE"], packet["R_STICK"][0])
    controller.update_packet(["R_STICK", "Y_VALUE"], -packet["R_STICK"][1])
    
    print("JOY", packet)

@socketio.on("button-down")
def button_down(packet):
    controller.update_packet([packet], True)
    print("DOWN", packet)

@socketio.on("button-up")
def button_up(packet):
    controller.update_packet([packet], False)
    print("UP", packet)

def start():
    Thread(target=lambda: socketio.run(app, host="0.0.0.0", port="8000")).start()