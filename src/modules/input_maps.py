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
            12: ["SCREENSHOT"]
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
    },
    "PS": {
        "Buttons": {
            0: ["A"],
            1: ["B"],
            2: ["X"],
            3: ["Y"],
            4: ["MINUS"],
            5: ["HOME"],
            6: ["PLUS"],
            7: ["L_STICK", "PRESSED"],
            8: ["R_STICK", "PRESSED"],
            9: ["L"],
            10: ["R"],
            11: ["DPAD_UP"],
            12: ["DPAD_DOWN"],
            13: ["DPAD_LEFT"],
            14: ["DPAD_RIGHT"],
            15: ["SCREENSHOT"]
        },
        "D-pad": {},
        "Axes": {}
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

    print("DOWN", button)


def button_up(button):
    button_map = get_map(controller.name)["Buttons"]
    
    controller.update_packet(button_map[button], False)

    print("UP", button)


def dpad_move(value):
    dpad_map = get_map(controller.name)["D-pad"]

    if len(dpad_map) == 0:
        return

    controller.update_packet(["DPAD_RIGHT"], False)
    controller.update_packet(["DPAD_LEFT"], False)
    controller.update_packet(["DPAD_UP"], False)
    controller.update_packet(["DPAD_DOWN"], False)

    if value[0] in dpad_map[0]:
        controller.update_packet(dpad_map[0][value[0]], True)
    
    if value[1] in dpad_map[1]:
        controller.update_packet(dpad_map[1][value[1]], True)

def z_button_move(axis, value):
    axis_map = get_map(controller.name)["Axes"]

    if len(axis_map) == 0:
        return

    if "Z" in axis_map[axis][0]:
        controller.update_packet(axis_map[axis], value >= 0.75)

"""controller.update_packet(["L_STICK", "X_VALUE"], joystick.get_axis(0) * 100)
        controller.update_packet(["L_STICK", "Y_VALUE"], joystick.get_axis(1) * -100)
        controller.update_packet(["R_STICK", "X_VALUE"], joystick.get_axis(3) * 100)
        controller.update_packet(["R_STICK", "Y_VALUE"], joystick.get_axis(4) * -100)"""

def axis_move(joystick):
    axis_map = get_map(controller.name)["Axes"]

    if len(axis_map) == 0:
        return

    for axis in axis_map:
        if "Z" not in axis_map[axis][0]:
            controller.update_packet(axis_map[axis][:2],
                joystick.get_axis(axis) * axis_map[axis][2])