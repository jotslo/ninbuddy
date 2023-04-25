"""button_map = {
    0: ["A"],
    1: ["B"],
    2: ["X"],
    3: ["Y"],
    4: ["L"],
    5: ["R"],
    6: ["MINUS"],
    7: ["PLUS"],
    8: ["HOME"],
    9: ["L_STICK", "PRESSED"],
    10: ["R_STICK", "PRESSED"],
    11: ["DPAD_UP"],
    12: ["DPAD_DOWN"],
    13: ["DPAD_LEFT"],
    14: ["DPAD_RIGHT"]
}"""

input_map_dict = {
    "Xbox": {
        "Buttons": {
            0: ["A"],
            1: ["B"],
            2: ["X"],
            3: ["Y"],
            4: ["L"],
            5: ["R"],
            6: ["MINUS"],
            7: ["PLUS"],
            8: ["HOME"],
            9: ["L_STICK", "PRESSED"],
            10: ["R_STICK", "PRESSED"],
            11: ["DPAD_UP"],
            12: ["DPAD_DOWN"],
            13: ["DPAD_LEFT"],
            14: ["DPAD_RIGHT"]
        },
        "D-pad": {
            0: {
                -1: ["DPAD_LEFT"],
                1: ["DPAD_RIGHT"]
            },
            1: {
                -1: ["DPAD_DOWN"],
                1: ["DPAD_UP"]
            }
        },
        "Axes": {
            0: ["L_STICK", "X_VALUE", 100],
            1: ["L_STICK", "Y_VALUE", -100],
            2: ["ZL"],
            3: ["R_STICK", "X_VALUE", 100],
            4: ["R_STICK", "Y_VALUE", -100],
            5: ["ZR"]
        }
    }
}

from modules import controller

# get button map for a given controller
def get_map(name):
    for key in input_map_dict:
        if key in name:
            return input_map_dict[key]
    
    # if no match, default to Xbox input map
    return input_map_dict["Xbox"]


def button_down(button):
    button_map = get_map(controller.name)["Buttons"]

    controller.update_packet(button_map[button], True)

    print("DOWN", button_map[button], True)


def button_up(button):
    button_map = get_map(controller.name)["Buttons"]
    
    controller.update_packet(button_map[button], False)

    print("UP", button_map[button], False)


def dpad_move(value):
    dpad_map = get_map(controller.name)["D-pad"]

    controller.update_packet(["DPAD_RIGHT"], False)
    controller.update_packet(["DPAD_LEFT"], False)
    controller.update_packet(["DPAD_UP"], False)
    controller.update_packet(["DPAD_DOWN"], False)
    
    for axis in dpad_map:
        if value[0] in dpad_map[axis]:
            controller.update_packet(dpad_map[axis][value[0]], True)
            print("DOWN", dpad_map[axis][value[0]])
        if value[1] in dpad_map[axis]:
            controller.update_packet(dpad_map[axis][value[1]], True)
            print("DOWN", dpad_map[axis][value[1]])

def z_button_move(axis, value):
    axis_map = get_map(controller.name)["Axes"]

    if "Z" in axis_map[axis]:
        controller.update_packet(axis_map[axis], value >= 0.75)

    print("AXIS", axis_map[axis], value)

def axis_move(joystick):
    axis_map = get_map(controller.name)["Axes"]

    for axis in axis_map:
        if "Z" not in axis_map[axis]:
            controller.update_packet(axis_map[axis][:2],
                joystick.get_axis(axis) * axis_map[axis][2])