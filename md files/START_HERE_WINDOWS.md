# START HERE - Windows Setup for Adaptive ECMP

## Your Situation
✅ You have Windows (D:\Melinia)
✅ You've cloned the project successfully
❌ Adaptive ECMP needs Linux (Mininet is Linux-only)
❓ You don't know how to set it up

**Good news**: I've created step-by-step guides. Just follow them!

---

## Which Guide Do I Read?

### 🚀 START WITH ONE OF THESE:

#### Option 1: "Tell me the simplest version" (⭐ Recommended)
👉 Read: `WINDOWS_SETUP_SIMPLE.md`
- Visual step-by-step
- Copy-paste commands
- ~35 minutes if WSL2, ~70 if VirtualBox
- **Read this first**

#### Option 2: "I want complete details"
👉 Read: `WINDOWS_SETUP_COMPLETE_GUIDE.md`
- Full explanations
- Troubleshooting for each section
- Detailed setup
- **Read this if Option 1 is unclear**

#### Option 3: "Help me decide between WSL2 vs VirtualBox"
👉 Read: `WINDOWS_SETUP_DECISION_FLOWCHART.md`
- Decision tree
- Comparison table
- Which option for your situation
- **Read this if you're unsure**

---

## Quick Decision (1 Minute)

**Answer these:**

1. Windows 10 or 11? 
   - YES → Continue to Q2
   - NO → You need to upgrade Windows first

2. Windows Home, Pro, or Enterprise?
   - Pro/Enterprise → Use WSL2 (faster, simpler)
   - Home → Use VirtualBox (always works)

3. Have 30GB free disk space?
   - YES → Continue
   - NO → Clean up disk, then start

---

## The Simplest Instructions (Copy-Paste)

**This guides you through everything you need to type.**

### For Windows Pro/Enterprise (WSL2 - 35 min)

**1. Open PowerShell as Admin**
- Right-click Start button
- Click PowerShell
- Right-click → "Run as Administrator"

**2. Paste these commands (one-by-one, press Enter)**

```powershell
wsl --install
```
Wait 5 min, computer restarts.

After restart, open PowerShell as Admin again:

```powershell
wsl --set-default-version 2
wsl --install -d Ubuntu-22.04
```

**3. Ubuntu opens, create password**

Then paste this (wait ~10 min):

```bash
sudo apt-get update && sudo apt-get install -y python3 python3-pip git curl wget build-essential mininet openvswitch-switch && sudo service openvswitch-switch start && pip3 install ryu networkx
```

**4. Verify it worked**

```bash
cd /mnt/d/Melinia/adaptive_ecmp
ls
sudo mn --version
```

See files and version number? ✅ You're done with setup!

---

### For Windows Home (VirtualBox - 70 min)

**1. Download & install VirtualBox**
- https://www.virtualbox.org/wiki/Downloads
- Click Windows hosts
- Install (next, next, finish)

**2. Download Ubuntu ISO**
- https://ubuntu.com/download/desktop
- Download (takes 15+ min)

**3. Create VM in VirtualBox**
- Open VirtualBox
- Click "New"
- Name: UbuntuAECMP
- RAM: 4096 MB
- Disk: 30GB
- Click Create

**4. Start VM, install Ubuntu**
- Start the VM
- Browse to Ubuntu ISO
- Follow installer (accept defaults)
- Reboot when done (wait 10 min)

**5. Open Terminal in Ubuntu**
- Right-click desktop
- Open Terminal

**6. Paste this (wait ~10 min)**

```bash
sudo apt-get update && sudo apt-get install -y python3 python3-pip git curl wget build-essential mininet openvswitch-switch && sudo service openvswitch-switch start && pip3 install ryu networkx
```

**7. Verify**

```bash
cd ~
git clone https://github.com/muthu-py/adaptive_ecmp.git
cd adaptive_ecmp
ls
sudo mn --version
```

See files and version? ✅ Setup complete!

---

## Now Run Your First Test

**Terminal 1:**
```bash
cd ~/adaptive_ecmp
sudo python3 simple_topo.py
```

Wait for `mininet>` prompt.

**Terminal 2 (open new terminal):**
```bash
cd ~/adaptive_ecmp
ryu-manager adaptive_ecmp.py
```

**Terminal 1 (at mininet> prompt):**
```bash
mininet> pingall
```

**See "received" messages?** 🎉 **SUCCESS!**

---

## What If Something Goes Wrong?

1. Copy the error message
2. Check the appropriate guide:
   - WSL2 issues → WINDOWS_SETUP_COMPLETE_GUIDE.md (search error)
   - General issues → WINDOWS_SETUP_DECISION_FLOWCHART.md (Troubleshooting)
   - Command confusion → WINDOWS_SETUP_SIMPLE.md (re-read section)

3. Most common fix:
   ```bash
   # Reinstall packages
   sudo apt-get install -y mininet python3-pip
   pip3 install ryu networkx
   ```

---

## File Reference Guide

| Situation | Read This |
|-----------|-----------|
| "Tell me what to do step-by-step" | WINDOWS_SETUP_SIMPLE.md |
| "I need full explanations and troubleshooting" | WINDOWS_SETUP_COMPLETE_GUIDE.md |
| "WSL2 or VirtualBox?" | WINDOWS_SETUP_DECISION_FLOWCHART.md |
| "What is this project I just installed?" | PROJECT_ANALYSIS.md |
| "How do I run actual tests?" | SETUP_AND_EXECUTION.md |
| "I want to understand the code" | IMPLEMENTATION_DETAILS.md |
| "Optimize/improve the project" | IMPLEMENTATION_ROADMAP.md |
| "Quick reference while coding" | QUICK_REFERENCE.md |

---

## Timeline

```
00:00  - Read this file (3 min)
00:03  - Open WINDOWS_SETUP_SIMPLE.md
00:05  - Download WSL2/VirtualBox/Ubuntu
00:25  - Run installation commands
00:35  - Verify everything works
00:40  - Run first test (pingall)
00:45  - SUCCESS! 🎉
```

**Actual working time: ~30-40 minutes**
**Total with downloads: ~45-75 minutes**

---

## What You'll Have After Setup

✅ Linux (Ubuntu) running on your Windows machine
✅ Mininet network emulator installed
✅ Ryu OpenFlow controller installed
✅ Adaptive ECMP project ready to use
✅ Test network created and verified
✅ Controller responding to packets
✅ Basic connectivity working

Then you can:
- Run test scenarios
- Compare with traditional ECMP
- Analyze performance
- Modify code to improve it
- Deploy ideas

---

## Most Important Thing to Remember

> **Don't skip steps. Don't modify commands. Just copy-paste and press Enter.**

The guides are tested. If you follow them exactly, you will succeed.

If something fails, the error message is usually the answer. Read it carefully.

---

## FAQ

**Q: Will this break my Windows?**
A: No. WSL2 and VirtualBox are safe. Your Windows stays untouched.

**Q: Can I use Python installed on Windows?**
A: No. You need Linux. That's why we're setting it up.

**Q: Do I need to pay for anything?**
A: No. Everything is free (Ubuntu, VirtualBox, Ryu, Mininet, etc.)

**Q: How much disk space do I need?**
A: ~30-40GB total (10GB for WSL2, 30GB for VirtualBox)

**Q: What if I close Terminal 1?**
A: Network stops. Open Terminal and run `sudo python3 simple_topo.py` again.

**Q: Can I use actual networking instead of Mininet?**
A: Yes, eventually. But start with Mininet for learning.

**Q: How do I undo everything if I mess up?**
A: WSL2: `wsl --unregister Ubuntu-22.04`
   VirtualBox: Delete VM, delete Ubuntu ISO
   Your Windows is always safe.

---

## Next Steps After Setup

1. ✅ Complete setup using this guide
2. ✅ Run and verify `sudo python3 simple_topo.py` works
3. ✅ Run and verify `ryu-manager adaptive_ecmp.py` works
4. 👉 Read `SETUP_AND_EXECUTION.md` Part 3 (run test scenarios)
5. 👉 Run all 4 test scenarios
6. 👉 Compare adaptive vs traditional ECMP
7. 👉 Read `IMPLEMENTATION_ROADMAP.md` (improve project)

---

## NOW PROCEED

**Pick your setup type:**

### ⭐ Easy Path (WSL2 for Windows Pro/Enterprise)
👉 Go to: `WINDOWS_SETUP_SIMPLE.md` - Section "OPTION A"

### ✅ Alternative Path (VirtualBox for Windows Home)
👉 Go to: `WINDOWS_SETUP_SIMPLE.md` - Section "OPTION B"

### ℹ️ Need Help Choosing?
👉 Go to: `WINDOWS_SETUP_DECISION_FLOWCHART.md`

### 📚 Want Full Details?
👉 Go to: `WINDOWS_SETUP_COMPLETE_GUIDE.md`

---

## Support

**If you get stuck:**
1. Re-read the exact section
2. Check "Troubleshooting" in appropriate guide
3. Google the error message
4. Post on GitHub issues

**You will succeed.** Just follow the steps carefully.

---

**Ready?** Open WINDOWS_SETUP_SIMPLE.md and start!

