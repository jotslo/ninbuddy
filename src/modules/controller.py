import nxbt, time

nx = nxbt.Nxbt()

packet = nx.create_input_packet()
device = None
input_devices = []

state = "Waiting for controller..."
is_physical_connected = False
is_mobile_connected = False

is_disconnecting = False

def update_packet(location, value):
    global packet

    if len(location) == 1:
        packet[location[0]] = value
    else:
        packet[location[0]][location[1]] = value

def connect():
    global joystick, state, device, input_devices, is_disconnecting
    
    if not is_disconnecting:
        state = "Connecting to console..."
        device = nx.create_controller(nxbt.PRO_CONTROLLER)
        nx.wait_for_connection(device)
        state = "Connected to console!"

def attempt_disconnect():
    global state, is_mobile_connected, is_physical_connected, device, input_devices, is_disconnecting

    if is_mobile_connected or is_physical_connected or is_disconnecting:
        return
    
    is_disconnecting = True

    while "Connected" not in state:
        time.sleep(0.1)

    if device != None:
        state = "Disconnecting from console..."
        nx.remove_controller(device)
        device = None

        state = "Waiting for controller..."
        is_disconnecting = False