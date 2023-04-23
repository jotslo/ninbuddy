import pygame
import time
import os

from modules import controller, input_maps

# if video driver is not set, set it to dummy value
# this allows us to use pygame without a display
if "SDL_VIDEODRIVER" not in os.environ:
    os.environ["SDL_VIDEODRIVER"] = "dummy"

# store last movement time & joystick object
last_movement = 0
joystick = None

# update joystick values in packet
def update_joystick():
    global last_movement, joystick
    current_time = time.time()

    # if 120th of a second has passed, update joystick values
    if current_time - last_movement > 1/120:
        controller.update_packet(["L_STICK", "X_VALUE"], joystick.get_axis(0) * 100)
        controller.update_packet(["L_STICK", "Y_VALUE"], joystick.get_axis(1) * -100)
        controller.update_packet(["R_STICK", "X_VALUE"], joystick.get_axis(3) * 100)
        controller.update_packet(["R_STICK", "Y_VALUE"], joystick.get_axis(4) * -100)

        # update last movement time
        last_movement = current_time
    
    # update input packet sent to switch accordingly
    controller.nx.set_controller_input(controller.device, controller.packet)

# connect physical controller
def connect_physical():
    global joystick

    # if physical controller is already connected, ignore
    if controller.is_physical_connected:
        return
    
    # initialise the connected physical controller
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    controller.is_physical_connected = True
    
    # if mobile device isn't in-use, use physical controller
    if not controller.is_mobile_connected:
        controller.connect()

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
        if controller.device != None and controller.is_physical_connected:
            update_joystick()

        # for each event in pygame event queue
        for event in pygame.event.get():

            # if new physical controller is added for the first time, connect to switch
            if event.type == pygame.JOYDEVICEADDED and pygame.joystick.get_count() == 1:
                connect_physical()
            
            # if physical controller is removed, attempt to disconnect from switch
            elif event.type == pygame.JOYDEVICEREMOVED and pygame.joystick.get_count() == 0:
                controller.is_physical_connected = False
                controller.attempt_disconnect()
            
            # if controller button is pressed, update packet accordingly
            elif event.type == pygame.JOYBUTTONDOWN:
                controller.update_packet(input_maps.button_map[event.button], True)
            
            # if controller button is released, update packet accordingly
            elif event.type == pygame.JOYBUTTONUP:
                controller.update_packet(input_maps.button_map[event.button], False)
            
            # if controller dpad is moved, update packet accordingly
            elif event.type == pygame.JOYHATMOTION:

                # reset dpad values
                controller.update_packet(["DPAD_UP"], False)
                controller.update_packet(["DPAD_DOWN"], False)
                controller.update_packet(["DPAD_LEFT"], False)
                controller.update_packet(["DPAD_RIGHT"], False)

                # update dpad values based on current values
                if event.value[0] == 1:
                    controller.update_packet(["DPAD_RIGHT"], True)
                elif event.value[0] == -1:
                    controller.update_packet(["DPAD_LEFT"], True)
                if event.value[1] == 1:
                    controller.update_packet(["DPAD_UP"], True)
                elif event.value[1] == -1:
                    controller.update_packet(["DPAD_DOWN"], True)
            
            # if controller trigger buttons are moved, update packet accordingly

            # ZL & ZR are buttons unlike most controllers,
            # so only apply user input if pressed past 75% of the way down
            elif event.type == pygame.JOYAXISMOTION:
                if event.axis == 2:
                    controller.update_packet(["ZL"], event.value >= 0.75)
                elif event.axis == 5:
                    controller.update_packet(["ZR"], event.value >= 0.75)