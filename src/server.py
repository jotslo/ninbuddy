# main file to run on raspberry pi
from os import environ, geteuid, system
from sys import executable, exit

# prevent pygame from outputting extraneous info
# this makes the console output cleaner
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# declare colours for console output
red = "\033[31m"
bold = "\033[1m"
green = "\033[32m"
reset = "\033[0m"

# if video driver is not set, set it to dummy value
# this allows us to use pygame without a display
if "SDL_VIDEODRIVER" not in environ:
    environ["SDL_VIDEODRIVER"] = "dummy"

# if file is ran directly, start web server and listen for physical controller input
if __name__ == "__main__":
    # if user is not root, exit with error
    if geteuid() != 0:
        print(f"{red}{bold}### NinBuddy by Josh Lotriet{reset}")
        print(f"{red}{bold}ERROR: You must run this script as root.{reset}")
        print(f"To fix, type 'sudo {executable} install.py'")
        exit(1)
    
    # import modules that handle web and physical controller input
    from modules import web_handler, physical_handler

    # start web server and listen for physical controller input
    try:
        web_handler.start()
        physical_handler.listen()
    
    # if user presses CTRL+C, exit software
    except KeyboardInterrupt:
        system("clear")
        exit(0)