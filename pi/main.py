import bluetooth
import subprocess
import evdev

import pygame
import os
import sys

"""
Button Map:
0 - B
1 - A
2 - Y
3 - X
4 - L
5 - R
6 - ZL
7 - ZR
8 - Minus
9 - Plus
10 - LStick
11 - RStick
12 - Home
13 - Capture

# not working?
14 - DPad Up
15 - DPad Down
16 - DPad Left
17 - DPad Right

"""

os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()

joystick = pygame.joystick.Joystick(0)

joystick.init()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            0 #finished
        
        elif event.type == pygame.JOYBUTTONDOWN:
            print(f"{event.button} pressed")
        
        elif event.type == pygame.JOYBUTTONUP:
            print(f"{event.button} released")
        
        print(joystick.get_hat(0))

"""from inputs import get_gamepad

while True:
    events = get_gamepad()
    for event in events:
        print(event.ev_type, event.code, event.state)"""

"""from pyjoystick.sdl2 import Key, Joystick, run_event_loop


def print_add(joy):
    print("Added", joy)

def print_remove(joy):
    print("Removed", joy)

def key_received(key):
    print("Key:", key)

run_event_loop(print_add, print_remove, key_received)"""


"""devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
controller = None

for device in devices:
    if device.name == "Pro Controller":
        controller = evdev.InputDevice(device.path)
        break


if controller:
    while True:
        event = controller.read_one()
        if event:
            print(event)"""

"""nx = nxbt.Nxbt()

adapters = nx.get_available_adapters()

print(len(adapters))

controller_index = nx.create_controller(nxbt.PRO_CONTROLLER)

print("Connecting")

nx.wait_for_connection(controller_index)

print("Connected")

time.sleep(3)

nx.press_buttons(controller_index, [nxbt.Buttons.B])"""

"""port = 1
passkey = "0000"

print("Scanning for devices...")
nearby_devices = bluetooth.discover_devices(lookup_names=True)

for addr, name in nearby_devices:
    print("  %s - %s" % (addr, name))

    if "Pro Controller" in name:
        print("Found Pro Controller!")

        subprocess.run(["rfkill", "unblock", "bluetooth"], check=True, shell=True)
        subprocess.run("bluetoothctl", check=True, shell=True)
        subprocess.run(["power", "on"], check=True, shell=True)
        subprocess.run(["pair", addr], check=True, shell=True)
        subprocess.run(["connect", addr], check=True, shell=True)
        print("Connected!")
        break"""