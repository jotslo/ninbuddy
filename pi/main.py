import pygame
import nxbt
    
"""nx = nxbt.Nxbt()

controller_index = nx.create_controller(nxbt.PRO_CONTROLLER)

print("Connecting")

nx.wait_for_connection(controller_index)

print("Connected")

time.sleep(3)

nx.press_buttons(controller_index, [nxbt.Buttons.B])"""

pygame.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(joystick.get_name())

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