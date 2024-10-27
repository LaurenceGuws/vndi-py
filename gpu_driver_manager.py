import os
import subprocess
import sys
import logging
from logging.handlers import RotatingFileHandler
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init(autoreset=True)

# Configure logging with rotation (max size 5 MB, keep 3 backups)
log_file = 'gpu_driver_manager.log'
log_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[log_handler]
)
logger = logging.getLogger(__name__)

def run_command(command):
    """Runs a shell command and returns its output."""
    logger.debug(f"Executing command: {command}")
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        logger.error(f"Command failed: {result.stderr.strip()}")
    return result.stdout.strip(), result.stderr.strip()

def check_sudo():
    """Ensure the script is run with sudo privileges."""
    if os.geteuid() != 0:
        logger.error("Script requires sudo privileges.")
        print(Fore.RED + "🔒 This script requires sudo privileges. Please run with sudo.")
        sys.exit(1)

def detect_gpu_vendor():
    """Detects the GPU vendor (NVIDIA or AMD)."""
    stdout, _ = run_command("lspci | grep -i 'vga\\|3d'")
    if "NVIDIA" in stdout:
        logger.info("Detected NVIDIA GPU.")
        return "NVIDIA"
    elif "AMD" in stdout or "Radeon" in stdout:
        logger.info("Detected AMD GPU.")
        return "AMD"
    else:
        logger.warning("No supported GPU detected.")
        print(Fore.RED + "❌ No supported GPU detected.")
        return None

def get_active_driver():
    """Displays the active GPU driver and logs any issues."""
    vendor = detect_gpu_vendor()
    if vendor == "NVIDIA":
        stdout, stderr = run_command("nvidia-smi")
        if stdout:
            print(Fore.GREEN + "\n📦 Active NVIDIA Driver:")
            print(Fore.BLUE + stdout)
            logger.info("Displayed active NVIDIA driver.")
        elif stderr and "version mismatch" in stderr.lower():
            logger.error("NVML version mismatch detected.")
            print(Fore.RED + f"⚠️ Failed to initialize NVML: {stderr}")
        else:
            logger.warning("NVIDIA driver not active.")
            print(Fore.YELLOW + "⚠️ NVIDIA driver not currently active.")
    elif vendor == "AMD":
        stdout, _ = run_command("lspci -k | grep -EA3 'VGA|3D' | grep 'amdgpu'")
        if stdout:
            print(Fore.GREEN + "\n📦 Active AMD Driver:")
            print(Fore.BLUE + stdout)
            logger.info("Displayed active AMD driver.")
        else:
            logger.warning("AMD driver not active.")
            print(Fore.YELLOW + "⚠️ AMD driver not currently active.")

def list_available_drivers(vendor, cache):
    """Lists available drivers for the detected vendor and displays them."""
    if vendor in cache and cache[vendor]:
        logger.info(f"Using cached list of {vendor} drivers.")
        return cache[vendor]
    
    package_manager = detect_package_manager()
    logger.info(f"Searching for {vendor} drivers...")
    print(Fore.CYAN + f"\n🔍 Searching for available {vendor} drivers...\n")

    if vendor == "NVIDIA":
        if package_manager == "apt":
            command = "apt-cache search '^nvidia-driver-[0-9]+'"
        elif package_manager == "yum":
            command = "yum list available | grep -i nvidia"
        elif package_manager == "pacman":
            command = "pacman -Ss nvidia"
    elif vendor == "AMD":
        if package_manager == "apt":
            command = "apt-cache search '^amdgpu-*'"
        elif package_manager == "yum":
            command = "yum list available | grep -i amdgpu"
        elif package_manager == "pacman":
            command = "pacman -Ss amdgpu"
    else:
        logger.error(f"Unsupported vendor: {vendor}")
        print(Fore.RED + "❌ Unsupported GPU vendor.")
        return []

    stdout, stderr = run_command(command)
    if stderr:
        logger.error(f"Error searching for drivers: {stderr}")
        print(Fore.RED + f"⚠️ Error: {stderr}")
        return []

    drivers = [line.split()[0] for line in stdout.splitlines()]
    if drivers:
        logger.info(f"Found {len(drivers)} {vendor} drivers.")
        print(Fore.GREEN + f"✅ Found {len(drivers)} {vendor} drivers:\n")
        for i, driver in enumerate(drivers, 1):
            print(Fore.BLUE + f"  [{i}] {driver}")
        cache[vendor] = drivers
        return drivers
    else:
        logger.warning(f"No {vendor} drivers found.")
        print(Fore.YELLOW + f"⚠️ No {vendor} drivers found.")
        return []

def display_driver_menu(drivers, vendor, list_displayed=True):
    """Displays a menu for the user to select a driver."""
    if not list_displayed:
        print(Fore.CYAN + f"\n🚀 Available {vendor} Drivers:\n")
        for i, driver in enumerate(drivers, 1):
            print(Fore.BLUE + f"  [{i}] {driver}")
        print(Fore.CYAN + "\n(Enter the corresponding number to select a driver)")
    
    while True:
        try:
            choice = int(input(Fore.GREEN + "🟢 Select a driver to install: ")) - 1
            if 0 <= choice < len(drivers):
                selected_driver = drivers[choice]
                logger.info(f"User selected driver: {selected_driver}")
                return selected_driver
            else:
                print(Fore.RED + "❌ Invalid choice. Please select a valid number.")
        except ValueError:
            print(Fore.RED + "❌ Please enter a valid number.")

def install_driver(driver):
    """Installs the selected GPU driver."""
    package_manager = detect_package_manager()
    logger.info(f"Installing driver: {driver}")
    print(Fore.CYAN + f"\n⚙️ Installing and activating {driver}...")

    if package_manager == "apt":
        command = f"DEBIAN_FRONTEND=noninteractive apt-get install -y {driver}"
    elif package_manager == "yum":
        command = f"yum install -y {driver}"
    elif package_manager == "pacman":
        command = f"pacman -S --noconfirm {driver}"

    stdout, stderr = run_command(command)
    # Handle the case where driver is already installed
    if stderr and "already the newest version" not in stderr.lower():
        logger.error(f"Error during installation: {stderr}")
        print(Fore.RED + f"⚠️ Error during installation: {stderr}")
    else:
        logger.info(f"{driver} installed successfully.")
        print(Fore.GREEN + f"✅ {driver} installed successfully.\n")
        print(Fore.CYAN + "🔄 A reboot is recommended for changes to take effect.")

def detect_package_manager():
    """Detects the appropriate package manager for the system."""
    if os.path.exists("/usr/bin/apt"):
        return "apt"
    elif os.path.exists("/usr/bin/yum"):
        return "yum"
    elif os.path.exists("/usr/bin/pacman"):
        return "pacman"
    else:
        logger.error("Unsupported package manager.")
        print(Fore.RED + "⚠️ Unsupported package manager.")
        sys.exit(1)

def main_menu():
    """Displays the main menu and handles user input."""
    vendor = detect_gpu_vendor()
    if not vendor:
        sys.exit(1)

    print(Fore.MAGENTA + f"\n===== {vendor} Driver Manager =====\n")
    print(Fore.CYAN + "1. Show Active Driver")
    print("2. List Available Drivers")
    print("3. Install a Driver")
    print("4. Exit\n")

    driver_cache = {}  # Initialize a cache for drivers
    drivers_listed = False  # Flag to track if drivers have been listed

    while True:
        choice = input(Fore.GREEN + "🔧 Select an option [1-4]: ")
        if choice == '1':
            get_active_driver()
        elif choice == '2':
            drivers = list_available_drivers(vendor, driver_cache)
            if drivers:
                drivers_listed = True
        elif choice == '3':
            if drivers_listed and vendor in driver_cache and driver_cache[vendor]:
                # Drivers are already listed and cached
                drivers = driver_cache[vendor]
                selected_driver = display_driver_menu(drivers, vendor, list_displayed=True)
                install_driver(selected_driver)
            else:
                # Drivers not listed yet; list and cache them first
                drivers = list_available_drivers(vendor, driver_cache)
                if drivers:
                    selected_driver = display_driver_menu(drivers, vendor, list_displayed=False)
                    install_driver(selected_driver)
        elif choice == '4':
            print(Fore.GREEN + "👋 Exiting. Goodbye!")
            sys.exit(0)
        else:
            print(Fore.RED + "❌ Invalid option. Please select a number between 1 and 4.")

def main():
    """Main entry point of the script."""
    check_sudo()
    main_menu()

if __name__ == "__main__":
    main()
