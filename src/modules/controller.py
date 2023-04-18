import nxbt

nx = nxbt.Nxbt()

packet = None
controller = None

state = "Waiting for controller..."
is_real_controller = False
is_mobile_connected = False

def update_packet(location, value):
    global packet
    
    if len(location) == 1:
        packet[location[0]] = value
    else:
        packet[location[0]][location[1]] = value

def update_joystick(joystick):
    update_packet(["L_STICK", "X_VALUE"], joystick.get_axis(0) * 100)
    update_packet(["L_STICK", "Y_VALUE"], joystick.get_axis(1) * -100)
    update_packet(["R_STICK", "X_VALUE"], joystick.get_axis(3) * 100)
    update_packet(["R_STICK", "Y_VALUE"], joystick.get_axis(4) * -100)

def connect(is_real):
    global joystick, is_real_controller, state

    state = "Connecting to console..."
    is_real_controller = is_real

    controller = nx.create_controller(nxbt.PRO_CONTROLLER)
    nx.wait_for_connection(controller)
    state = "Connected to console!"

def disconnect():
    global state

    if not is_mobile_connected:
        return

    print("User has disconnected!")

    if controller != None:
        state = "Removing controller..."

        try:
            nx.remove_controller(controller)
        except KeyError:
            print("Controller removed during connection.")

        controller = None
    
    is_mobile_connected = False
    state = "Waiting for controller..."

