packet = None
button_map = None

def setup(nx):
    global packet, button_map
    packet = nx.create_input_packet()
    
    button_map = {
        0: packet["A"],
        1: packet["B"],
        2: packet["X"],
        3: packet["Y"],
        4: packet["L"],
        5: packet["R"],
        6: packet["MINUS"],
        7: packet["PLUS"],
        8: packet["HOME"],
        9: packet["L_STICK"]["PRESSED"],
        10: packet["R_STICK"]["PRESSED"]
    }