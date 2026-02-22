# Install Ryu from GitHub Source (When pip3 Fails)

## Problem
`pip3 install ryu` gives an error? No problem! We'll install from GitHub source code instead.

---

## Step 1: Install Prerequisites for Building Ryu

```bash
sudo apt-get update
sudo apt-get install -y \
    git \
    python3-dev \
    python3-pip \
    python3-setuptools \
    gcc \
    libssl-dev \
    libffi-dev
```

---

## Step 2: Clone Ryu Repository from GitHub

```bash
cd ~
git clone https://github.com/osrg/ryu.git
cd ryu
```

---

## Step 3: Check Your Python Version

```bash
python3 --version
# Should be 3.7 or higher
```

---

## Step 4: Install Ryu from Source

### Option A: System-Wide Installation
```bash
cd ~/ryu
sudo pip3 install -e .
```

### Option B: User Installation (Recommended if sudo fails)
```bash
cd ~/ryu
pip3 install -e .
```

---

## Step 5: Verify Installation

```bash
# Check if Ryu is installed
ryu --version

# Test import in Python
python3 -c "import ryu; print('✓ Ryu successfully installed from source')"
```

---

## Step 6: If Still Having Issues - Install Dependencies Manually

```bash
cd ~/ryu

# Install all required dependencies
pip3 install netaddr
pip3 install oslo.config
pip3 install msgpack
pip3 install python-eventlet
pip3 install tinyrpc
pip3 install lxml
pip3 install six
pip3 install WebOb
pip3 install Routes
pip3 install PasteDeploy
pip3 install Werkzeug
pip3 install webtest
```

Then try again:
```bash
pip3 install -e .
```

---

## Step 7: Copy Ryu to Your Adaptive ECMP Project

This is optional but helpful:

```bash
# Copy ryu to your project folder
cp -r ~/ryu/ryu ~/adaptive_ecmp/ryu
```

---

## Step 8: Now Run Your Project

Go back to Terminal 2 and run:

```bash
cd ~/adaptive_ecmp
ryu-manager adaptive_ecmp.py
```

---

## If ryu-manager Command Not Found

Try running it directly with Python:

```bash
cd ~/adaptive_ecmp
python3 -m ryu.cmd.manager adaptive_ecmp.py
```

Or if that doesn't work:

```bash
cd ~/adaptive_ecmp
python3 -c "from ryu.cmd import manager; manager.main(['adaptive_ecmp.py'])"
```

---

## Common Errors & Solutions

### Error: "No module named 'ryu'"
```bash
# Make sure you're in the ryu directory
cd ~/ryu

# Install with pip3
pip3 install -e .

# Verify
python3 -c "import ryu; print(ryu.__version__)"
```

### Error: "gcc: command not found"
```bash
sudo apt-get install -y build-essential
```

### Error: "libssl-dev not found"
```bash
sudo apt-get install -y libssl-dev libffi-dev
```

### Error: "Permission denied"
```bash
# If using sudo fails, try user installation
cd ~/ryu
pip3 install --user -e .
```

---

## Check Ryu Installation Location

```bash
python3 -c "import ryu; print(ryu.__file__)"
```

This shows where Ryu is installed.

---

## Full Step-by-Step for Kali (Clean Install)

```bash
# 1. Update system
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install ALL dependencies
sudo apt-get install -y python3 python3-pip python3-dev git \
    gcc libssl-dev libffi-dev build-essential

# 3. Clone Ryu from GitHub
cd ~
git clone https://github.com/osrg/ryu.git
cd ryu

# 4. Install Ryu from source
pip3 install -e .

# 5. Verify
ryu --version
python3 -c "import ryu, networkx; print('✓ All good!')"

# 6. Go to your project
cd ~/adaptive_ecmp

# 7. Run!
sudo python3 simple_topo.py   # Terminal 1
ryu-manager adaptive_ecmp.py   # Terminal 2
```

---

## Success Check

```bash
# Should output version number
ryu --version

# Should output True
python3 -c "import ryu; print(True)"

# Should show ryu location
which ryu-manager
```

✓ If all three work, you're ready to go!
