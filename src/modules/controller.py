import nxbt, time

nx = nxbt.Nxbt()

packet = nx.create_input_packet()
device = None
input_devices = []

state = "Waiting for controller..."
is_real_controller = False
is_mobile_connected = False

is_disconnecting = False

def update_packet(location, value):
    global packet

    if len(location) == 1:
        packet[location[0]] = value
    else:
        packet[location[0]][location[1]] = value

def connect(indicator):
    global joystick, is_real_controller, state, device, input_devices, is_disconnecting
    
    input_devices.append(indicator)

    if len(input_devices) == 1 and not is_disconnecting:
        state = "Connecting to console..."
        device = nx.create_controller(nxbt.PRO_CONTROLLER)
        nx.wait_for_connection(device)
        state = "Connected to console!"

def disconnect(indicator):
    global state, is_mobile_connected, device, input_devices, is_disconnecting

    if indicator in input_devices:
        input_devices.remove(indicator)

    if len(input_devices) == 0 and not is_disconnecting:
        is_disconnecting = True

        while "Connected" not in state:
            time.sleep(0.1)
            pass

        if device != None:
            state = "Disconnecting from console..."
            nx.remove_controller(device)
            device = None

        state = "Waiting for controller..."
    
    is_disconnecting = False