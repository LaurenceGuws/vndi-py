# vndi-py

## Overview
`vndi-py` is a Python-based NVIDIA Driver Manager designed to streamline the process of managing NVIDIA drivers on Debian-based systems. It provides a user-friendly interface with color-coded outputs for easy navigation.

---

## Features
- **List available NVIDIA drivers:** Quickly view all NVIDIA drivers available for installation.
- **Show installed NVIDIA driver:** Check the currently installed NVIDIA driver, if any.
- **Install and uninstall drivers:** Install or uninstall NVIDIA drivers through guided prompts.
- **Update NVIDIA drivers:** Keep your drivers up-to-date with a single command.
- **User-friendly interface:** Color-coded outputs with intuitive menus and error handling.
  
---

## Usage
### Prerequisites:
- Ensure the script is run with **sudo** privileges.
- **Python 3.6+** and the `colorama` package are required:
    ```bash
    pip install colorama
    ```

### How to Run:
1. Clone the repository:
    ```bash
    git clone https://github.com/LaurenceGuws/vndi-py.git
    cd vndi-py
    ```

2. Run the script:
    ```bash
    sudo python3 nvidia_driver_manager.py
    ```

---

## Files
- **nvidia_driver_manager.py:** Main script to manage NVIDIA drivers.
- **test.sh:** A collection of NVIDIA-related commands for testing and debugging.

---

## Available Commands (test.sh)
- Check for installed NVIDIA drivers:
    ```bash
    dpkg -l | grep nvidia
    ```
- List available drivers:
    ```bash
    ubuntu-drivers list
    ```
- Install a specific NVIDIA driver (dry-run):
    ```bash
    sudo apt-get install --dry-run nvidia-driver-535
    ```

---

## Developer Information
**Author:** Your Name  
**Version:** 2.0  
**License:** MIT

---

## Notes
- Ensure you have an active internet connection when installing or updating drivers.
- A system reboot is recommended after any driver change.

---

## Help and Support
Run the script and select the **Help** option from the main menu to get detailed usage instructions.

---

## Contributing
Feel free to fork the repository and create pull requests with improvements or bug fixes.

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
