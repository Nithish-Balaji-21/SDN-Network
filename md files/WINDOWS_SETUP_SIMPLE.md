# Windows to Linux Setup - Visual Step-by-Step (Simplified)

## TL;DR - The 3-Minute Version

**You're on Windows** → You need **Linux** → You can get it via **WSL2** (easy) or **VirtualBox** (slower)

**Choice**: Pick ONE:
- ✅ **WSL2** - If Windows 10/11 Pro
- ✅ **VirtualBox** - If basic Windows or you're unsure

---

## OPTION A: WSL2 Setup (Recommended - 30 min)

### STEP 1️⃣: Check Your Windows

Right-click Start button → Run `winver`

See version 20H2 or newer? ✓ Continue
See older version? Skip to OPTION B (VirtualBox)

### STEP 2️⃣: Open PowerShell as Admin

Right-click PowerShell → "Run as Administrator"

Copy and paste (one by one):

```powershell
# Command 1
wsl --install

# Press Enter, wait 5 minutes, computer may restart

# After restart, open PowerShell again as Admin

# Command 2  
wsl --set-default-version 2
```

### STEP 3️⃣: Install Ubuntu

**Method 1 - Easy (Recommended)**:
- Open Microsoft Store
- Search "Ubuntu 22.04"
- Click "Get" then "Install"
- Wait 5 minutes
- Launch from Start menu
- Create username + password
- You're done with Step 3! ✓

**Method 2 - Command line**:
```powershell
wsl --install -d Ubuntu-22.04
```

### STEP 4️⃣: Verify WSL Works

Open Ubuntu terminal (from Start menu)

Type:
```bash
uname -a
```

See `Linux` in output? Perfect! ✓

---

## OPTION B: VirtualBox Setup (Fallback - 1 hour)

### STEP 1️⃣: Download Software

**Download VirtualBox**:
- Go to: https://www.virtualbox.org/wiki/Downloads
- Click "Windows hosts"
- Install it (double-click and follow prompts)

**Download Ubuntu**:
- Go to: https://ubuntu.com/download/desktop
- Download "Ubuntu 22.04 LTS" (4.5GB - takes 10+ min)

### STEP 2️⃣: Create Virtual Machine

- Open VirtualBox
- Click "New"
- Name: `AECMPLinux`
- RAM: `4096 MB` (4GB)
- Disk: `30 GB`
- Click "Create"

### STEP 3️⃣: Install Ubuntu

- Start the VM
- When it asks for ISO: select Ubuntu ISO file you downloaded
- Follow installer (accept everything, create password)
- Reboot when done

### STEP 4️⃣: First Boot

- VM will boot into Ubuntu
- Open Terminal
- Type password when asked
- Ready! ✓

---

## Now You Have Ubuntu! Continue Here

**You now have Linux running** (via WSL2 or VirtualBox)

---

## STEP 5️⃣: Copy Project to Linux

### For WSL2 Users:

Open Ubuntu terminal and run:

```bash
cd /mnt/d/Melinia/adaptive_ecmp
ls
```

See files? Good! ✓

### For VirtualBox Users:

You need to copy the project. Run:

```bash
cd ~
git clone https://github.com/muthu-py/adaptive_ecmp.git
cd adaptive_ecmp
ls
```

See files? Good! ✓

---

## STEP 6️⃣: Install What Adaptive ECMP Needs

Open Ubuntu terminal and paste these commands ONE AT A TIME.

### 6a: Update Ubuntu

```bash
sudo apt-get update
```

**If you see "Temporary failure resolving" - DNS issue!**

Fix DNS and retry:
```bash
# Add Google DNS to system
echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf
echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf

# Try update again
sudo apt-get update
```

**If still failing**, try this minimal install (skip build-essential for now):
```bash
# Stop update with Ctrl+C if needed, then:
sudo apt-get install -y python3 git wget curl
```

You can add build-essential later if needed.

**For VirtualBox users with network issues:**
```bash
# Check if you have internet
ping google.com

# If no response, try restarting network:
sudo systemctl restart networking
```

### 6b: Install Basic Tools

```bash
sudo apt-get install -y python3 git curl wget build-essential
```

**For Ubuntu 24.04 (newer)**, pip needs special permission. Use this:

```bash
python3 get-pip.py --break-system-packages
rm get-pip.py
```

**If you still get "externally-managed-environment" error**, skip pip entirely and use system packages instead:

```bash
# Install all packages from apt (no pip needed!)
sudo apt-get install -y python3-networkx python3-eventlet python3-dev
```

This is actually simpler and recommended for this project.

**Verify packages installed:**
```bash
python3 -c "import networkx; print('networkx OK')"
```

Should show `networkx OK`. ✓

### 6c: Install Mininet

```bash
sudo apt-get install -y mininet openvswitch-switch
```

**Verify mininet installed:**
```bash
sudo mn --version
```

Should show `mininet version 2.x.x` ✓

**If you get "command not found"**, try:
```bash
# Install again
sudo apt-get install --reinstall mininet
# Or try the alternative package
sudo apt-get install -y mn
```

Wait 2-3 minutes.

### 6d: Install Python Libraries (Ryu) - Clone from Repo

**Clone from the official Ryu repo (most reliable):**

```bash
cd ~
git clone https://github.com/faucetsdn/ryu.git
cd ryu
```

**Python 3.12 has compatibility issues with Ryu's setup.py. Use this workaround:**

```bash
# Install distutils package for Python 3.12
pip3 install setuptools-distutils --break-system-packages

# Install other dependencies
pip3 install eventlet netaddr --break-system-packages
```

**Edit setup.py to skip the problematic hook:**

```bash
# Comment out the hook that causes the error
sed -i '21s/^/# /' setup.py  # Comments out line 21

# Now try installing
python3 setup.py install --user
```

**If that fails**, use pip directly without building:

```bash
# Go back to ryu directory
cd ~/ryu

# Install just the dependencies and current code
pip3 install -e . --no-build-isolation --break-system-packages
```

**If both fail**, download pre-built wheel instead:

```bash
# Skip source build entirely
pip3 install ryu==4.34 --no-cache-dir --break-system-packages
```

**Verify Ryu installed:**
```bash
ryu-manager --help
# OR
python3 -c "import ryu; print(ryu.__version__)"
```

Should show help text or version. ✓

### 6e: Start OpenVSwitch Service

```bash
sudo service openvswitch-switch start
```

---

## STEP 7️⃣: Verify Everything Works

Run these checks:

```bash
# Check Python
python3 --version

# Should show: Python 3.x.x

# Check Mininet  
sudo mn --version

# Should show: mininet version 2.x.x

# Check packages
python3 -c "import ryu, networkx; print('OK')"

# Should show: OK
```

If all three show success ✓, you're ready!

---

## STEP 8️⃣: Your First Test Run

### Terminal 1: Start Network

```bash
cd ~/adaptive_ecmp
sudo python3 simple_topo.py
```

Wait for `mininet>` prompt (this is good!)

### Terminal 2: Start Controller (open NEW terminal)

```bash
cd ~/adaptive_ecmp
ryu-manager adaptive_ecmp.py
```

You'll see lots of messages. That's good! ✓

### Terminal 1 (back to first terminal): Run Test

In the `mininet>` prompt, type:

```bash
mininet> pingall
```

See `received 100% packets` or similar? **SUCCESS!** ✓

---

## What Just Happened?

```
1. Linux started network (4 switches, 4 computers)
2. Adaptive ECMP controller started
3. You tested if all computers can reach each other
4. Result: They can! System works! ✓
```

---

## Next: Actual Testing

Now that basic setup works, do this:

1. Open `~/adaptive_ecmp/SETUP_AND_EXECUTION.md` (Part 3 onward)
2. Follow the test scenarios
3. See load balancing in action

---

## Troubleshooting - If Something Breaks

| Error | Solution |
|-------|----------|
| `externally-managed-environment` | Ubuntu 24.04: Add `--break-system-packages` to pip command, or use virtual environment: `python3 -m venv ~/ryu_env` |
| `0% [Connecting...]` or packages show "Ign:" | **Network stalled**: Press Ctrl+C. In PowerShell: `wsl --shutdown`. Reopen Ubuntu and retry |
| `command not found: python3` | Run: `sudo apt-get install -y python3` |
| `sudo: command not found` | You're already root, remove `sudo` |
| `mininet: command not found` | Run: `sudo apt-get install -y mininet` |
| `Permission denied` | Add `sudo` at front of command |
| `ModuleNotFoundError: ryu` | Run: `cd ~/ryu` then `pip3 install -e . --break-system-packages` |
| Can't connect WSL to internet | Run: `wsl --shutdown` in PowerShell, then reopen Ubuntu |
| `Package pip3 not available` | Use system packages: `sudo apt-get install -y python3-networkx python3-eventlet` |
| VirtualBox slow | Increase RAM in Settings |

---

## Most Common Mistakes (Don't Do These!)

❌ **Don't**: Skip the `sudo service openvswitch-switch start` command
✅ **Do**: Run it after Ubuntu starts

❌ **Don't**: Try to install on Windows directly (it won't work)
✅ **Do**: Install in Ubuntu first

❌ **Don't**: Close terminal while installation running
✅ **Do**: Wait for prompt to return

❌ **Don't**: Use different Python (python vs python3)
✅ **Do**: Always use `python3`

❌ **Don't**: Skip creating password for Ubuntu
✅ **Do**: Remember that password (`sudo` needs it)

---

## Directory Structure After Setup

```
Your Windows Machine
└─ D:\Melinia\adaptive_ecmp\      (original, still here)

Ubuntu (WSL2 or VirtualBox)
└─ ~/adaptive_ecmp/               (Linux copy or clone)
   ├─ adaptive_ecmp.py
   ├─ final_adaptive.py
   ├─ simple_topo.py
   ├─ SETUP_AND_EXECUTION.md
   └─ ... other files
```

---

## Quick Command Summary

After everything is installed, these are commands you'll use:

```bash
# Navigate to project
cd ~/adaptive_ecmp

# Start network (Terminal 1)
sudo python3 simple_topo.py

# Start controller (Terminal 2)
ryu-manager adaptive_ecmp.py

# Run tests (back in Terminal 1 at mininet> prompt)
mininet> pingall
mininet> h1 ping h4
mininet> h1 iperf -c 10.0.0.4 -t 5
mininet> exit           # Stop Mininet

# Stop controller (Terminal 2)
# Press Ctrl+C

# Next time you restart Ubuntu, run this:
sudo service openvswitch-switch start
```

---

## You're Almost There! 🎉

Once you complete Step 8 and see `pingall` succeed, you have:

✅ Linux (Ubuntu) running
✅ All required software installed  
✅ Adaptive ECMP project ready
✅ Network emulation working
✅ Controller running
✅ Verified connectivity working

**Next**: Read `SETUP_AND_EXECUTION.md` Part 3 to learn the actual test scenarios

---

## One Final Thing

After Step 8, if you want to stop everything:

**Stop Mininet**:
```bash
mininet> exit
```

**Stop Controller**:
- Press `Ctrl+C` in Terminal 2

**You can restart anytime** by repeating Steps 8

---

**Questions?** Check the full guide at:
`~/adaptive_ecmp/WINDOWS_SETUP_COMPLETE_GUIDE.md`

**Ready?** Start with Step 1 above, follow carefully. You'll have it running in 30-60 minutes!

