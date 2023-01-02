import pygame
import nxbt
import data
import json

def update_packet(location, state):
    if len(location) == 1:
        data.packet[location[0]] = state
    else:
        data.packet[location[0]][location[1]] = state


nx = nxbt.Nxbt()
data.setup(nx)
pygame.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()

controller_index = nx.create_controller(nxbt.PRO_CONTROLLER)
nx.wait_for_connection(controller_index)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            0 #finished
        
        elif event.type == pygame.JOYBUTTONDOWN:
            update_packet(data.button_map[event.button], True)
            print(f"{event.button} pressed")
        
        elif event.type == pygame.JOYBUTTONUP:
            update_packet(data.button_map[event.button], False)
            print(f"{event.button} released")
        
        nx.set_controller_input(controller_index, data.packet)
        #print(joystick.get_hat(0))



"""
controller_index = nx.create_controller(nxbt.PRO_CONTROLLER)

print("Connecting")

nx.wait_for_connection(controller_index)

print("Connected")

time.sleep(3)

nx.press_buttons(controller_index, [nxbt.Buttons.B])
"""