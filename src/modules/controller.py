import nxbt, time, os
from modules import config

# start nxbt and get format for input packet
# input packet is sent to switch each frame
nx = nxbt.Nxbt()
packet = nx.create_input_packet()

packet_queue = {}

last_input = 0

# variables containing current controller and its visual state
device = None
state = "Waiting for controller..."

# name of physical controller (e.g. "Xbox Series X Controller")
name = None

# variables that determine connection state
is_physical_connected = False
is_mobile_connected = False
is_disconnecting = False

# declare colours for console output
red = "\033[31m"
bold = "\033[1m"
green = "\033[32m"
reset = "\033[0m"

# ip of raspberry pi
ip = None

extract_dir = f"/home/{os.environ.get('SUDO_USER')}/ninbuddy"

def update_state(new_state):
    global state
    state = new_state

    os.system("clear")

    print(f"{red}{bold}### NinBuddy by Josh Lotriet{reset}")
    print(f"{green}{bold}### STARTED{reset}\n")
    print(f"{bold}> {state}{reset}\n")

    # instructions for user to connect to switch
    print("Go to 'Change Grip/Order' on your Switch to connect.")
    print("Next, plug in any controller to your Raspberry Pi.\n")

    # if ip is valid, output connection details for user
    if ip.decode().strip().startswith("192.168."):
        print("To use a mobile device as a controller...")
        print(f"Go to: {bold}http://{ip.decode().strip()}:{config.port}{reset} on your phone.\n")
    
    # how to exit software
    print("Press CTRL+C to exit.\n")

# update packet with new joystick values
def update_packet(location, value):
    global packet

    # if only one location, update packet with value
    # otherwise, access nested dict and update with value
    if len(location) == 1:
        packet[location[0]] = value
    else:
        packet[location[0]][location[1]] = value


def add_to_queue(location, value):
    global packet_queue

    # none value acts as a buffer to prevent fast inputs that get ignored

    if location not in packet_queue:
        packet_queue[location] = [value]
        return
    
    packet_queue[location] += [value]


def set_input():
    for button in packet_queue:
        queue = packet_queue[button]

        if len(queue) == 0:
            continue

        next_input = queue[0]

        if next_input != None:
            packet[button] = next_input

        queue.pop(0)

    nx.set_controller_input(device, packet)

# connect new generated controller to switch
def connect():
    global joystick, state, device, input_devices, is_disconnecting
    
    # if ready to connect, update states & connect via nxbt
    if not is_disconnecting:
        update_state("Connecting to console...")
        device = nx.create_controller(nxbt.PRO_CONTROLLER)
        nx.wait_for_connection(device)
        update_state("Connected to console!")

# attempt to disconnect from switch, if possible
def attempt_disconnect():
    global state, is_mobile_connected, is_physical_connected, device, input_devices, is_disconnecting, packet

    # reset packet to prevent infinite input, if user is still holding buttons
    packet = nx.create_input_packet()

    # if another device is still connected or is already disconnecting, ignore
    if is_mobile_connected or is_physical_connected or is_disconnecting:
        return
    
    # set disconnecting state and wait for connection to be removed
    is_disconnecting = True

    # while device isnt connected yet, wait
    while "Connected" not in state:
        time.sleep(0.1)

    # if connected but missing mobile/physical, disconnect from controller and update vars accordingly
    if device != None and not (is_mobile_connected or is_physical_connected):
        update_state("Disconnecting from console...")
        nx.remove_controller(device)
        device = None
        update_state("Waiting for controller...")
    
    # regardless, update disconnecting state
    is_disconnecting = False
