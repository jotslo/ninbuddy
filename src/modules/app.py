from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from threading import Thread
from modules import data, controller, functions

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
        return jsonify({"message": data.state})

    if not data.is_mobile_connected:
        data.is_mobile_connected = True
        print("User has connected!")

        if data.controller == None:
            Thread(target=create_controller, args=(False,)).start()
            return jsonify({"message": data.state})
    
    Thread(target=track_last_ping).start()
    return jsonify({"message": data.state})

@socketio.on("joystick-input")
def joystick_input(packet):
    packet["L_STICK"][0] = functions.clamp(packet["L_STICK"][0], -100, 100)
    packet["L_STICK"][1] = functions.clamp(packet["L_STICK"][1], -100, 100)
    packet["R_STICK"][0] = functions.clamp(packet["R_STICK"][0], -100, 100)
    packet["R_STICK"][1] = functions.clamp(packet["R_STICK"][1], -100, 100)

    update_packet(["L_STICK", "X_VALUE"], packet["L_STICK"][0])
    update_packet(["L_STICK", "Y_VALUE"], -packet["L_STICK"][1])
    update_packet(["R_STICK", "X_VALUE"], packet["R_STICK"][0])
    update_packet(["R_STICK", "Y_VALUE"], -packet["R_STICK"][1])
    
    print("JOY", packet)

@socketio.on("button-down")
def button_down(packet):
    update_packet([packet], True)
    print("DOWN", packet)

@socketio.on("button-up")
def button_up(packet):
    update_packet([packet], False)
    print("UP", packet)

Thread(target=lambda: socketio.run(app, host="0.0.0.0", port="8000")).start()
