import os
import subprocess
import sys
import logging
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(
    filename='gpu_driver_manager.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_command(command):
    """Runs a shell command and returns its output."""
    logging.debug(f"Executing command: {command}")
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.stderr:
        logging.error(f"Error: {result.stderr.strip()}")
    return result.stdout.strip(), result.stderr.strip()

def check_sudo():
    """Ensure the script is run with sudo privileges."""
    if os.geteuid() != 0:
        print(Fore.RED + "🔒 This script requires sudo privileges. Please run with sudo.")
        sys.exit(1)

def detect_gpu_vendor():
    """Detects the GPU vendor (NVIDIA or AMD)."""
    stdout, _ = run_command("lspci | grep -i 'vga\|3d'")
    if "NVIDIA" in stdout:
        return "NVIDIA"
    elif "AMD" in stdout:
        return "AMD"
    else:
        return None

def detect_package_manager():
    """Detects the appropriate package manager for the system."""
    if os.path.exists("/usr/bin/apt"):
        return "apt"
    elif os.path.exists("/usr/bin/yum"):
        return "yum"
    elif os.path.exists("/usr/bin/pacman"):
        return "pacman"
    else:
        print(Fore.RED + "⚠️ Unsupported package manager.")
        sys.exit(1)

def list_available_drivers(vendor):
    """Lists available drivers based on the vendor."""
    package_manager = detect_package_manager()
    print(Fore.CYAN + f"\n🔍 Searching for available {vendor} drivers...\n")

    if package_manager == "apt":
        if vendor == "NVIDIA":
            command = "apt-cache search '^nvidia-driver-[0-9]+'"
        else:  # AMD
            command = "apt-cache search '^amdgpu-*'"
    elif package_manager == "yum":
        command = f"yum list available | grep -i {vendor}"
    elif package_manager == "pacman":
        command = f"pacman -Ss {vendor.lower()}"

    stdout, stderr = run_command(command)
    if stderr:
        print(Fore.RED + f"⚠️ Error: {stderr}")
        return []

    drivers = [line.split()[0] for line in stdout.splitlines()]
    if drivers:
        print(Fore.GREEN + f"✅ Available {vendor} Drivers Found:\n")
        for driver in drivers:
            print(Fore.BLUE + f"  - {driver}")
    else:
        print(Fore.YELLOW + f"⚠️ No {vendor} drivers found.")
    return drivers

def install_driver(driver):
    """Installs the selected GPU driver."""
    package_manager = detect_package_manager()
    print(Fore.CYAN + f"\n⚙️ Installing and activating {driver}...")

    if package_manager == "apt":
        command = f"DEBIAN_FRONTEND=noninteractive apt-get install -y {driver} 2>&1 | grep -v 'WARNING:'"
    elif package_manager == "yum":
        command = f"yum install -y {driver}"
    elif package_manager == "pacman":
        command = f"pacman -S --noconfirm {driver}"

    stdout, stderr = run_command(command)
    if stderr:
        print(Fore.RED + f"⚠️ Error during installation: {stderr}")
    else:
        print(Fore.GREEN + stdout)
        print(Fore.GREEN + f"✅ {driver} installed successfully.\n")
        print(Fore.CYAN + "🔄 A reboot is recommended for changes to take effect.")

def uninstall_driver(driver):
    """Uninstalls the specified GPU driver."""
    package_manager = detect_package_manager()
    print(Fore.CYAN + f"\n⚙️ Uninstalling {driver}...")

    if package_manager == "apt":
        command = f"apt-get purge -y {driver}"
    elif package_manager == "yum":
        command = f"yum remove -y {driver}"
    elif package_manager == "pacman":
        command = f"pacman -R --noconfirm {driver}"

    stdout, stderr = run_command(command)
    if stderr:
        print(Fore.RED + f"⚠️ Error during uninstallation: {stderr}")
    else:
        print(Fore.GREEN + stdout)
        print(Fore.GREEN + f"✅ {driver} uninstalled successfully.\n")
        print(Fore.CYAN + "🔄 A reboot is recommended to complete uninstallation.")

def main_menu():
    """Displays the main menu and handles user input."""
    vendor = detect_gpu_vendor()
    if not vendor:
        print(Fore.RED + "❌ No supported GPU detected.")
        sys.exit(1)

    print(Fore.MAGENTA + f"\n===== {vendor} Driver Manager =====\n")
    print(Fore.CYAN + "1. List Available Drivers")
    print("2. Install a Driver")
    print("3. Uninstall a Driver")
    print("4. Exit\n")

    while True:
        choice = input(Fore.GREEN + "🔧 Select an option [1-4]: ")
        if choice == '1':
            list_available_drivers(vendor)
        elif choice == '2':
            drivers = list_available_drivers(vendor)
            if drivers:
                driver = drivers[0]  # Automatically select the first driver for simplicity
                install_driver(driver)
        elif choice == '3':
            installed_driver = list_available_drivers(vendor)
            if installed_driver:
                uninstall_driver(installed_driver[0])
        elif choice == '4':
            print(Fore.GREEN + "👋 Exiting. Goodbye!")
            sys.exit(0)
        else:
            print(Fore.RED + "❌ Invalid option. Please select a valid number.")

def main():
    """Main entry point of the script."""
    check_sudo()
    main_menu()

if __name__ == "__main__":
    main()
