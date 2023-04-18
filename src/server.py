from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import pygame
import nxbt
import time
import os
import numpy
import random

from modules import data, functions, controller

global joystick

app = Flask(__name__, static_url_path="/static")
app.config["SECRET_KEY"] = "ninbuddy"
socketio = SocketIO(app)

# if video driver is not set, set it to dummy
if "SDL_VIDEODRIVER" not in os.environ:
    os.environ["SDL_VIDEODRIVER"] = "dummy"

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
            threading.Thread(target=controller.connect, args=(False,)).start()
            return jsonify({"message":  controller.state})
    
    threading.Thread(target=track_last_ping).start()
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
    threading.Thread(target=lambda: socketio.run(app, host="0.0.0.0", port="9000")).start()

### move nxbt stuff to controller.py
#data.setup(nx)
pygame.init()

if pygame.joystick.get_count() >= 1:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    controller.connect(True)

while True:
    if controller.controller != None:
        current_time = time.time()

        if current_time - data.last_movement > 1/120:
            if  controller.is_real_controller:
                controller.update_joystick(joystick)
                data.last_movement = current_time

            controller.nx.set_controller_input( controller.controller, controller.packet)

    for event in pygame.event.get():
        if event.type == pygame.JOYDEVICEADDED and pygame.joystick.get_count() == 1:
            if  controller.controller == None:
                joystick = pygame.joystick.Joystick(0)
                joystick.init()
                controller.connect(True)
        
        elif event.type == pygame.JOYDEVICEREMOVED and pygame.joystick.get_count() == 0:
            controller.disconnect()
        
        elif event.type == pygame.JOYBUTTONDOWN:
            controller.update_packet(data.button_map[event.button], True)
        
        elif event.type == pygame.JOYBUTTONUP:
            controller.update_packet(data.button_map[event.button], False)
        
        elif event.type == pygame.JOYHATMOTION:
            controller.update_packet(["DPAD_UP"], False)
            controller.update_packet(["DPAD_DOWN"], False)
            controller.update_packet(["DPAD_LEFT"], False)
            controller.update_packet(["DPAD_RIGHT"], False)

            if event.value[0] == 1:
                controller.update_packet(["DPAD_RIGHT"], True)
            elif event.value[0] == -1:
                controller.update_packet(["DPAD_LEFT"], True)
            if event.value[1] == 1:
                controller.update_packet(["DPAD_UP"], True)
            elif event.value[1] == -1:
                controller.update_packet(["DPAD_DOWN"], True)
        
        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 2:
                controller.update_packet(["ZL"], event.value == 1.0)
            elif event.axis == 5:
                controller.update_packet(["ZR"], event.value == 1.0)
            
            data.cached_event = event