# Adaptive ECMP - Linux/Kali Linux Setup & Execution Guide

## Prerequisites
- Kali Linux VM (preferably 4GB+ RAM, 20GB+ disk)
- Internet connection
- Terminal access
- Sudo privileges

---

## Part 1: Clone Repository from Windows Machine

### Option 1: Clone directly to Kali from GitHub (if repo is public)
```bash
cd ~
git clone <your-repo-url>
cd adaptive_ecmp
```

### Option 2: Clone on Windows, Transfer via USB/SCP
```bash
# On Windows PowerShell
scp -r "d:\Melinia\adaptive_ecmp" kali_user@<your-linux-ip>:/home/kali_user/
```

### Option 3: Download ZIP and Transfer
1. **Windows**: Compress folder: `Right-click adaptive_ecmp → Compress`
2. **Transfer via USB drive** or SCP
3. **Linux**: Extract:
```bash
unzip adaptive_ecmp.zip
cd adaptive_ecmp
```

---

## Part 2: Full Environment Setup for Kali Linux

### Step 1: Update System (CRITICAL)
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 2: Install Core Dependencies
```bash
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    mininet \
    openvswitch-switch \
    openvswitch-testcontroller \
    build-essential \
    net-tools \
    curl
```

### Step 3: Start OpenVSwitch Service
```bash
# Important: OVS must be running
sudo systemctl start openvswitch-switch
sudo systemctl enable openvswitch-switch

# Verify it's running
sudo systemctl status openvswitch-switch
```

### Step 4: Install Python Packages
```bash
sudo pip3 install --upgrade pip
sudo pip3 install ryu networkx
```

**⚠️ If pip3 install ryu fails:** Follow [INSTALL_RYU_FROM_GITHUB.md](INSTALL_RYU_FROM_GITHUB.md) to install from source

### Step 5: Verify Installation
```bash
# Check Mininet
sudo mn --version

# Check Ryu
ryu --version

# Check Python packages
python3 -c "import ryu, networkx; print('✓ All packages installed successfully')"
```

---

## Part 3: Prepare Your Repository

### Navigate to Project
```bash
cd ~/adaptive_ecmp  # or wherever you cloned it
```

### Give Execute Permissions
```bash
chmod +x *.py
ls -la
```

### Verify Key Files Exist
```bash
ls -l simple_topo.py adaptive_ecmp.py final_adaptive.py
```

---

## Part 4: Running Adaptive ECMP

### Terminal 1: Start Network Topology
```bash
cd ~/adaptive_ecmp
sudo python3 simple_topo.py
```

**Expected output:**
```
*** Starting network
*** Configuring hosts
*** Starting controller
*** Starting 6 switches
*** Starting 4 hosts
*** Starting CLI
mininet>
```

**DO NOT CLOSE THIS TERMINAL** - Network runs in this window.

---

### Terminal 2: Start Ryu Controller
```bash
# Open NEW terminal/tab
cd ~/adaptive_ecmp
ryu-manager adaptive_ecmp.py
```

**Expected output:**
```
INFO:ryu.base.app_manager:loading app adaptive_ecmp.py
INFO:ryu.base.app_manager:instantiating app adaptive_ecmp.py
[BOOT] Default FLOOD rule installed on switch 1
[BOOT] Default FLOOD rule installed on switch 2
[TOPO] Detected switches: [1, 2, 3, 4]
...
[LINK_CHANGE] Link event detected
```

---

### Terminal 3: Run Tests in Mininet CLI
```bash
# Go back to Terminal 1 and use mininet> prompt

# Test 1: Basic connectivity
mininet> pingall

# Test 2: See network nodes
mininet> nodes

# Test 3: Check switch connections
mininet> links

# Test 4: Simple bandwidth test
mininet> h4 iperf -s &
mininet> h1 iperf -c 10.0.0.4 -t 5

# Test 5: Run traceroute
mininet> h1 traceroute 10.0.0.4

# Test 6: Exit mininet
mininet> exit
```

---

## Part 5: Comparing Different Controllers

### Run Traditional ECMP (One Terminal)
```bash
cd ~/adaptive_ecmp
ryu-manager traditional_ecmp.py
```

### Run Final Adaptive (With Group Modifications)
```bash
cd ~/adaptive_ecmp
ryu-manager final_adaptive.py
```

---

## Part 6: Troubleshooting

### Issue 1: "Permission denied" when starting Mininet
```bash
# Solution: Run with sudo
sudo python3 simple_topo.py
```

### Issue 2: "OVS daemon is not running"
```bash
# Solution: Start OpenVSwitch
sudo systemctl start openvswitch-switch
sudo systemctl status openvswitch-switch
```

### Issue 3: "Mininet not found"
```bash
# Solution: Reinstall mininet
sudo apt-get update
sudo apt-get install -y mininet
```

### Issue 4: "Port already in use"
```bash
# Solution: Kill lingering processes
sudo pkill -f mininet
sudo pkill -f mn
sudo mn -c  # Clean up all switches

# Then retry
sudo python3 simple_topo.py
```

### Issue 5: "ImportError: No module named 'ryu'"
```bash
# Solution: Install ryu globally
sudo pip3 install ryu
# Or for this user
pip3 install --user ryu
```

### Issue 5b: "pip3 install ryu" gives error
```bash
# Solution: Install Ryu from GitHub source
# Follow INSTALL_RYU_FROM_GITHUB.md for complete instructions
cd ~
git clone https://github.com/osrg/ryu.git
cd ryu
pip3 install -e .
```

---

## Part 7: Quick Commands Reference

### Start Everything (Terminal 1)
```bash
cd ~/adaptive_ecmp
sudo python3 simple_topo.py
```

### Start Ryu Controller (Terminal 2)
```bash
cd ~/adaptive_ecmp
ryu-manager adaptive_ecmp.py     # Main controller
# OR
ryu-manager final_adaptive.py    # Enhanced version
# OR
ryu-manager traditional_ecmp.py  # Baseline
```

### Monitor Controller Logs (Terminal 3)
```bash
cd ~/adaptive_ecmp
# Use mininet CLI inside Terminal 1, OR run tests in Terminal 3
```

### Clean Up All Processes
```bash
sudo mn -c
sudo pkill -f ryu
sudo pkill -f mininet
```

---

## Part 8: File Structure After Setup

```
~/adaptive_ecmp/
├── adaptive_ecmp.py              ← Main controller (recommended)
├── final_adaptive.py             ← Enhanced controller
├── controller_in_loop_ecmp.py    ← Alternative controller
├── traditional_ecmp.py           ← Baseline controller
├── simple_topo.py                ← Network topology
├── git_topo.py                   ← Alternative topology
├── bandwidth_monitor.py          ← Monitoring utilities
├── graph.py                      ← Graph utilities
├── Documentation files (*.md)
└── __pycache__/                  ← Python cache
```

---

## Part 9: Understanding Output

### Mininet CLI Output
```
mininet> pingall
*** Ping: h1 -> h2 h3 h4
*** Results: 0% dropped
```
✓ Network is working correctly

### Ryu Controller Output
```
[LINK_CHANGE] Link event detected
[STAT] Utilization: Port 1: 45.2%, Port 2: 32.1%
[FORWARD] Packet for 10.0.0.4 -> Port 2 (lower load)
```
✓ Controller is monitoring and adapting paths

### Performance Test
```
h1 iperf -c 10.0.0.4 -t 5
----------------------------------------------------
[  3] 0.0-5.0 sec  125 MBytes  211 Mbits/sec
```
✓ Traffic flowing successfully

---

## Part 10: Next Steps

1. **Modify controllers**: Edit `adaptive_ecmp.py` to test changes
2. **Create custom topologies**: Modify `simple_topo.py`
3. **Performance testing**: Run longer iperf tests
4. **Compare implementations**: Run tests with each controller
5. **Deep dive**: Read `IMPLEMENTATION_DETAILS.md`

---

## Support

If you encounter issues:
1. Check **Part 6: Troubleshooting**
2. Verify OpenVSwitch is running: `sudo systemctl status openvswitch-switch`
3. Check Python version: `python3 --version` (should be 3.7+)
4. See original docs: `SETUP_AND_EXECUTION.md`, `QUICK_REFERENCE.md`
