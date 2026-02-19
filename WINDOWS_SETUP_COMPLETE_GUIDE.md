# Windows Setup Guide for Adaptive ECMP - Complete From Scratch

## Your Situation
- ✗ You're on Windows (D:\Melinia)
- ✗ Adaptive ECMP needs Linux
- ✗ Mininet doesn't work on Windows natively
- ✓ Solutions exist!

---

## Option 1: WSL2 (Windows Subsystem for Linux) - RECOMMENDED ⭐

**Pros**: Native integration, fast, easy
**Cons**: Windows 10/11 Pro/Enterprise required
**Time**: 30-40 minutes total

### Step 1: Check Windows Version

Press `Win + R` and type:
```
winver
```

Look for:
- **Windows 10**: Version 2004 or higher (Build 19041+)
- **Windows 11**: Any version

If you have these, continue. If not, use Option 2 (VirtualBox).

### Step 2: Enable WSL2

Open PowerShell **as Administrator** and run:

```powershell
# Run BOTH commands one at a time
wsl --install
wsl --set-default-version 2
```

**What this does**:
- Installs WSL2 (Windows Subsystem for Linux)
- Sets it to use Linux kernel
- This takes ~5 minutes and may auto-restart

### Step 3: Install Ubuntu

After restart, you have two options:

**Option A**: Microsoft Store (Easiest)
1. Open Microsoft Store
2. Search for "Ubuntu 22.04" or "Ubuntu 20.04"
3. Click "Get" → "Install"
4. Wait 5 minutes
5. Launch Ubuntu from Start Menu
6. Create username and password
7. Done!

**Option B**: Command line
```powershell
wsl --install -d Ubuntu-22.04
```

### Step 4: Verify WSL Installation

Open Ubuntu terminal and run:
```bash
uname -a
```

Should show something like:
```
Linux DESKTOP-XXXX 5.15.90.1-microsoft-standard ...
```

If you see this, WSL2 is working! ✓

---

## Option 2: VirtualBox (Fallback if WSL not available)

**Pros**: Works on any Windows version
**Cons**: Slower, needs more disk space, manual setup
**Time**: 1-1.5 hours total

### Step 1: Download VirtualBox

Go to: https://www.virtualbox.org/wiki/Downloads

Click "Windows hosts" → Download and install

### Step 2: Download Ubuntu ISO

Go to: https://ubuntu.com/download/desktop

Download "Ubuntu 22.04 LTS" (4.5GB)

### Step 3: Create Virtual Machine

1. Open VirtualBox
2. Click "New"
3. Settings:
   - Name: UbuntuAECMP
   - Type: Linux
   - Version: Ubuntu (64-bit)
   - RAM: 4096 MB (4GB)
   - Disk: 30GB (dynamic allocation)
4. Click "Create"

### Step 4: Install Ubuntu

1. Start the VM
2. When asked for ISO, select the Ubuntu ISO you downloaded
3. Follow Ubuntu installer (accept defaults)
4. Reboot when done

### Step 5: Install VirtualBox Guest Additions

In Ubuntu terminal:
```bash
sudo apt-get install virtualbox-guest-additions-iso
```

This makes Ubuntu run faster in the VM.

---

## Now You Have Ubuntu! Continue Below

Whether you chose WSL2 or VirtualBox, you now have Ubuntu running. Continue with:

---

# Installation Inside Ubuntu/WSL2

## Part A: System Setup (10 minutes)

### Step 1: Open Terminal

**WSL2**: 
- Just launch Ubuntu from Start Menu

**VirtualBox**: 
- Click inside Ubuntu window → Right-click → Open Terminal

### Step 2: Update System

Copy and paste this command:

```bash
sudo apt-get update
```

You'll be asked for password (the one you created during Ubuntu setup). Type it and press Enter.

**What this does**: Updates package lists (like app store catalog)

Wait for it to finish (shows `Processing triggers...` at end).

### Step 3: Upgrade System

```bash
sudo apt-get upgrade -y
```

The `-y` means "yes to all questions". This takes 5-10 minutes.

---

## Part B: Install Required Tools (15 minutes)

### Step 1: Install Python and Basic Tools

```bash
sudo apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    wget \
    build-essential
```

**Explanation**:
- `python3`: Python programming language
- `python3-pip`: Package manager for Python
- `git`: Version control (already used to clone project)
- `build-essential`: Tools for compiling code
- `-y`: Answer "yes" to all prompts

**Time**: 3-5 minutes

### Step 2: Install Mininet

```bash
sudo apt-get install -y mininet openvswitch-switch
```

**What this does**:
- `mininet`: Network emulator
- `openvswitch-switch`: Virtual switch software

**Time**: 2-3 minutes

### Step 3: Start OpenVSwitch Service

```bash
sudo service openvswitch-switch start
```

**Important**: Do this every time you restart Ubuntu

---

## Part C: Install Python Packages (10 minutes)

These are libraries that Adaptive ECMP needs.

### Step 1: Install Ryu

```bash
pip3 install ryu
```

**What is Ryu?**: OpenFlow controller framework
**Time**: 5 minutes (lots of downloading)

### Step 2: Install NetworkX

```bash
pip3 install networkx
```

**What is NetworkX?**: Graph algorithms library
**Time**: 1 minute

### Step 3: Verify Installation

```bash
python3 -c "import ryu, networkx; print('✓ All packages OK')"
```

**Expected output**:
```
✓ All packages OK
```

If you see this, everything is installed! ✓

---

## Part D: Set Up Adaptive ECMP Project (5 minutes)

### Step 1: Navigate to Project

The project is already cloned. Navigate to it:

**For WSL2**:
```bash
cd /mnt/d/Melinia/adaptive_ecmp
```

**For VirtualBox**:
You need to copy the project first:
```bash
# Create project folder
mkdir -p ~/adaptive_ecmp

# If files are on Windows, you'll need to copy them
# For now, let's clone fresh from GitHub
cd ~
git clone https://github.com/muthu-py/adaptive_ecmp.git
cd adaptive_ecmp
```

### Step 2: Verify Project Files

```bash
ls -la
```

You should see:
```
adaptive_ecmp.py
final_adaptive.py  
simple_topo.py
PROJECT_ANALYSIS.md
... (other files)
```

If you see these, you're ready! ✓

---

## Part E: Quick Verification Test (5 minutes)

Let's make sure everything works:

### Test 1: Check Mininet

```bash
sudo mn --version
```

Expected output:
```
mininet version 2.3.0
```

### Test 2: Check Python Packages

```bash
python3 -m ryu.cmd.manager --help
```

Expected output:
```
usage: manager [--help] ...
```

### Test 3: Run Topology

This will start the network for 10 seconds (using `timeout`):

```bash
cd ~/adaptive_ecmp
sudo timeout 10 python3 simple_topo.py 2>&1 | head -20
```

Expected output:
```
*** Starting network
*** Configuring hosts
*** Starting controller
*** Starting switches
...
```

If you see these, everything works! ✓

---

## Summary: What You've Installed

```
✓ Linux (Ubuntu) via WSL2 or VirtualBox
✓ Python 3 + pip (package manager)
✓ Mininet (network emulator)
✓ OpenVSwitch (virtual switch)
✓ Ryu (OpenFlow controller)
✓ NetworkX (graph algorithms)
✓ Adaptive ECMP project files
```

---

## Next Steps: Actually Running Adaptive ECMP

Once all the above is installed, follow these steps to run the project:

### Terminal 1: Start Network

```bash
cd ~/adaptive_ecmp
sudo python3 simple_topo.py
```

You'll see `mininet>` prompt when ready.

### Terminal 2: Start Controller (in new terminal)

```bash
cd ~/adaptive_ecmp
ryu-manager adaptive_ecmp.py
```

### Terminal 3: Run Tests (in Terminal 1 where mininet is running)

```bash
mininet> pingall
mininet> h1 ping h4
mininet> h4 iperf -s &
mininet> h1 iperf -c 10.0.0.4 -t 5
```

---

## Troubleshooting During Installation

### Issue 1: "Command not found: sudo"
**Cause**: You're already root
**Fix**: Remove `sudo` from command

### Issue 2: "Permission denied" or "sudo: command not found"
**Cause**: WSL2 needs configuration
**Fix**: Close and reopen Ubuntu terminal

### Issue 3: "python3: command not found"
**Cause**: Python not installed
**Fix**: Run Part B Step 1 again

### Issue 4: Mininet installation fails
**Cause**: System packages missing
**Fix**: Run this first:
```bash
sudo apt-get install -y openvswitch-testcontroller
sudo apt-get purge -y mininet
sudo apt-get install -y mininet
```

### Issue 5: Ryu installation fails
**Cause**: pip3 issue
**Fix**: 
```bash
sudo apt-get install -y python3-dev
pip3 install --upgrade pip
pip3 install ryu
```

---

## Quick Command Reference

### Starting Services
```bash
sudo service openvswitch-switch start   # Start OVS
```

### Checking Installation
```bash
python3 --version
pip3 list | grep -E "ryu|networkx"
mininet --version
```

### Running Project
```bash
cd ~/adaptive_ecmp
sudo python3 simple_topo.py
```

### Common Issues
```bash
sudo dpkg --configure -a          # Fix broken packages
sudo apt-get clean                # Free up space
sudo apt-get autoclean            # Clean old packages
```

---

## Final Checklist

Before moving to actual testing, verify:

- [ ] Ubuntu running (WSL2 or VirtualBox)
- [ ] `python3 --version` works
- [ ] `pip3 list` shows ryu and networkx
- [ ] `sudo mn --version` works
- [ ] Can navigate to ~/adaptive_ecmp
- [ ] `ls adaptive_ecmp.py` shows the file
- [ ] No error messages above

If all checked, you're ready for the actual Adaptive ECMP testing! ✓

---

## Still Having Issues?

If installation fails at any step:

1. **Copy the exact error message**
2. **Do this**:
   ```bash
   lsb_release -a
   uname -a
   pip3 --version
   ```
3. **Run the installation command again with verbose output**
4. Check specific section in this guide for that error

---

## Next: Actually Running Adaptive ECMP

Once installation is complete, read:
- File: `~/adaptive_ecmp/SETUP_AND_EXECUTION.md` (Parts 3-4)
- This explains how to actually run the project

---

