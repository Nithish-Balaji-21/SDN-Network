# Quick Start: Linux/Kali Setup (5 Minutes)

## Step 1: Get the Files to Your Kali Machine

**Option A: Using SCP from Windows**
```bash
# On Kali Linux terminal
scp -r username@<windows-ip>:/d/Melinia/adaptive_ecmp ~/adaptive_ecmp
```

**Option B: Using Git (if available)**
```bash
cd ~
git clone <repo-url>
cd adaptive_ecmp
```

**Option C: USB Drive**
- Copy folder to USB on Windows
- Mount on Kali and copy to home folder

---

## Step 2: Automatic Setup (Easiest)

```bash
# Make script executable
chmod +x ~/adaptive_ecmp/setup_linux.sh

# Run automatic setup
sudo bash ~/adaptive_ecmp/setup_linux.sh
```

**This installs everything automatically!**

---

## Step 3: Run the Project

### Terminal 1: Start Network
```bash
cd ~/adaptive_ecmp
sudo python3 simple_topo.py
```
Wait until you see: `mininet>`

### Terminal 2: Start Controller
```bash
cd ~/adaptive_ecmp
ryu-manager adaptive_ecmp.py
```

### Terminal 1: Run Tests (at mininet> prompt)
```
mininet> pingall
mininet> h1 iperf -c 10.0.0.4 -t 5
mininet> exit
```

---

## That's It!

✓ Network is running  
✓ Controller is adapting paths  
✓ Topology is emulated with Mininet  

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Permission denied" | Use `sudo` |
| "Port already in use" | `sudo mn -c` then retry |
| "OVS not running" | `sudo systemctl start openvswitch-switch` |
| "No module named 'ryu'" | `sudo pip3 install ryu` |

---

## More Info

- **Full setup guide**: `LINUX_KALI_SETUP.md`
- **Implementation details**: `IMPLEMENTATION_DETAILS.md`
- **Project overview**: `PROJECT_ANALYSIS.md`
