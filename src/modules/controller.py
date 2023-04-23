import nxbt, time

# start nxbt and get format for input packet
# input packet is sent to switch each frame
nx = nxbt.Nxbt()
packet = nx.create_input_packet()

# variables containing current controller and its visual state
device = None
state = "Waiting for controller..."

# variables that determine connection state
is_physical_connected = False
is_mobile_connected = False
is_disconnecting = False

# update packet with new joystick values
def update_packet(location, value):
    global packet

    # if only one location, update packet with value
    # otherwise, access nested dict and update with value
    if len(location) == 1:
        packet[location[0]] = value
    else:
        packet[location[0]][location[1]] = value

# connect new generated controller to switch
def connect():
    global joystick, state, device, input_devices, is_disconnecting
    
    # if ready to connect, update states & connect via nxbt
    if not is_disconnecting:
        state = "Connecting to console..."
        device = nx.create_controller(nxbt.PRO_CONTROLLER)
        nx.wait_for_connection(device)
        state = "Connected to console!"

# attempt to disconnect from switch, if possible
def attempt_disconnect():
    global state, is_mobile_connected, is_physical_connected, device, input_devices, is_disconnecting, packet

    # if another device is still connected or is already disconnecting, ignore
    # reset packet to prevent infinite input, if user is still holding buttons
    if is_mobile_connected or is_physical_connected or is_disconnecting:
        packet = nx.create_input_packet()
        return
    
    # set disconnecting state and wait for connection to be removed
    is_disconnecting = True

    # while device isnt connected yet, wait
    while "Connected" not in state:
        time.sleep(0.1)

    # if connected, disconnect from controller and update vars accordingly
    if device != None:
        state = "Disconnecting from console..."
        nx.remove_controller(device)
        device = None

        state = "Waiting for controller..."
        is_disconnecting = False