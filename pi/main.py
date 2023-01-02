import pygame
import nxbt
import data
import json
import time
import threading

def update_packet(location, state):
    if len(location) == 1:
        data.packet[location[0]] = state
    else:
        data.packet[location[0]][location[1]] = state
    

def update_joystick(event):
    if event.axis == 0:
        update_packet(["L_STICK", "X_VALUE"], event.value * 100)
    elif event.axis == 1:
        update_packet(["L_STICK", "Y_VALUE"], event.value * -100)
    elif event.axis == 3:
        update_packet(["R_STICK", "X_VALUE"], event.value * 100)
    elif event.axis == 4:
        update_packet(["R_STICK", "Y_VALUE"], event.value * -100)

nx = nxbt.Nxbt()
data.setup(nx)
pygame.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()

controller_index = nx.create_controller(nxbt.PRO_CONTROLLER)
nx.wait_for_connection(controller_index)

while True:
    current_time = time.time()

    if current_time - data.last_event > 1/120 and data.cached_event:
        update_joystick(data.cached_event)
        data.cached_event = None
        data.last_event = current_time
    
    nx.set_controller_input(controller_index, data.packet)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            0 #finished
        
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
            data.last_event = current_time