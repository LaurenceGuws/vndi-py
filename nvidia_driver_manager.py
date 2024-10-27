import os
import subprocess
import sys
import logging
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(
    filename='nvidia_driver_manager.log',
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

def list_available_nvidia_drivers():
    """Lists available NVIDIA drivers using apt."""
    print(Fore.CYAN + "\n🔍 Searching for available NVIDIA drivers...\n")
    stdout, stderr = run_command("apt-cache search '^nvidia-driver-[0-9]+'")
    if stderr:
        print(Fore.RED + f"⚠️ Error: {stderr}")
        return []
    drivers = [line.split()[0] for line in stdout.splitlines()]
    if drivers:
        print(Fore.GREEN + "✅ Available NVIDIA Drivers Found:\n")
        for driver in drivers:
            print(Fore.BLUE + f"  - {driver}")
    else:
        print(Fore.YELLOW + "⚠️ No NVIDIA drivers found.")
    return drivers

def get_installed_nvidia_driver():
    """Checks if an NVIDIA driver is currently installed."""
    stdout, _ = run_command("dpkg -l | grep '^ii  nvidia-driver-'")
    if stdout:
        driver = stdout.split()[1]
        print(Fore.GREEN + f"\n📦 Currently installed NVIDIA driver: {driver}\n")
        return driver
    else:
        print(Fore.YELLOW + "\n📦 No NVIDIA driver is currently installed.\n")
        return None

def display_driver_menu(drivers):
    """Displays a menu for driver selection."""
    print(Fore.CYAN + "\n🚀 Available NVIDIA Drivers:\n")
    for i, driver in enumerate(drivers, 1):
        print(Fore.BLUE + f"  [{i}] {driver}")
    
    print(Fore.CYAN + "\n(Enter the corresponding number to select a driver)")
    while True:
        choice = input(Fore.GREEN + "🟢 Select a driver to activate: ")
        try:
            index = int(choice) - 1
            if 0 <= index < len(drivers):
                return drivers[index]
            else:
                print(Fore.RED + "❌ Invalid choice. Please select a valid number.")
        except ValueError:
            print(Fore.RED + "❌ Please enter a valid number.")

def confirm_action(message):
    """Ask the user to confirm before proceeding."""
    while True:
        response = input(Fore.YELLOW + f"{message} [y/n]: ").strip().lower()
        if response in ["y", "n"]:
            return response == "y"
        print(Fore.RED + "❌ Please enter 'y' or 'n'.")

def install_driver(driver):
    """Installs the selected NVIDIA driver."""
    print(Fore.CYAN + f"\n⚙️ Installing and activating {driver}...")
    command = f"DEBIAN_FRONTEND=noninteractive apt-get install -y {driver} 2>&1 | grep -v 'WARNING:'"
    stdout, stderr = run_command(command)
    if stderr:
        print(Fore.RED + f"⚠️ Error during installation: {stderr}")
    else:
        print(Fore.GREEN + stdout)
        print(Fore.GREEN + f"✅ {driver} installed successfully.\n")
        print(Fore.CYAN + "🔄 A reboot is recommended for changes to take effect.")

def uninstall_driver(driver):
    """Uninstalls the specified NVIDIA driver."""
    print(Fore.CYAN + f"\n⚙️ Uninstalling {driver}...")
    command = f"apt-get purge -y {driver}"
    stdout, stderr = run_command(command)
    if stderr:
        print(Fore.RED + f"⚠️ Error during uninstallation: {stderr}")
    else:
        print(Fore.GREEN + stdout)
        print(Fore.GREEN + f"✅ {driver} uninstalled successfully.\n")
        print(Fore.CYAN + "🔄 A reboot is recommended to complete uninstallation.")

def update_drivers():
    """Updates the package lists and upgrades NVIDIA drivers."""
    print(Fore.CYAN + "\n🔄 Updating package lists...")
    stdout, stderr = run_command("apt-get update")
    if stderr:
        print(Fore.RED + f"⚠️ Error during update: {stderr}")
        return
    print(Fore.GREEN + stdout)
    
    print(Fore.CYAN + "\n⚙️ Upgrading NVIDIA drivers...")
    stdout, stderr = run_command("apt-get upgrade -y nvidia-driver-*")
    if stderr:
        print(Fore.RED + f"⚠️ Error during upgrade: {stderr}")
    else:
        print(Fore.GREEN + stdout)
        print(Fore.GREEN + "✅ NVIDIA drivers upgraded successfully.\n")
        print(Fore.CYAN + "🔄 A reboot is recommended for changes to take effect.")

def show_help():
    """Displays help information."""
    help_text = f"""
{Fore.CYAN}NVIDIA Driver Manager Help
{Fore.RESET}This script allows you to manage NVIDIA drivers on your system.

{Fore.YELLOW}Options:
  1. List Available NVIDIA Drivers   - Display all NVIDIA drivers available for installation.
  2. Show Installed NVIDIA Driver    - Show the currently installed NVIDIA driver, if any.
  3. Install a NVIDIA Driver         - Choose and install a specific NVIDIA driver.
  4. Uninstall NVIDIA Driver         - Remove the currently installed NVIDIA driver.
  5. Update NVIDIA Drivers           - Update the package lists and upgrade NVIDIA drivers.
  6. Exit                            - Exit the script.

{Fore.YELLOW}Usage:
  - Select an option by entering the corresponding number.
  - Follow on-screen prompts for each action.

{Fore.YELLOW}Notes:
  - Ensure you have an active internet connection.
  - It's recommended to reboot your system after installing or uninstalling drivers.
"""
    print(help_text)

def show_about():
    """Displays about information."""
    about_text = f"""
{Fore.CYAN}NVIDIA Driver Manager
{Fore.RESET}Version: 2.0
Author: Your Name
Description: A Python script to manage NVIDIA drivers on Debian-based systems.

{Fore.YELLOW}Features:
  - List available NVIDIA drivers
  - Show installed NVIDIA driver
  - Install and uninstall NVIDIA drivers
  - Update NVIDIA drivers
  - User-friendly interface with color-coded outputs

{Fore.YELLOW}Note:
  - Run this script with sudo privileges.
  - Ensure your system is backed up before making changes to drivers.
"""
    print(about_text)

def main_menu():
    """Displays the main menu and handles user input."""
    while True:
        print(Fore.MAGENTA + "\n===== NVIDIA Driver Manager =====\n")
        print(Fore.CYAN + "1. List Available NVIDIA Drivers")
        print("2. Show Installed NVIDIA Driver")
        print("3. Install a NVIDIA Driver")
        print("4. Uninstall NVIDIA Driver")
        print("5. Update NVIDIA Drivers")
        print("6. Help")
        print("7. About")
        print("8. Exit\n")
        
        choice = input(Fore.GREEN + "🔧 Select an option [1-8]: ")
        if choice == '1':
            list_available_nvidia_drivers()
        elif choice == '2':
            get_installed_nvidia_driver()
        elif choice == '3':
            drivers = list_available_nvidia_drivers()
            if drivers:
                selected_driver = display_driver_menu(drivers)
                if selected_driver:
                    print(Fore.CYAN + f"\nYou selected: {selected_driver}")
                    if confirm_action("Do you want to proceed with the installation?"):
                        install_driver(selected_driver)
        elif choice == '4':
            installed_driver = get_installed_nvidia_driver()
            if installed_driver:
                if confirm_action(f"Are you sure you want to uninstall {installed_driver}?"):
                    uninstall_driver(installed_driver)
        elif choice == '5':
            update_drivers()
        elif choice == '6':
            show_help()
        elif choice == '7':
            show_about()
        elif choice == '8':
            print(Fore.GREEN + "👋 Exiting NVIDIA Driver Manager. Goodbye!")
            sys.exit(0)
        else:
            print(Fore.RED + "❌ Invalid option. Please select a number between 1 and 8.")

def main():
    """Main entry point of the script."""
    check_sudo()
    main_menu()

if __name__ == "__main__":
    main()
