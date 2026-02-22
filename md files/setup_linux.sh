#!/bin/bash

# Adaptive ECMP - Kali Linux Automatic Setup Script
# This script automates all installation steps

set -e  # Exit on error

echo "======================================"
echo "Adaptive ECMP - Linux Setup Script"
echo "======================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use: sudo bash setup_linux.sh)"
   exit 1
fi

print_status "Starting Adaptive ECMP setup for Linux..."
echo ""

# Step 1: Update system
print_status "Step 1: Updating system packages..."
apt-get update > /dev/null 2>&1
apt-get upgrade -y > /dev/null 2>&1
print_status "System updated"
echo ""

# Step 2: Install dependencies
print_status "Step 2: Installing dependencies..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    mininet \
    openvswitch-switch \
    openvswitch-testcontroller \
    build-essential \
    net-tools \
    curl > /dev/null 2>&1

print_status "Dependencies installed"
echo ""

# Step 3: Start and enable OpenVSwitch
print_status "Step 3: Configuring OpenVSwitch..."
systemctl start openvswitch-switch
systemctl enable openvswitch-switch
print_status "OpenVSwitch configured"
echo ""

# Step 4: Install Python packages
print_status "Step 4: Installing Python packages..."
pip3 install --upgrade pip > /dev/null 2>&1

# Try pip install first
if pip3 install ryu networkx > /dev/null 2>&1; then
    print_status "Python packages installed via pip"
else
    print_warning "pip3 install ryu failed, installing from GitHub source..."
    
    # Install from GitHub if pip fails
    cd ~
    if [ ! -d "ryu" ]; then
        git clone https://github.com/osrg/ryu.git > /dev/null 2>&1
    fi
    
    cd ~/ryu
    pip3 install -e . > /dev/null 2>&1
    cd - > /dev/null
    
    # Install networkx separately
    pip3 install networkx > /dev/null 2>&1
    print_status "Ryu installed from GitHub source"
fi
echo ""

# Step 5: Verify installations
print_status "Step 5: Verifying installations..."
echo ""

# Check Mininet
echo -n "  Mininet: "
if sudo mn --version &>/dev/null; then
    print_status "Mininet installed"
else
    print_warning "Mininet check (continue anyway)"
fi

# Check Ryu
echo -n "  Ryu: "
if ryu --version &>/dev/null; then
    print_status "Ryu installed"
else
    print_error "Ryu installation failed"
fi

# Check Python packages
echo -n "  Python packages: "
if python3 -c "import ryu, networkx" 2>/dev/null; then
    print_status "All Python packages loaded"
else
    print_error "Python package import failed"
fi

echo ""
print_status "Setup complete!"
echo ""
echo "======================================"
echo "Next Steps:"
echo "======================================"
echo ""
echo "1. Navigate to your project:"
echo "   cd ~/adaptive_ecmp"
echo ""
echo "2. Terminal 1 - Start topology:"
echo "   sudo python3 simple_topo.py"
echo ""
echo "3. Terminal 2 - Start controller:"
echo "   ryu-manager adaptive_ecmp.py"
echo ""
echo "4. Terminal 1 (mininet prompt) - Run tests:"
echo "   mininet> pingall"
echo "   mininet> h1 iperf -c 10.0.0.4 -t 5"
echo ""
echo "======================================"
