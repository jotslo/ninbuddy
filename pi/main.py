import pygame
import nxbt
import data

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
            data.button_map[event.button] = True
            print(f"{event.button} pressed")
        
        elif event.type == pygame.JOYBUTTONUP:
            data.button_map[event.button] = True
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