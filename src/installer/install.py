"""



If you are reading this, you might have installed NinBuddy incorrectly.

To install NinBuddy, please enter the following command into your terminal:
    curl -L -O nb.jotslo.com/get && sudo python3 get

If there are issues with this script, manual installation is possible.
Please see the README.md file for more information.



"""

import os
import urllib.request
import zipfile
import io
import sys
import subprocess

# store download url & extract dir
download_url = "https://github.com/jotslo/ninbuddy/releases/download/v1.0.0/ninbuddy.zip"
extract_dir = f"/home/{os.environ.get('SUDO_USER')}/ninbuddy"

# declare colours for console output
red = "\033[31m"
bold = "\033[1m"
green = "\033[32m"
reset = "\033[0m"

# if file is ran directly, start installation
def start():
    os.system("clear")
    print(f"{red}{bold}### NinBuddy by Josh Lotriet{reset}")

    # if user is not root, exit with error
    if os.geteuid() != 0:
        print(f"{red}{bold}ERROR: You must run this script as root.{reset}")
        print(f"To fix, type 'sudo {sys.executable} install.py'")
        sys.exit(1)

# get source files from github
def get_source_files():
    print(f"{green}{bold}### PLEASE WAIT...{reset}\n")
    print("Downloading source files...")

    # download source files from github and extra to extract dir
    with urllib.request.urlopen(download_url) as url_response:
        with zipfile.ZipFile(io.BytesIO(url_response.read())) as zip_file:
            zip_file.extractall(extract_dir)

    print(f"Source files downloaded to {os.path.abspath(extract_dir)}.")

# install dependencies from pip (nxbt & pygame)
def install_dependencies():
    print("Preparing to install dependencies...")

    # get pip path, install nxbt dev branch & pygame
    # dev branch used to fix issues in current branch (25 Apr 2023)
    pip_path = sys.executable.replace("python", "pip")
    subprocess.run(["sudo", pip_path, "install", "git+https://github.com/Brikwerk/nxbt.git@086293d33d8a64fdbd2b58fa15197c5b66e0ff7b"])
    subprocess.run([pip_path, "install", "pygame==2.1.2"])

# ask user specified questions
def ask(question, custom_response=None, invalid_response=None):
    os.system("clear")
    print(f"{red}{bold}### NinBuddy by Josh Lotriet{reset}")
    print(f"{green}{bold}### CONFIGURATION{reset}\n")

    # if invalid_response is True, print an error message
    if invalid_response:
        print(f"{red}{bold}Invalid response. Please try again.{reset}\n")

    # output question
    print(f"{bold}{question}{reset}\n")

    # if custom_response is True, ask for a custom response
    if custom_response:
        print("Type the number of your choice, between 1000 & 60000")
        response = input("\n> ")

        # if response is valid, return it
        if response.isdigit():
            int_response = int(response)
            if 1000 <= int_response <= 60000:
                return int_response
                
        # if response is invalid, ask again
        return ask(question, custom_response=True, invalid_response=True)
    
    # if custom_response is False, ask for a yes or no response
    else:
        print("Type 'y' for yes, or 'n' for no.")
        response = input("\n> ")

        # return true or false depending on response
        if response.lower().startswith("y"):
            return True
        elif response.lower().startswith("n"):
            return False
        
        # if response is invalid, ask again
        return ask(question, invalid_response=True)

# after installation, start NinBuddy
def start_ninbuddy():
    os.system("clear")
    print(f"{red}{bold}### NinBuddy by Josh Lotriet{reset}")
    print(f"{green}{bold}### STARTING...{reset}\n")

    subprocess.run(["sudo", "python3", "server.py"])

# after installation, if user opted to not start NinBuddy
# outputs a message to tell user how to start software
def install_complete():
    os.system("clear")
    print(f"{red}{bold}### NinBuddy by Josh Lotriet{reset}")
    print(f"{green}{bold}### INSTALLATION COMPLETE!{reset}\n")

    print(f"1. Type 'cd {extract_dir}' to go to the NinBuddy directory")
    print("2. Type 'sudo python3 server.py' to start the software")

# updates config file with specified port
def set_port(port):
    with open("modules/config.py", "w") as config_file:
        config_file.write(f"port = {port}")

# if user opted for NinBuddy to start on boot
# add command to rc.local, which is executed on boot
def prepare_auto_start():
    command = f"cd {extract_dir} && sudo python3 server.py\n"
    
    # get lines from rc.local
    with open("/etc/rc.local", "r") as rc_file:
        lines = rc_file.readlines()
    
    # if command is not in lines, add it
    if command not in lines:
        lines[-1] = command
        lines.append("exit 0\n")

        # write lines to rc.local
        with open("/etc/rc.local", "w") as rc_file:
            rc_file.writelines(lines)

# ask user the configuration questions
def user_configuration():
    # change directory to extract dir
    os.chdir(extract_dir)

    # ask user if they want software to start on boot
    auto_start = ask(f"""Do you want NinBuddy to automatically start when your Pi turns on?
{reset}-> Plug in a controller & it will auto-connect to your console any time!""")
                     
    # if user opted for auto start, set that up
    if auto_start:
        prepare_auto_start()
    
    # ask user if they want to use the default port
    standard_port = ask(f"""Do you want to use the default dashboard port? (1010)
{reset}-> Just type 'y' if you're not sure.""")
                        
    # if user opted for custom port, set that up
    if not standard_port:
        port = ask("What port would you like NinBuddy to use?", custom_response=True)
        set_port(port)
    
    # start NinBuddy now if user opts for it
    if ask("Do you want to start NinBuddy now?"):
        start_ninbuddy()
        return
    
    # if NinBuddy isn't starting now, tell user how to start it
    install_complete()

# call necessary functions to install NinBuddy
start()
get_source_files()
install_dependencies()
user_configuration()


"""



If you are reading this, you might have installed NinBuddy incorrectly.

To install NinBuddy, please enter the following command into your terminal:
    curl -L -O nb.jotslo.com/get && sudo python3 get

If there are issues with this script, manual installation is possible.
Please see the README.md file for more information.



"""