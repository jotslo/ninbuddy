from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import pygame
import nxbt
import data
import time
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "ninbuddy"
socketio = SocketIO(app)

state = "Waiting for controller..."

global joystick
os.environ["SDL_VIDEODRIVER"] = "dummy"

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route('/data')
def get_data():
    data = {
        "message": state,
        "real_controller": data.controller != None
    }

    return jsonify(data)

@app.route('/main.js')
def get_main_js():
    with open('templates/main.js', 'r') as f:
        return f.read()

@app.route('/stylesheet.css')
def get_stylesheet():
    # Return the contents of stylesheet.css as a CSS response
    with open('templates/stylesheet.css', 'r') as f:
        return f.read()

def update_packet(location, state):
    if len(location) == 1:
        data.packet[location[0]] = state
    else:
        data.packet[location[0]][location[1]] = state

def update_joystick(joystick):
    update_packet(["L_STICK", "X_VALUE"], joystick.get_axis(0) * 100)
    update_packet(["L_STICK", "Y_VALUE"], joystick.get_axis(1) * -100)
    update_packet(["R_STICK", "X_VALUE"], joystick.get_axis(3) * 100)
    update_packet(["R_STICK", "Y_VALUE"], joystick.get_axis(4) * -100)

def create_controller(is_real):
    global joystick, state

    state = "Connecting controller..."
    data.is_real_controller = is_real

    if is_real:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    data.controller = nx.create_controller(nxbt.PRO_CONTROLLER)
    nx.wait_for_connection(data.controller)
    state = "Controller connected!"

@socketio.on("connect")
def on_connect():
    print("Connected!")

    if data.controller == None:
        create_controller(False)
    
    emit("ready-for-input", True)

@socketio.on("disconnect")
def on_disconnect():
    print("Disconnected!")

@socketio.on("get-state")
def get_state():
    emit("get-state", state)

@socketio.on("input-packet")
def input_packet(packet):
    print(packet)

if __name__ == '__main__':
    threading.Thread(target=lambda: socketio.run(app, host="0.0.0.0", port="7999", debug=True, use_reloader=False)).start()

nx = nxbt.Nxbt()
data.setup(nx)
pygame.init()

if pygame.joystick.get_count() >= 1:
    create_controller(True)

while True:
    if data.controller != None:
        if data.is_real_controller:
            current_time = time.time()

            if current_time - data.last_movement > 1/120:
                update_joystick(joystick)
                data.last_movement = current_time

        nx.set_controller_input(data.controller, data.packet)

    for event in pygame.event.get():
        if event.type == pygame.JOYDEVICEADDED and pygame.joystick.get_count() == 1:
            if data.controller == None:
                create_controller(True)
        
        elif event.type == pygame.JOYDEVICEREMOVED and pygame.joystick.get_count() == 0:
            if data.controller != None:
                state = "Removing controller..."
                nx.remove_controller(data.controller)
                data.controller = None
            state = "Waiting for controller..."
        
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