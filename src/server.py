# main file to run on raspberry pi
from modules import web_handler, physical_handler
from os import environ

# if video driver is not set, set it to dummy value
# this allows us to use pygame without a display
if "SDL_VIDEODRIVER" not in environ:
    environ["SDL_VIDEODRIVER"] = "dummy"

# prevent pygame from outputting extraneous info
# this makes the console output cleaner
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# if file is ran directly, start web server and listen for physical controller input
if __name__ == "__main__":
    web_handler.start()
    physical_handler.listen()