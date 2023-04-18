# main file to run on raspberry pi
from modules import web_handler, physical_handler

# if file is ran directly, start web server and listen for physical controller input
if __name__ == "__main__":
    web_handler.start()
    physical_handler.listen()