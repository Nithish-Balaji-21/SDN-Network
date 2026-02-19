# Windows Setup Decision Tree & Flowchart

## Quick Decision: Which Option Should I Choose?

```
START
  │
  ├─ Do you have Windows 10 or 11? 
  │  │
  │  ├─ NO → Skip to STOP (need to upgrade Windows)
  │  └─ YES → Continue
  │
  ├─ Do you have Windows 10/11 Pro or Enterprise?
  │  │
  │  ├─ YES → ✅ USE WSL2 (Option A) - Jump to "OPTION A BELOW"
  │  │
  │  └─ NO (Home Edition) → Continue
  │
  ├─ Do you have 30GB free disk space?
  │  │
  │  ├─ YES → ✅ USE VIRTUALBOX (Option B) - Jump to "OPTION B BELOW"
  │  │
  │  └─ NO → Contact me for alternatives
  │
  └─ SETUP COMPLETE
```

---

## Your Situation Right Now

**Current**: Windows machine with project cloned to `D:\Melinia\adaptive_ecmp\`
**Problem**: Adaptive ECMP needs Linux (Mininet is Linux-only)
**Solution**: Create Linux environment
**Goal**: Run the project successfully

---

## THE FASTEST PATH (WSL2 for Windows Pro Users)

### Total Time: 30-35 minutes

### Step-by-Step Exact Commands

**1. Open PowerShell as Administrator**
   - Right-click Windows Start button
   - Type `powershell`
   - Right-click PowerShell
   - Select "Run as Administrator"

**2. Copy these commands (one at a time, press Enter after each)**

First command:
```powershell
wsl --install
```
- Wait for it to finish
- Computer will restart (this is normal)
- After restart, continue with next command

Second command (after restart):
```powershell
wsl --set-default-version 2
```

**3. Install Ubuntu 22.04**

Option A - Microsoft Store (easiest):
- Click Start button
- Type "store"
- Open Microsoft Store
- Search: "Ubuntu 22.04"
- Click any result
- Click "Get" → "Install"
- Wait ~5 minutes
- Click "Open" when done
- Choose username (e.g., `xiaoming`)
- Choose password (remember this!)
- Wait for `$` prompt

Option B - Command line:
```powershell
wsl --install -d Ubuntu-22.04
```

**4. Inside Ubuntu Terminal (you'll see `$` prompt)**

Copy and paste these commands one-by-one:

```bash
# Update system
sudo apt-get update
```
Type your password + Enter. Wait for `done`.

```bash
# Install tools
sudo apt-get install -y python3 python3-pip git curl wget build-essential
```
Wait 3-5 minutes.

```bash
# Install Mininet and networking
sudo apt-get install -y mininet openvswitch-switch
```
Wait 2-3 minutes.

```bash
# Start network service
sudo service openvswitch-switch start
```

```bash
# Install Python packages
pip3 install ryu networkx
```
Wait 5 minutes.

**5. Navigate to Your Project**

```bash
cd /mnt/d/Melinia/adaptive_ecmp
ls
```

See the files? Good!

**6. Verify Everything Works**

```bash
sudo mn --version
python3 -c "import ryu, networkx; print('ALL GOOD!')"
```

Both commands should give you output (no errors).

**7. Run Quick Test**

This terminal:
```bash
sudo python3 simple_topo.py
```

Open NEW Ubuntu terminal and run:
```bash
cd /mnt/d/Melinia/adaptive_ecmp
ryu-manager adaptive_ecmp.py
```

Back in FIRST terminal, at `mininet>` prompt:
```bash
mininet> pingall
```

**✓ SUCCESS** - If you see "received 100%" or similar

---

## THE MOST COMPATIBLE PATH (VirtualBox for Everyone)

### Total Time: 1-1.5 hours (including downloads)

### Prerequisites
- 30GB free disk space
- 15 minutes download time (Ubuntu ISO)

### Step-by-Step

**1. Download & Install VirtualBox**

- Go to: https://www.virtualbox.org/wiki/Downloads
- Click "Windows hosts"
- Download (~150MB)
- Double-click installer
- Click "Next" repeatedly, keep defaults
- Finish

**2. Download Ubuntu ISO**

- Go to: https://ubuntu.com/download/desktop
- Download Ubuntu 22.04 LTS (~4.5GB)
- This takes 15+ minutes on normal internet

**3. Create Virtual Machine**

- Open VirtualBox
- Click "New"
- Fill in exactly:
  - Name: `UbuntuAECMP`
  - Type: `Linux`
  - Version: `Ubuntu (64-bit)`
  - RAM: `4096` MB
  - Storage: `30` GB
  - Click "Create"

**4. Install Ubuntu in VM**

- Start the virtual machine
- When it asks for ISO: click folder icon → select Ubuntu ISO you downloaded
- Click "Install"
- Follow installer (accept all defaults)
- When asked for password: choose something you remember!
- Wait 10 minutes for installation
- Click "Restart Now"
- Wait for Ubuntu to fully boot (shows desktop)

**5. Open Terminal Inside VM**

- Right-click desktop
- Select "Open Terminal"

**6. Now Follow Installation Steps from WSL2 Section Above**

From the Ubuntu terminal, run commands from Step 4-7 of WSL2 section.

(They're identical once you have Ubuntu)

**7. Run Quick Test**

Same three steps as WSL2 section above.

---

## Visual Comparison

| Feature | WSL2 | VirtualBox |
|---------|------|-----------|
| Setup time | 20-30 min | 60+ min |
| Speed | Fast | Slower |
| Disk space | 10GB | 30GB |
| RAM needed | 8GB | 12GB |
| Restart needed | Yes (once) | No |
| Windows versions | Pro+ only | All |
| Integration | Seamless | Separate window |
| Learning curve | Easy | Easier |

**→ Choose WSL2 if you can, VirtualBox if you must**

---

## After Setup: What to Do Next

Once you successfully run `mininet> pingall` (Step 7), you have achieved:

✅ Linux environment running
✅ All software installed
✅ Project accessible in Linux
✅ Network simulation working
✅ Controller can start
✅ Connectivity verified

Now read: `SETUP_AND_EXECUTION.md` (Part 3 and beyond) for actual testing scenarios.

---

## Exact Copy-Paste Commands by Setup Type

### WSL2 Setup (Copy-Paste These)

```powershell
# PowerShell as Administrator
wsl --install
# Wait and restart, then:
wsl --set-default-version 2
# Then through Microsoft Store or:
wsl --install -d Ubuntu-22.04
```

### Ubuntu Setup (Same for Both WSL2 and VirtualBox)

```bash
# In Ubuntu Terminal
sudo apt-get update
sudo apt-get install -y python3 python3-pip git curl wget build-essential
sudo apt-get install -y mininet openvswitch-switch
sudo service openvswitch-switch start
pip3 install ryu networkx

# For WSL2 only:
cd /mnt/d/Melinia/adaptive_ecmp

# For VirtualBox only:
cd ~
git clone https://github.com/muthu-py/adaptive_ecmp.git
cd adaptive_ecmp

# Both: Verify
ls -la
sudo mn --version
python3 -c "import ryu, networkx; print('OK')"
```

### Running Project (Same for Both)

Terminal 1:
```bash
cd ~/adaptive_ecmp
sudo python3 simple_topo.py
```

Terminal 2:
```bash
cd ~/adaptive_ecmp
ryu-manager adaptive_ecmp.py
```

Terminal 1 (at mininet> prompt):
```bash
mininet> pingall
mininet> h1 ping h4
```

---

## Common Problems & Solutions

### "command not found" errors
**Fix**: Make sure you're in Ubuntu terminal, not Windows PowerShell

### "sudo: command not found"
**Fix**: Already running as root, remove `sudo`

### Takes forever downloading
**Fix**: Normal, just wait. Grab coffee ☕

### Can't type password in terminal
**Fix**: It's invisible - keep typing and press Enter

### Installation fails halfway
**Fix**: Run `sudo apt-get install -y <package-name>` individually

### Can't find Ubuntu in Start menu
**Fix** (WSL2): Open Microsoft Store, find Ubuntu, click "Install"

### Ubuntu window too small (VirtualBox)
**Fix**: Click anywhere in window, press Ctrl+F to fullscreen

---

## Estimated Timeline

### WSL2 Path
```
5 min   - Check Windows version
10 min  - Run wsl commands
5 min   - Install Ubuntu
5 min   - Navigate and verify
10 min  - Install tools (parallel)
___________________________
35 min  Total
```

### VirtualBox Path  
```
10 min  - Download & install VirtualBox
15 min  - Download Ubuntu ISO (meanwhile)
10 min  - Create virtual machine
20 min  - Install Ubuntu on VM
5 min   - Navigate and create terminal
10 min  - Install tools
___________________________
70 min  Total (most is downloading/waiting)
```

---

## Verification Checklist

After installing, verify each item:

- [ ] Ubuntu terminal opens and you can type
- [ ] `python3 --version` shows Python 3.x
- [ ] `pip3 list` shows `ryu` and `networkx`
- [ ] `sudo mn --version` shows mininet version
- [ ] Can navigate to adaptive_ecmp folder
- [ ] `ls` shows `adaptive_ecmp.py` file
- [ ] `sudo service openvswitch-switch start` completes
- [ ] Can run `sudo python3 simple_topo.py` (stops with Ctrl+C)
- [ ] Can run `ryu-manager adaptive_ecmp.py` 
- [ ] `mingall` in mininet shows success

Check ALL items before declaring "ready"

---

## Emergency Troubleshooting

If completely stuck:

### WSL2 Issues:
```powershell
# Reset WSL
wsl --shutdown
wsl --unregister Ubuntu-22.04
wsl --install -d Ubuntu-22.04
```

### Ubuntu Issues:
```bash
# Reinstall critical packages
sudo apt-get purge -y mininet openvswitch-switch ryu
sudo apt-get install -y mininet openvswitch-switch python3-pip
pip3 install ryu networkx
```

### Still Stuck:
Post error message to [GitHub issues](https://github.com/muthu-py/adaptive_ecmp/issues)

---

## Next: Actually Learning the Project

Once setup complete ✓, read in this order:

1. `PROJECT_ANALYSIS.md` - What is this project
2. `QUICK_REFERENCE.md` - 5-minute overview  
3. `SETUP_AND_EXECUTION.md` - Part 3 (actual testing)
4. `IMPLEMENTATION_DETAILS.md` - Deep dive

---

## Final Tip

**Don't overthink it!** Just follow the exact steps. Most people get it right first try.

When stuck, re-read that section carefully. Usually the answer is right there.

**You've got this!** 🚀

---

