from modules import data
import time
import nxbt
import pygame

joystick = None

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

def create(is_real):
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


nx = nxbt.Nxbt()
data.setup(nx)
pygame.init()