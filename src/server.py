from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import pygame
import nxbt
import time
import os
import numpy
import random

from modules import data, functions

global joystick

app = Flask(__name__)
app.config["SECRET_KEY"] = "ninbuddy"
socketio = SocketIO(app)

# if video driver is not set, set it to dummy
if not os.environ["SDL_VIDEODRIVER"]:
    os.environ["SDL_VIDEODRIVER"] = "dummy"

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
            threading.Thread(target=create_controller, args=(False,)).start()
            return jsonify({"message": data.state})
    
    threading.Thread(target=track_last_ping).start()
    return jsonify({"message": data.state})


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
    global joystick

    data.state = "Connecting to console..."
    data.is_real_controller = is_real

    if is_real:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    data.controller = nx.create_controller(nxbt.PRO_CONTROLLER)
    nx.wait_for_connection(data.controller)
    data.state = "Connected to console!"

def disconnected():
    if not data.is_mobile_connected:
        return

    print("User has disconnected!")

    if data.controller != None:
        data.state = "Removing controller..."

        try:
            nx.remove_controller(data.controller)
        except KeyError:
            print("Controller removed during connection.")

        data.controller = None
    
    data.is_mobile_connected = False
    data.state = "Waiting for controller..."


def track_last_ping():
    data.last_mobile_ping = time.time()
    time.sleep(5)

    if time.time() - data.last_mobile_ping >= 5:
        disconnected()


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

if __name__ == '__main__':
    threading.Thread(target=lambda: socketio.run(app, host="0.0.0.0", port="9000")).start()

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
            disconnected()
        
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
            
            data.cached_event = event