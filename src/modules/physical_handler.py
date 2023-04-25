import pygame
import time

from modules import controller, input_maps
from threading import Thread

# store last movement time & joystick object
last_movement = 0
joystick = None

# update joystick values in packet
def update_joystick():
    global last_movement, joystick
    current_time = time.time()

    # if 120th of a second has passed, update joystick values
    if current_time - last_movement > 1/120:
        input_maps.axis_move(joystick)

        # update last movement time
        last_movement = current_time

# connect physical controller
def connect_physical():
    global joystick

    # if physical controller is already connected, ignore
    if controller.is_physical_connected:
        return
    
    # initialise the connected physical controller
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    
    # update controller name & physical connection status
    controller.name = joystick.get_name()
    controller.is_physical_connected = True
    
    # if mobile device isn't in-use, use physical controller
    if not controller.is_mobile_connected:
        conn = Thread(target=controller.connect)
        conn.daemon = True
        conn.start()

# listen for physical controller input
def listen():
    global last_movement, joystick

    # initialise pygame for easy access to joystick input
    pygame.init()

    # if physical controller is already connected, connect to switch
    if pygame.joystick.get_count() >= 1:
        connect_physical()
    
    # consistently check for input changes
    while True:

        # if physical controller is connected, update joystick each frame
        if controller.device != None:
            if controller.is_physical_connected:
                update_joystick()
        
            # update input packet sent to switch each frame
            controller.set_input()

        # for each event in pygame event queue
        for event in pygame.event.get():
            try:
                # if new physical controller is added for the first time, connect to switch
                if event.type == pygame.JOYDEVICEADDED and pygame.joystick.get_count() == 1:
                    connect_physical()
                
                # if physical controller is removed, attempt to disconnect from switch
                elif event.type == pygame.JOYDEVICEREMOVED and pygame.joystick.get_count() == 0:
                    controller.name = None
                    joystick.quit()
                    controller.is_physical_connected = False
                    disconn = Thread(target=controller.attempt_disconnect)
                    disconn.daemon = True
                    disconn.start()
                
                # if controller button is pressed, update packet accordingly
                elif event.type == pygame.JOYBUTTONDOWN:
                    input_maps.button_down(event.button)
                
                # if controller button is released, update packet accordingly
                elif event.type == pygame.JOYBUTTONUP:
                    input_maps.button_up(event.button)
                
                # if controller dpad is moved, update packet accordingly
                elif event.type == pygame.JOYHATMOTION:
                    input_maps.dpad_move(event.value)

                # if ZL or ZR are pressed, update packet accordingly
                # these are triggers on xbox & ps, so apply if 75% or more is pressed
                elif event.type == pygame.JOYAXISMOTION:
                    input_maps.z_button_move(event.axis, event.value)

            except Exception:
                # ignore any errors that occur
                # prevents software from crashing
                pass