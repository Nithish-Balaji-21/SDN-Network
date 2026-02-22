# Fresh Install - Step by Step Commands

## PHASE 1: Clear WSL and Install Ubuntu (PowerShell)

Open PowerShell as Administrator and run these commands one by one:

### Step 1: Stop WSL
```powershell
wsl --shutdown
```

### Step 2: Unregister existing Ubuntu
```powershell
wsl --unregister Ubuntu
```

### Step 3: Install fresh Ubuntu 22.04
```powershell
wsl --install -d Ubuntu-22.04
```
**NOTE:** This will take 5-10 minutes. Wait for it to complete and show the username/password setup screen.

### Step 4: Set Ubuntu as default (if needed)
```powershell
wsl --set-default Ubuntu-22.04
```

### Step 5: Verify WSL is ready
```powershell
wsl --list --verbose
```
✓ You should see `Ubuntu-22.04` with STATE `Running` or `Stopped`

---

## PHASE 2: Initial Ubuntu Setup (Run in Ubuntu terminal)

Open Ubuntu terminal and run these commands one by one:

### Step 1: Update system repositories
```bash
sudo apt-get update
```

### Step 2: Install basic tools
```bash
sudo apt-get install -y build-essential curl wget git python3-dev python3-venv
```

### Step 3: Install Python 3.10
```bash
sudo apt-get install -y python3.10 python3.10-venv python3.10-dev
```

### Step 4: Verify Python 3.10 is installed
```bash
python3.10 --version
```
✓ Should show: `Python 3.10.x`

---

## PHASE 3: Create Virtual Environment (Ubuntu terminal)

### Step 1: Create project directory
```bash
mkdir -p ~/adaptive_ecmp_project
cd ~/adaptive_ecmp_project
```

### Step 2: Create virtual environment with Python 3.10
```bash
python3.10 -m venv aecmp_env
```

### Step 3: Activate virtual environment
```bash
source aecmp_env/bin/activate
```
✓ You should see `(aecmp_env)` at the beginning of the command line

### Step 4: Upgrade pip in virtual environment
```bash
pip install --upgrade pip setuptools wheel
```

---

## PHASE 4: Install Python Dependencies (Ubuntu terminal - keep venv activated)

Make sure you still have `(aecmp_env)` active from previous step!

### Step 1: Install eventlet 3.1
```bash
pip install eventlet==0.33.3
```

### Step 2: Install Ryu
```bash
pip install ryu==4.33
```

### Step 3: Install NetworkX
```bash
pip install networkx
```

### Step 4: Install other dependencies Ryu needs
```bash
pip install netaddr
```

### Step 5: Verify installations
```bash
python -c "import eventlet; print(f'eventlet: {eventlet.__version__}')"
```

### Step 6: Verify Ryu
```bash
python -c "import ryu; print(f'ryu: {ryu.__version__}')"
```

### Step 7: Verify NetworkX
```bash
python -c "import networkx; print(f'networkx version OK')"
```

✓ All three should print without errors

---

## PHASE 5: Install Mininet and OpenVSwitch (Ubuntu terminal)

Keep virtual environment active!

### Step 1: Install Mininet
```bash
sudo apt-get install -y mininet
```

### Step 2: Install OpenVSwitch
```bash
sudo apt-get install -y openvswitch-switch openvswitch-common
```

### Step 3: Start OpenVSwitch service
```bash
sudo service openvswitch-switch start
```

### Step 4: Verify Mininet installation
```bash
sudo mn --version
```
✓ Should show: `mininet version 2.x.x`

---

## PHASE 6: Copy Project Files (Ubuntu terminal)

### Step 1: Copy files from Windows to Ubuntu
```bash
cd ~/adaptive_ecmp_project
cp /mnt/d/Melinia/adaptive_ecmp/*.py ./
cp -r /mnt/d/Melinia/adaptive_ecmp/ryu ./
```

### Step 2: Verify files were copied
```bash
ls -la
```
✓ You should see: `adaptive_ecmp.py`, `simple_topo.py`, `final_adaptive.py`, etc.

---

## PHASE 7: Verify Everything Works (Ubuntu terminal - venv active)

### Step 1: Check all imports work
```bash
python -c "import ryu, networkx, eventlet, mininet; print('All imports OK!')"
```

### Step 2: Check Ryu manager works
```bash
ryu-manager --help
```
✓ Should show help text for ryu-manager

### Step 3: Verify project files exist
```bash
ls -la ~/adaptive_ecmp_project/*.py | head -5
```

---

## PHASE 8: First Test Run (Ubuntu terminal)

### Terminal 1: Start the network (keep venv activated!)

```bash
cd ~/adaptive_ecmp_project
source aecmp_env/bin/activate
sudo -E python3 simple_topo.py
```

Wait for the prompt to show `mininet>` (this means the network started!)

### Terminal 2: Start the controller (NEW TERMINAL - activate venv first!)

```bash
cd ~/adaptive_ecmp_project
source aecmp_env/bin/activate
ryu-manager adaptive_ecmp.py
```

You'll see lots of messages. That's normal and good!

### Terminal 1: Run the test (type in the mininet> prompt)

```bash
mininet> pingall
```

✓ You should see output like: `received 100%` - SUCCESS!

---

## How to Stop (When done testing)

### Stop Mininet (in Terminal 1):
```bash
mininet> exit
```

### Stop Ryu Controller (in Terminal 2):
```bash
Press Ctrl+C
```

---

## QUICK REFERENCE: After Ubuntu Restarts

Every time you close and reopen Ubuntu, run these commands in order:

```bash
# 1. Navigate to project
cd ~/adaptive_ecmp_project

# 2. Activate virtual environment
source aecmp_env/bin/activate

# 3. Start OpenVSwitch service
sudo service openvswitch-switch start

# 4. You're ready! The venv is activated and services are running
```

---

## TROUBLESHOOTING

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: eventlet` | Activate venv: `source aecmp_env/bin/activate` |
| `command not found: ryu-manager` | Activate venv: `source aecmp_env/bin/activate` |
| `Python 3.10 not found` | Run: `sudo apt-get install -y python3.10 python3.10-venv` |
| `mininet: command not found` | Run: `sudo apt-get install -y mininet` |
| `Cannot connect to display` in mininet | Use the topology in code, don't use graphical display |
| `OpenVSwitch not running` | Run: `sudo service openvswitch-switch start` |
| `Permission denied` errors | Use `sudo` or activate venv with `source` |
| `ryu 4.34 metadata error` | Use `pip install ryu==4.33` instead - ryu 4.34 has corrupted PyPI metadata |

---

## Summary of What You're Installing

- **Python 3.10** - Programming language (specific version for compatibility)
- **Eventlet 3.1** - Lightweight networking library for Ryu
- **Ryu** - SDN controller framework
- **NetworkX** - Graph library for networks
- **Mininet** - Network emulator
- **OpenVSwitch** - Virtual switch software

All running in a **virtual environment** called `aecmp_env` to keep everything isolated and clean!

---

## Ready?

Start with PHASE 1 in PowerShell. Good luck! 🚀
