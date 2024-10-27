# Check for installed NVIDIA drivers
time dpkg -l | grep nvidia

# List available NVIDIA drivers using 'ubuntu-drivers'
time ubuntu-drivers list

# Show recommended drivers for detected devices
time ubuntu-drivers devices

# Install a specific NVIDIA driver (dry run, no changes made)
time sudo apt-get install --dry-run nvidia-driver-535

# Display system hardware with PCI devices filtered for NVIDIA
time lspci | grep -i nvidia

# Display kernel modules related to NVIDIA
time lsmod | grep nvidia

# Check NVIDIA driver version (if installed)
time nvidia-smi

# Display system information for all devices
time lshw -c display

# List all loaded kernel modules
time lsmod

# Check available repositories and search for NVIDIA drivers
time apt-cache search nvidia

# Get information about the currently running Linux kernel
time uname -r

# Show running processes that may use the GPU
time ps aux | grep nvidia

# Display available GPU resources
time nvidia-smi --query-gpu=utilization.gpu --format=csv

# Debug command for 'ubuntu-drivers'
time ubuntu-drivers debug
