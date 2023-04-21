from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

from modules import controller
from threading import Thread
import time

# clamp a number between a min and max
clamp = lambda n, _min, _max: max(min(n, _max), _min)

# last time a mobile device pinged the server
last_mobile_ping = 0

# declare variables for web server
app = Flask(__name__, static_url_path="/static")
app.config["SECRET_KEY"] = "ninbuddy"
socketio = SocketIO(app)

# return the dashboard page upon visiting the root url
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# mobile device pings this url each second for latest controller data
@app.route('/ping-server')
def get_data():
    is_mobile = request.args.get("is_mobile", default = False) == "true"

    # if the ping isn't from a mobile device, just return controller state
    if not is_mobile:
        return jsonify({"message": controller.state})
    
    # if no controller is connected, connect a new controller to switch
    if not (controller.is_mobile_connected or controller.is_physical_connected or controller.is_disconnecting):
        controller.is_mobile_connected = True
        Thread(target=controller.connect).start()
        return jsonify({"message": controller.state})
    
    # otherwise, update the last ping time and return the controller state
    Thread(target=track_last_ping).start()
    return jsonify({"message": controller.state})

# update last mobile ping time each second
def track_last_ping():
    global last_mobile_ping
    last_mobile_ping = time.time()
    time.sleep(5)

    # if the last ping was more than 5 seconds ago, disconnect the controller
    if time.time() - last_mobile_ping >= 5:
        last_mobile_ping = time.time()
        controller.is_mobile_connected = False
        controller.attempt_disconnect()

# forward joystick input to controller when received from mobile device
@socketio.on("joystick-input")
def joystick_input(packet):
    # clamp joystick values between -100 and 100 to prevent errors
    packet["L_STICK"][0] = clamp(packet["L_STICK"][0], -100, 100)
    packet["L_STICK"][1] = clamp(packet["L_STICK"][1], -100, 100)
    packet["R_STICK"][0] = clamp(packet["R_STICK"][0], -100, 100)
    packet["R_STICK"][1] = clamp(packet["R_STICK"][1], -100, 100)

    # update pending controller packet with joystick values
    controller.update_packet(["L_STICK", "X_VALUE"], packet["L_STICK"][0])
    controller.update_packet(["L_STICK", "Y_VALUE"], -packet["L_STICK"][1])
    controller.update_packet(["R_STICK", "X_VALUE"], packet["R_STICK"][0])
    controller.update_packet(["R_STICK", "Y_VALUE"], -packet["R_STICK"][1])
    
    # output joystick values to console
    print("JOY", packet)

# when button pressed, update pending controller packet
@socketio.on("button-down")
def button_down(packet):
    controller.update_packet([packet], True)
    print("DOWN", packet)

# when button released, update pending controller packet
@socketio.on("button-up")
def button_up(packet):
    controller.update_packet([packet], False)
    print("UP", packet)

# start web server on local network with port 8000
def start():
    Thread(target=lambda: socketio.run(app, host="0.0.0.0", port="8000")).start()