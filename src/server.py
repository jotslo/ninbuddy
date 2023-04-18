
import nxbt
import time
import os
import numpy
import random

from threading import Thread

from modules import (data,
                     controller,
                     web_handler,
                     physical_handler)

# start web server for mobile controller input
web_handler.start()

# listen for physical controller input
physical_handler.listen()