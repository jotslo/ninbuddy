import pygame
import time
import os

from modules import controller, data

# if video driver is not set, set it to dummy value
# this allows us to use pygame without a display
if "SDL_VIDEODRIVER" not in os.environ:
    os.environ["SDL_VIDEODRIVER"] = "dummy"

last_movement = 0

global joystick

def update_joystick():
    global joystick
    controller.update_packet(["L_STICK", "X_VALUE"], joystick.get_axis(0) * 100)
    controller.update_packet(["L_STICK", "Y_VALUE"], joystick.get_axis(1) * -100)
    controller.update_packet(["R_STICK", "X_VALUE"], joystick.get_axis(3) * 100)
    controller.update_packet(["R_STICK", "Y_VALUE"], joystick.get_axis(4) * -100)

def listen():
    global last_movement, joystick
    pygame.init()

    if pygame.joystick.get_count() >= 1:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        controller.connect(0)

    while True:
        if controller.device != None:
            current_time = time.time()

            if current_time - last_movement > 1/120:
                if controller.is_real_controller:
                    update_joystick(joystick)
                    last_movement = current_time

                controller.nx.set_controller_input( controller.device, controller.packet)

        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEADDED and pygame.joystick.get_count() == 1:
                if controller.device == None:
                    joystick = pygame.joystick.Joystick(0)
                    joystick.init()
                    controller.connect(0)
            
            elif event.type == pygame.JOYDEVICEREMOVED and pygame.joystick.get_count() == 0:
                controller.disconnect(0)
            
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