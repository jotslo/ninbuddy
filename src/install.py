import os
import urllib.request
import zipfile
import io
import sys
import subprocess

download_url = "https://github.com/jotslo/ninbuddy/releases/download/v0.1-alpha/ninbuddy.zip"
extract_dir = os.path.expanduser("~/ninbuddy")

os.system("clear")

red = "\033[31m"
bold = "\033[1m"
green = "\033[32m"
reset = "\033[0m"

print(f"{red}{bold}### NinBuddy by Josh Lotriet{reset}")

if os.geteuid() != 0:
    print(f"{red}{bold}ERROR: You must run this script as root.{reset}")
    print(f"To fix, type 'sudo {sys.executable} install.py'")
    sys.exit(1)

home_dir = os.environ["HOME"]
extract_dir = extract_dir.replace("/root/", f"{home_dir}/")

print(f"{green}{bold}### PLEASE WAIT...{reset}\n")
print("Downloading source files...")

with urllib.request.urlopen(download_url) as url_response:
    with zipfile.ZipFile(io.BytesIO(url_response.read())) as zip_file:
        zip_file.extractall(extract_dir)

print(f"Source files downloaded to {os.path.abspath(extract_dir)}.")

print("Preparing to install NXBT and PyGame...")

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

        return response.lower().startswith("y")


auto_start = ask("Do you want NinBuddy to automatically start when your Pi turns on?")
use_custom_port = ask("""Do you want to NinBuddy to use a port other than 1010?
If you're not sure, type 'n'.""")

if use_custom_port:
    port = ask("What port would you like NinBuddy to use?", custom_response=True)

print(auto_start)
print(use_custom_port)
print(port)

# auto start on boot?
# custom port? or default to 1010?
# do you want to start the software now?

# curl -O https://raw.githubusercontent.com/jotslo/ninbuddy/main/src/install.py && sudo python3 install.py
# curl -O https://nb.jotslo.com && sudo python3 install.py
# curl -O https://joshl.io/nb.py && sudo python3 install.py