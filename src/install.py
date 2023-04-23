import os
import urllib.request
import zipfile
import io
import sys
import subprocess

download_url = "https://github.com/jotslo/ninbuddy/releases/download/v0.1-alpha/ninbuddy.zip"
extract_dir = os.path.expanduser("~/ninbuddy")

os.system("cls")

red = "\033[31m"
bold = "\033[1m"
reset = "\033[0m"

print(f"{red}{bold}### NinBuddy by Josh Lotriet{reset}")

if os.geteuid() != 0:
    print(f"{red}{bold}ERROR: You must run this script as root.{reset}")
    print("Use 'sudo python3 install.py' to run this script as root.")
    sys.exit(1)

print("Downloading source files...")

with urllib.request.urlopen(download_url) as url_response:
    with zipfile.ZipFile(io.BytesIO(url_response.read())) as zip_file:
        zip_file.extractall(extract_dir)

print(f"Source files downloaded to {os.path.abspath(extract_dir)}.")

pip_path = sys.executable.replace("python", "pip")
subprocess.run(["sudo", pip_path, "install", "git+https://github.com/Brikwerk/nxbt.git@dev"])
subprocess.run([pip_path, "install", "pygame==2.1.2"])

print("Config...")

# curl -O https://raw.githubusercontent.com/jotslo/ninbuddy/main/src/install.py && sudo python3 install.py
# curl -O https://nb.jotslo.com && sudo python3 install.py