from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

from modules import controller, data, functions
from threading import Thread
import time

app = Flask(__name__, static_url_path="/static")
app.config["SECRET_KEY"] = "ninbuddy"
socketio = SocketIO(app)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route('/ping-server')
def get_data():
    is_mobile = request.args.get("is_mobile", default = False) == "true"

    if not is_mobile:
        return jsonify({"message":  controller.state})

    if not controller.is_mobile_connected:
        controller.is_mobile_connected = True
        print("User has connected!")

        if controller.controller == None:
            Thread(target=controller.connect, args=(False,)).start()
            return jsonify({"message":  controller.state})
    
    Thread(target=track_last_ping).start()
    return jsonify({"message":  controller.state})


def track_last_ping():
    data.last_mobile_ping = time.time()
    time.sleep(5)

    if time.time() - data.last_mobile_ping >= 5:
        controller.disconnect()


@socketio.on("joystick-input")
def joystick_input(packet):
    packet["L_STICK"][0] = functions.clamp(packet["L_STICK"][0], -100, 100)
    packet["L_STICK"][1] = functions.clamp(packet["L_STICK"][1], -100, 100)
    packet["R_STICK"][0] = functions.clamp(packet["R_STICK"][0], -100, 100)
    packet["R_STICK"][1] = functions.clamp(packet["R_STICK"][1], -100, 100)

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

if __name__ == '__main__':
    Thread(target=lambda: socketio.run(app, host="0.0.0.0", port="9000")).start()