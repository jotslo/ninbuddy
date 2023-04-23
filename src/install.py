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
yellow = "\033[33m"
reset = "\033[0m"

print(f"{red}{bold}### NinBuddy by Josh Lotriet{reset}")

if os.geteuid() != 0:
    print(f"{red}{bold}ERROR: You must run this script as root.{reset}")
    print("Use 'sudo python3 install.py' to run this script as root.")
    sys.exit(1)

home_dir = os.environ["HOME"]
extract_dir = extract_dir.replace("/root/", f"{home_dir}/")

print("Downloading source files...")

with urllib.request.urlopen(download_url) as url_response:
    with zipfile.ZipFile(io.BytesIO(url_response.read())) as zip_file:
        zip_file.extractall(extract_dir)

print(f"Source files downloaded to {os.path.abspath(extract_dir)}.")

print("Preparing to install NXBT and PyGame...")

pip_path = sys.executable.replace("python", "pip")
subprocess.run(["sudo", pip_path, "install", "git+https://github.com/Brikwerk/nxbt.git@dev"])
subprocess.run([pip_path, "install", "pygame==2.1.2"])

os.system("clear")

print(f"{red}{bold}### NinBuddy by Josh Lotriet{reset}")
print(f"{yellow}{bold}### CONFIGURATION{reset}\n")

print(f"{bold}Do you want NinBuddy to automatically start when your Pi turns on?{reset}")
print("Type 'y' for yes, or 'n' for no.")

response = input("\n> ")

if response.lower().startswith("y"):
    print("ok!")
else:
    print("oh!")


# curl -O https://raw.githubusercontent.com/jotslo/ninbuddy/main/src/install.py && sudo python3 install.py
# curl -O https://nb.jotslo.com && sudo python3 install.py