from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import pygame
import nxbt
import data
import time
import os
import numpy
import random

app = Flask(__name__)
app.config["SECRET_KEY"] = "ninbuddy"
socketio = SocketIO(app)

state = "Waiting for Raspberry Pi..."
is_mobile_connected = False

global joystick
os.environ["SDL_VIDEODRIVER"] = "dummy"

def clamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/wrong-device")
def wrong_device():
    return render_template("wrong-device.html")

@app.route('/ping-server')
def get_data():
    global is_mobile_connected

    if not is_mobile_connected:
        is_mobile_connected = True
        print("User has connected!")

        if data.controller == None:
            threading.Thread(target=create_controller, args=(False,)).start()
            return jsonify({"message": state})
    
    threading.Thread(target=track_last_ping).start()
    return jsonify({"message": state})

@app.route('/main.js')
def get_main_js():
    with open('templates/main.js', 'r') as f:
        return f.read()

@app.route('/stylesheet.css')
def get_stylesheet():
    # Return the contents of stylesheet.css as a CSS response
    with open('templates/stylesheet.css', 'r') as f:
        return f.read()

def update_state(new_state):
    global state
    state = new_state

    if is_mobile_connected:
        pass
        #emit("get-state", new_state, broadcast=True)

def update_packet(location, value):
    if len(location) == 1:
        data.packet[location[0]] = value
    else:
        data.packet[location[0]][location[1]] = value

def update_joystick(joystick):
    update_packet(["L_STICK", "X_VALUE"], joystick.get_axis(0) * 100)
    update_packet(["L_STICK", "Y_VALUE"], joystick.get_axis(1) * -100)
    update_packet(["R_STICK", "X_VALUE"], joystick.get_axis(3) * 100)
    update_packet(["R_STICK", "Y_VALUE"], joystick.get_axis(4) * -100)

def create_controller(is_real):
    global joystick, state

    update_state("Connecting to console...")
    data.is_real_controller = is_real

    if is_real:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    data.controller = nx.create_controller(nxbt.PRO_CONTROLLER)
    nx.wait_for_connection(data.controller)
    update_state("Connected to console!")

"""@socketio.on("connect")
def on_connect():
    global is_mobile_connected
    print("User has connected!")
    is_mobile_connected = True

    if data.controller == None:
        create_controller(False)

@socketio.on("disconnect")
def on_disconnect():
    global is_mobile_connected
    print("User has disconnected!")

    if data.controller != None:
        update_state("Removing controller...")
        nx.remove_controller(data.controller)
        data.controller = None
    
    is_mobile_connected = False
    update_state("Waiting for controller...")"""

def disconnected():
    global is_mobile_connected

    if not is_mobile_connected:
        return

    print("User has disconnected!")

    if data.controller != None:
        update_state("Removing controller...")
        nx.remove_controller(data.controller)
        data.controller = None
    
    is_mobile_connected = False
    update_state("Waiting for controller...")

"""
@socketio.on("is-connected")
def is_connected():
    global is_mobile_connected

    if not is_mobile_connected:
        is_mobile_connected = True
        print("User has connected!")

        if data.controller == None:
            create_controller(False)
    
    else:
        data.last_mobile_ping = time.time()
        time.sleep(5)

        if time.time() - data.last_mobile_ping >= 5:
            disconnected()"""

def track_last_ping():
    data.last_mobile_ping = time.time()
    time.sleep(5)

    if time.time() - data.last_mobile_ping >= 5:
        disconnected()


@socketio.on("joystick-input")
def joystick_input(packet):
    packet["L_STICK"][0] = clamp(packet["L_STICK"][0], -100, 100)
    packet["L_STICK"][1] = clamp(packet["L_STICK"][1], -100, 100)
    packet["R_STICK"][0] = clamp(packet["R_STICK"][0], -100, 100)
    packet["R_STICK"][1] = clamp(packet["R_STICK"][1], -100, 100)

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

"""@socketio.on("input-packet")
def input_packet(packet):
    print("BTN", packet)
    for button_name in packet:
        if "STICK" in button_name:
            if packet[button_name]["identifier"]:
                data.packet[button_name]["X_VALUE"] = packet[button_name]["userinput"][0] / 5
                data.packet[button_name]["Y_VALUE"] = packet[button_name]["userinput"][1] / 5
            else:
                data.packet[button_name]["X_VALUE"] = 0
                data.packet[button_name]["Y_VALUE"] = 0
        else:
            if packet[button_name]["identifier"]:
                data.packet[button_name] = True
            else:
                data.packet[button_name] = False"""

if __name__ == '__main__':
    threading.Thread(target=lambda: socketio.run(app, host="0.0.0.0", port="1234")).start()


nx = nxbt.Nxbt()
data.setup(nx)
pygame.init()

if pygame.joystick.get_count() >= 1:
    create_controller(True)

while True:
    if data.controller != None:
        current_time = time.time()

        if current_time - data.last_movement > 1/120:
            if data.is_real_controller:
                update_joystick(joystick)
                data.last_movement = current_time

            nx.set_controller_input(data.controller, data.packet)

    for event in pygame.event.get():
        if event.type == pygame.JOYDEVICEADDED and pygame.joystick.get_count() == 1:
            if data.controller == None:
                create_controller(True)
        
        elif event.type == pygame.JOYDEVICEREMOVED and pygame.joystick.get_count() == 0:
            if data.controller != None:
                update_state("Removing controller...")
                nx.remove_controller(data.controller)
                data.controller = None
            update_state("Waiting for controller...")
        
        elif event.type == pygame.JOYBUTTONDOWN:
            update_packet(data.button_map[event.button], True)
        
        elif event.type == pygame.JOYBUTTONUP:
            update_packet(data.button_map[event.button], False)
        
        elif event.type == pygame.JOYHATMOTION:
            update_packet(["DPAD_UP"], False)
            update_packet(["DPAD_DOWN"], False)
            update_packet(["DPAD_LEFT"], False)
            update_packet(["DPAD_RIGHT"], False)

            if event.value[0] == 1:
                update_packet(["DPAD_RIGHT"], True)
            elif event.value[0] == -1:
                update_packet(["DPAD_LEFT"], True)
            if event.value[1] == 1:
                update_packet(["DPAD_UP"], True)
            elif event.value[1] == -1:
                update_packet(["DPAD_DOWN"], True)
        
        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 2:
                update_packet(["ZL"], event.value == 1.0)
            elif event.axis == 5:
                update_packet(["ZR"], event.value == 1.0)
            
            #if current_time - data.last_event > 1/120 or event.value == 0.0:
            #    update_joystick(event)
            #else:
            data.cached_event = event