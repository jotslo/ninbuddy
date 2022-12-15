import bluetooth
import subprocess
import evdev
#import nxbt, time


devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
controller = None

for device in devices:
    if device.name == "Pro Controller":
        controller = evdev.InputDevice(device.path)
        break


if controller:
    while True:
        event = controller.read_one()
        if event:
            print(event)

"""nx = nxbt.Nxbt()

adapters = nx.get_available_adapters()

print(len(adapters))

controller_index = nx.create_controller(nxbt.PRO_CONTROLLER)

print("Connecting")

nx.wait_for_connection(controller_index)

print("Connected")

time.sleep(3)

nx.press_buttons(controller_index, [nxbt.Buttons.B])"""

"""port = 1
passkey = "0000"

print("Scanning for devices...")
nearby_devices = bluetooth.discover_devices(lookup_names=True)

for addr, name in nearby_devices:
    print("  %s - %s" % (addr, name))

    if "Pro Controller" in name:
        print("Found Pro Controller!")

        subprocess.run(["rfkill", "unblock", "bluetooth"], check=True, shell=True)
        subprocess.run("bluetoothctl", check=True, shell=True)
        subprocess.run(["power", "on"], check=True, shell=True)
        subprocess.run(["pair", addr], check=True, shell=True)
        subprocess.run(["connect", addr], check=True, shell=True)
        print("Connected!")
        break"""