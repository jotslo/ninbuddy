# main file to run on raspberry pi
from os import environ

# prevent pygame from outputting extraneous info
# this makes the console output cleaner
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# if video driver is not set, set it to dummy value
# this allows us to use pygame without a display
if "SDL_VIDEODRIVER" not in environ:
    environ["SDL_VIDEODRIVER"] = "dummy"

# import modules that handle web and physical controller input
from modules import web_handler, physical_handler

# if file is ran directly, start web server and listen for physical controller input
if __name__ == "__main__":
    web_handler.start()
    physical_handler.listen()