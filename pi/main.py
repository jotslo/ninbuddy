import bluetooth
#import nxbt, time

"""nx = nxbt.Nxbt()

adapters = nx.get_available_adapters()

print(len(adapters))

controller_index = nx.create_controller(nxbt.PRO_CONTROLLER)

print("Connecting")

nx.wait_for_connection(controller_index)

print("Connected")

time.sleep(3)

nx.press_buttons(controller_index, [nxbt.Buttons.B])"""

print("Scanning for devices...")

nearby_devices = bluetooth.discover_devices(lookup_names=True)

for addr, name in nearby_devices:
    print("  %s - %s" % (addr, name))