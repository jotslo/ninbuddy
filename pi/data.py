packet = None
button_map = None

def setup(nx):
    global packet, button_map
    packet = nx.create_input_packet()
    
    button_map = {
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
        10: ["R_STICK", "PRESSED"]
    }