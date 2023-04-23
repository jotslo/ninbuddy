import os
import urllib.request
import zipfile
import io
import sys
import subprocess

download_url = "https://github.com/jotslo/ninbuddy/releases/download/v0.1-alpha/ninbuddy.zip"
extract_dir = f"/home/{os.environ.get('SUDO_USER')}/ninbuddy"

red = "\033[31m"
bold = "\033[1m"
green = "\033[32m"
reset = "\033[0m"

def start():
    os.system("clear")
    print(f"{red}{bold}### NinBuddy by Josh Lotriet{reset}")

    if os.geteuid() != 0:
        print(f"{red}{bold}ERROR: You must run this script as root.{reset}")
        print(f"To fix, type 'sudo {sys.executable} install.py'")
        sys.exit(1)

def get_source_files():
    print(f"{green}{bold}### PLEASE WAIT...{reset}\n")
    print("Downloading source files...")

    with urllib.request.urlopen(download_url) as url_response:
        with zipfile.ZipFile(io.BytesIO(url_response.read())) as zip_file:
            zip_file.extractall(extract_dir)

    print(f"Source files downloaded to {os.path.abspath(extract_dir)}.")


def install_dependencies():
    print("Preparing to install dependencies...")

    pip_path = sys.executable.replace("python", "pip")
    subprocess.run(["sudo", pip_path, "install", "git+https://github.com/Brikwerk/nxbt.git@dev"])
    subprocess.run([pip_path, "install", "pygame==2.1.2"])


def ask(question, custom_response=None, invalid_response=None):
    os.system("clear")
    print(f"{red}{bold}### NinBuddy by Josh Lotriet{reset}")
    print(f"{green}{bold}### CONFIGURATION{reset}\n")

    # if invalid_response is True, print an error message
    if invalid_response:
        print(f"{red}{bold}Invalid response. Please try again.{reset}\n")

    print(f"{bold}{question}{reset}")

    # if custom_response is True, ask for a custom response
    if custom_response:
        print("Type the number of your choice, between 1000 & 60000")
        response = input("\n> ")

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

        if response.lower().startswith("y"):
            return True
        elif response.lower().startswith("n"):
            return False
        
        # if response is invalid, ask again
        return ask(question, invalid_response=True)



def start_ninbuddy():
    os.system("clear")
    print(f"{red}{bold}### NinBuddy by Josh Lotriet{reset}")
    print(f"{green}{bold}### STARTING...{reset}\n")

    subprocess.run(["sudo", "python3", "server.py"])


def install_complete():
    os.system("clear")
    print(f"{red}{bold}### NinBuddy by Josh Lotriet{reset}")
    print(f"{green}{bold}### INSTALLATION COMPLETE!{reset}\n")

    print("1. Type 'cd {extract_dir}' to go to the NinBuddy directory")
    print("2. Type 'sudo python3 server.py' to start the software")


def set_port(port):
    with open("modules/config.py", "w") as config_file:
        config_file.write(f"port = {port}")


def prepare_auto_start():
    command = f"sudo {extract_dir}/installer/start.sh\n"

    with open(f"{extract_dir}/installer/start.sh", "w") as start_file:
        start_file.write(f"cd {extract_dir}\nsudo python3 server.py")
    
    with open("/etc/rc.local", "r") as rc_file:
        lines = rc_file.readlines()
    
    if command not in lines:
        with open("/etc/rc.local", "a") as rc_file:
            rc_file.write(command)
    
    os.system(f"chmod +x {extract_dir}/installer/start.sh")


def user_configuration():
    os.chdir(extract_dir)

    auto_start = ask("Do you want NinBuddy to automatically start when your Pi turns on?")

    if auto_start:
        prepare_auto_start()

    standard_port = ask("""Do you want to use the default dashboard port? (1010)
    -> If you're not sure, type 'y'.""")

    if not standard_port:
        port = ask("What port would you like NinBuddy to use?", custom_response=True)
        set_port(port)

    if ask("Do you want to start NinBuddy now?"):
        start_ninbuddy()
        return
    
    install_complete()


#####################################

start()
get_source_files()
install_dependencies()
user_configuration()


# auto start on boot?
# custom port? or default to 1010?
# do you want to start the software now?

# curl -L nb.jotslo.com|bash
# curl jotslo.com/nb.sh|bash

#    curl -L -O nb.jotslo.com/get && sudo python3 get