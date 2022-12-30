import pygame
import os

import nxbt

import time

"""
Button Map:
00 - B
01 - A
02 - Y
03 - X
04 - L
05 - R
06 - ZL
07 - ZR
08 - Minus
09 - Plus
10 - LStick
11 - RStick
12 - Home
13 - Capture

# Hat Map:
(0,  1) - DPad Up
(0, -1) - DPad Down
(-1, 0) - DPad Left
(1,  0) - DPad Right
"""

os.environ["SDL_VIDEODRIVER"] = "dummy"
"""
nx = nxbt.Nxbt()
pygame.init()

controller_index = nx.create_controller(nxbt.PRO_CONTROLLER)

print("Connecting")

nx.wait_for_connection(controller_index)

print("Connected")

time.sleep(3)

nx.press_buttons(controller_index, [nxbt.Buttons.B])

print(nx.create_input_packet())"""

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
        
        #print(joystick.get_hat(0))



adapters = nx.get_available_adapters()

print(len(adapters))



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