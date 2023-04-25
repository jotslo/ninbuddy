from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

from modules import controller, config
from threading import Thread
import time, subprocess

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
    
    if not controller.is_mobile_connected:
        controller.is_mobile_connected = True
    
        if not controller.is_physical_connected and not controller.is_disconnecting:
            conn = Thread(target=controller.connect)
            conn.daemon = True
            conn.start()
    
    # otherwise, update the last ping time and return the controller state
    track = Thread(target=track_last_ping)
    track.daemon = True
    track.start()
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
    # multiply by 1.5 to make more sensitive
    packet["L_STICK"][0] = clamp(packet["L_STICK"][0] * 1.5, -100, 100)
    packet["L_STICK"][1] = clamp(packet["L_STICK"][1] * 1.5, -100, 100)
    packet["R_STICK"][0] = clamp(packet["R_STICK"][0] * 1.5, -100, 100)
    packet["R_STICK"][1] = clamp(packet["R_STICK"][1] * 1.5, -100, 100)

    # update pending controller packet with joystick values
    controller.update_packet(["L_STICK", "X_VALUE"], packet["L_STICK"][0])
    controller.update_packet(["L_STICK", "Y_VALUE"], -packet["L_STICK"][1])
    controller.update_packet(["R_STICK", "X_VALUE"], packet["R_STICK"][0])
    controller.update_packet(["R_STICK", "Y_VALUE"], -packet["R_STICK"][1])

# when button pressed, update pending controller packet
@socketio.on("button-down")
def button_down(packet):
    controller.add_to_queue(packet, True)
    print(packet)

# when button released, update pending controller packet
@socketio.on("button-up")
def button_up(packet):
    controller.add_to_queue(packet, False)
    print(packet)

# start web server on local network with defined port
def start():
    socket = Thread(target=lambda: socketio.run(app, host="0.0.0.0", port=config.port))
    socket.daemon = True
    socket.start()

    # execute command to get ip
    controller.ip = subprocess.check_output("hostname -I | cut -f1 -d' '", shell=True)

    # print instructions for connecting to dashboard
    controller.update_state("Waiting for controller.")