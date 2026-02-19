# Adaptive ECMP - Complete Setup and Execution Guide

## Prerequisites Check

### Requirements
- Python 3.7+
- Linux or macOS (Mininet requires Linux/Unix)
- ~2GB RAM for Mininet
- Administrator/sudo access

### Windows Users Note
Windows is NOT directly supported by Mininet. Options:
1. Use WSL2 (Windows Subsystem for Linux)
2. Use VirtualBox with Ubuntu
3. Use Docker + Mininet container

---

## Part 1: Environment Setup

### 1.1 Install on Ubuntu/Linux (Recommended)

#### Step 1: Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### Step 2: Install Dependencies
```bash
sudo apt-get install -y \
    python3 \
    python3-pip \
    git \
    mininet \
    openvswitch-switch \
    openvswitch-testcontroller
```

#### Step 3: Install Python Packages
```bash
pip3 install ryu networkx
```

#### Step 4: Verify Installation
```bash
# Check Mininet
sudo mn --version

# Check Ryu
ryu --version

# Check Python packages
python3 -c "import ryu, networkx; print('All packages OK')"
```

### 1.2 Install on WSL2 / Ubuntu VM

```bash
# Same as 1.1, but may need:
sudo service openvswitch-switch start

# Verify OVS running
sudo ovs-vsctl show
```

---

## Part 2: Project Structure Understanding

### 2.1 Key Files

```
adaptive_ecmp/
├── PROJECT_ANALYSIS.md          # Project overview ✓
├── IMPLEMENTATION_DETAILS.md    # Deep dive into code ✓
│
├── adaptive_ecmp.py             # Core adaptive ECMP controller
├── final_adaptive.py            # Enhanced version with groups
├── controller_in_loop_ecmp.py   # Alternative approach
├── traditional_ecmp.py          # Baseline implementation
├── dynamic_ecmp.py              # Experimental
│
├── simple_topo.py               # Spine-Leaf topology
├── git_topo.py                  # Alternative topology
├── graph.py                     # Topology utilities
│
├── bandwidth_monitor.py         # Monitoring utilities
└── ryu/                         # Custom Ryu modules (empty)
```

### 2.2 Implementation Selection

For **first run**, use:
- **Topology**: `simple_topo.py` (most tested)
- **Controller**: `adaptive_ecmp.py` (cleaner code)
- **Comparison**: `traditional_ecmp.py` (baseline)

For **advanced testing**, use:
- **Controller**: `final_adaptive.py` (most features)

---

## Part 3: Running Adaptive ECMP

### 3.1 Terminal Setup

You'll need 3 terminals:
1. **Terminal 1**: Topology
2. **Terminal 2**: Ryu Controller
3. **Terminal 3**: Mininet CLI / Testing

### 3.2 Terminal 1: Start Topology

```bash
cd /d/Melinia/adaptive_ecmp

# With default controller (don't kill this process)
sudo python3 simple_topo.py

# Expected output:
# *** Starting network
# *** Configuring hosts
# *** Starting controller
# *** Starting 6 switches
# *** Starting 4 hosts
# *** Starting CLI
```

**Don't proceed until you see `mininet>` prompt!**

### 3.3 Terminal 2: Start Ryu Controller

```bash
# New terminal (keep Terminal 1 running)
cd /d/Melinia/adaptive_ecmp

# Start adaptive ECMP controller
ryu-manager adaptive_ecmp.py

# Expected output:
# INFO:ryu.base.app_manager:loading app adaptive_ecmp.py
# INFO:ryu.base.app_manager:instantiating app adaptive_ecmp.py
# [BOOT] Default FLOOD rule installed on switch 1
# [BOOT] Default FLOOD rule installed on switch 2
# ...
# [TOPO] Detected switches: [1, 2, 3, 4]
# [TOPO] Link added: 1 -> 2 via port 1
# ...
```

**Keep this running!**

### 3.4 Terminal 3: Run Tests

```bash
# New terminal (keep 1 & 2 running)
# Type these commands directly in mininet CLI from Terminal 1

# Basic connectivity test
mininet> pingall

# Expected: All hosts can ping each other

# Single ping test
mininet> h1 ping h4

# Expected: Successful ping responses

# Bandwidth test
mininet> iperf h1 h4

# Expected: Shows throughput, RTT stats
```

---

## Part 4: Detailed Test Scenarios

### 4.1 Test 1: Basic Connectivity

**Goal**: Verify adaptive ECMP can handle basic traffic

**Commands**:
```bash
mininet> h1 ping -c 4 h2
mininet> h1 ping -c 4 h3
mininet> h1 ping -c 4 h4
mininet> pingall
```

**Expected Result**:
- All pings succeed
- No packet loss
- RTT: ~1-5ms (depends on system)

**What happens**:
1. Ping from h1 → ICMP packet created
2. Switch 513 receives (no MAC table entry)
3. Controller computes path to h3's switch (514)
4. Adaptive decision: Selects least-used spine link
5. Flow rule installed, packet forwarded
6. Reply packet learns MAC at 514
7. Subsequent pings hit flow rule (fast)

---

### 4.2 Test 2: Single Flow Throughput

**Goal**: Measure throughput on single flow

**Commands**:
```bash
# Terminal 3 (Mininet)
mininet> h4 iperf -s &  # Start server on h4
mininet> h1 iperf -c 10.0.0.4 -t 5  # Client sends for 5 seconds
```

**Expected Output**:
```
...
[  3]  0.0- 5.0 sec   X.XX MBytes   Y.YY Mbits/sec
```

**Expected Throughput**: ~2-3 Mbps (link bandwidth is 3 Mbps)

**Analysis**:
- Single flow uses single path
- No parallelism advantage yet
- Bottleneck: Single leaf-to-spine link

---

### 4.3 Test 3: Parallel Flows (Load Balancing)

**Goal**: Test adaptive distribution across multiple spines

**Commands**:
```bash
# Terminal 3 (Mininet)
mininet> h3 iperf -s &   # Server 1
mininet> h4 iperf -s &   # Server 2

# Terminal 3a (new pane/window)
mininet> h1 iperf -c 10.0.0.3 -t 10 &
mininet> h2 iperf -c 10.0.0.4 -t 10

# Expected: Both flows run simultaneously
```

**Expected Result**:
- Flow 1 (h1→h3): Uses one spine
- Flow 2 (h2→h4): Uses other spine
- Combined throughput: ~4-5 Mbps (2x3 - some overhead)

**Verification in Controller Logs**:
```
[PATH] Selected path from 513 to 514: [513, 1, 514] (load=100)
[PATH] Selected path from 513 to 514: [513, 2, 514] (load=50)
```

---

### 4.4 Test 4: Load Adaptation Over Time

**Goal**: Verify adaptive selection responds to changing load

**Commands**:
```bash
# Terminal 3 - Baseline
mininet> h1 iperf -c 10.0.0.4 -t 60

# Terminal 3a - Start after 15 seconds
mininet> (sleep 15; h2 iperf -c 10.0.0.3 -t 30) &

# Expected: 
# 0-15s:   h1→h4 on port X
# 15-45s:  h1→h4 on port Y, h2→h3 on port X (adaptive switch)
# 45-60s:  h1→h4 remains on port Y
```

**Controller Behavior**:
- First flow: Chooses least loaded link
- Second flow: Avoids first flow's path
- Result: Better load distribution

---

## Part 5: Comparing Implementations

### 5.1 Adaptive vs Traditional ECMP

#### Setup Comparison Test

**Terminal 2 Option A: Traditional ECMP**
```bash
ryu-manager traditional_ecmp.py
```

**Terminal 2 Option B: Adaptive ECMP**
```bash
ryu-manager adaptive_ecmp.py
```

**Test Scenario** (same for both):
```bash
# Terminal 3
mininet> h1 iperf -c 10.0.0.3 -t 5
mininet> h1 iperf -c 10.0.0.4 -t 5
mininet> h2 iperf -c 10.0.0.3 -t 5
mininet> h2 iperf -c 10.0.0.4 -t 5
```

**Expected Differences**:

| Metric | Traditional | Adaptive |
|--------|-------------|----------|
| Throughput consistency | Variable | Better |
| Load distribution | Hash-based (may be uneven) | Dynamic balancing |
| Adaptation time | None | 2-5 seconds |
| CPU overhead | Low | Low-moderate |

---

## Part 6: Monitoring and Debugging

### 6.1 View Controller Logs

```bash
# Real-time log watching (Terminal 2)
# Logs appear automatically as ryu-manager runs

# Key log types:
[BOOT]    # Switch initialization
[TOPO]    # Topology changes
[STATS]   # Statistics updates
[PATH]    # Path selection decisions
[FLOW]    # Flow rule installations
[PACKET_IN]  # Incoming packets
```

### 6.2 View Switch Rules

**In separate terminal**:
```bash
# View flows on switch
sudo ovs-ofctl dump-flows br1

# View groups on switch
sudo ovs-ofctl dump-groups br1

# Monitor in real-time
watch 'sudo ovs-ofctl dump-flows br1'
```

**Output Example**:
```
cookie=0x0, duration=3.145s, table=0, n_packets=42, n_bytes=3360,
  idle_age=1, priority=10,eth_dst=aa:bb:cc:dd:ee:01 
  actions=output:1

cookie=0x0, duration=2.103s, table=0, n_packets=85, n_bytes=6800,
  priority=0 actions=FLOOD
```

### 6.3 Real-time Traffic Monitoring

**In Mininet**:
```bash
mininet> h1 tcpdump -i h1-eth0 -n

# Shows all packets:
# 10.0.0.1 > 10.0.0.4: ICMP
# etc.
```

### 6.4 Mininet CLI Commands

```bash
mininet> help           # List all commands
mininet> nodes          # List all switches/hosts
mininet> dump           # Show configuration
mininet> links          # Show link status
mininet> net            # Show topology
mininet> sh <command>   # Run shell command
mininet> exit           # Stop Mininet
```

---

## Part 7: Troubleshooting

### Issue 1: Permission Denied

```bash
# Error: "sudo: mininet: command not found"
# Solution: Install mininet first
sudo apt-get install mininet

# Error: "Permission denied" for ovs-ofctl
# Solution: Use sudo
sudo ovs-ofctl dump-flows s1
```

### Issue 2: No Connectivity in Mininet

```bash
# Problem: Ping fails
# Debug:
mininet> h1 ip addr show      # Check IP
mininet> h1 arp -a            # Check ARP table
mininet> links                # Check link status

# If links show down:
# 1. Check controller is running
# 2. Restart controller (Ctrl-C in Terminal 2, re-run)
# 3. Restart Mininet (Ctrl-C in Terminal 1)
```

### Issue 3: High Controller CPU Usage

```bash
# Problem: ryu-manager using 100% CPU
# Causes:
# - Too many PacketIn events
# - Stats collection too frequent

# Temporary fix: Restart controller
# Permanent fix: Increase hard_timeout in code
# In adaptive_ecmp.py:
hard_timeout = 30  # Flows don't expire as quickly
```

### Issue 4: Stats Not Updating

```bash
# Problem: Adaptive selection always picks port 1
# Debug:
# Add logging in _port_stats_reply_handler():
self.logger.info("Stats: port1=%d, port2=%d", 
                 self.port_stats.get(dpid, {}).get(1, 0),
                 self.port_stats.get(dpid, {}).get(2, 0))

# If zeros: Stats collection not running
# Check: Is monitoring thread active?
# Check: ryu-manager logs for errors
```

---

## Part 8: Performance Benchmarking

### 8.1 Benchmark Script

Create `benchmark.sh`:
```bash
#!/bin/bash
# In Mininet CLI

echo "=== Test 1: Single Flow ==="
h1 iperf -c 10.0.0.4 -t 5

echo "=== Test 2: Two Parallel Flows ==="
h1 iperf -c 10.0.0.3 -t 5 &
h2 iperf -c 10.0.0.4 -t 5

echo "=== Test 3: All Hosts ==="
iperf_server &
h1 iperf -c 10.0.0.3 -t 5 &
h2 iperf -c 10.0.0.4 -t 5 &
h3 iperf -c 10.0.0.1 -t 5

echo "=== Done ==="
```

### 8.2 Metrics to Track

```
For each test:
1. Throughput (Mbps)
2. Packet loss (%)
3. Latency (ms)
4. Jitter (ms)
5. Controller CPU (%)
```

### 8.3 Expected Results

| Test | Throughput | Loss | Latency |
|------|-----------|------|---------|
| Single flow | 2.8 Mbps | 0% | 2-3 ms |
| Two parallel | 5.5 Mbps | 0% | 2-3 ms |
| All hosts | 3.5 Mbps | <1% | 2-4 ms |

---

## Part 9: Code Modification Examples

### 9.1 Increase Monitoring Frequency

**File**: `adaptive_ecmp.py`

**Change**:
```python
# Line ~16
STATS_INTERVAL = 2  # Changed from 2 to 1

# ==> 

STATS_INTERVAL = 1  # More frequent monitoring
```

**Effect**: Faster adaptation to link congestion (trade-off: higher CPU)

### 9.2 Change Path Selection Metric

**File**: `adaptive_ecmp.py`

**Current** (line ~80):
```python
# Uses TX bytes (cumulative)
load = sum(...tx_bytes...)
```

**Alternative** (use recent packets):
```python
# Use TX packets instead
load = sum(...tx_packets...)
```

**Effect**: Faster response to small packets, slower response to large objects

### 9.3 Add Threshold-Based Selection

**File**: `adaptive_ecmp.py`

**Add method**:
```python
def _should_adapt(self, load_diff):
    THRESHOLD = 100  # Only adapt if difference > 100 bytes
    return abs(load_diff) > THRESHOLD
```

**Effect**: Reduce oscillation when paths have similar load

---

## Part 10: Complete Test Execution Checklist

- [ ] System requirements met (Python 3, Mininet, OVS)
- [ ] Project files accessible at `/d/Melinia/adaptive_ecmp/`
- [ ] Terminal 1: `sudo python3 simple_topo.py` shows `mininet>`
- [ ] Terminal 2: `ryu-manager adaptive_ecmp.py` shows controller logs
- [ ] Terminal 3: `mininet> pingall` shows all connectivity
- [ ] Basic ping test successful
- [ ] Single flow bandwidth test works
- [ ] Multiple parallel flows show load balancing
- [ ] Controller logs show path adaptation
- [ ] No error messages in any terminal
- [ ] Switch flow rules visible with `ovs-ofctl`

---

## Part 11: Next Steps After Basic Testing

### 11.1 Short Term (1-2 hours)
1. Run all 4 test scenarios
2. Compare with traditional ECMP
3. Analyze controller logs
4. Document findings

### 11.2 Medium Term (1-2 days)
1. Modify monitoring frequency
2. Implement threshold-based selection
3. Add link failure detection
4. Create comprehensive benchmark report

### 11.3 Long Term (1+ weeks)
1. Implement multi-tenant support
2. Add machine learning for prediction
3. Optimize control plane overhead
4. Test at scale (100+ hosts)

---

## Part 12: Quick Reference

### Start Everything (Copy-Paste)

**Terminal 1**:
```bash
cd /d/Melinia/adaptive_ecmp
sudo python3 simple_topo.py
```

**Terminal 2**:
```bash
cd /d/Melinia/adaptive_ecmp
ryu-manager adaptive_ecmp.py
```

**Terminal 3**:
```bash
# Inside mininet CLI (from Terminal 1)
mininet> pingall
mininet> h1 ping h4
mininet> h4 iperf -s &
mininet> h1 iperf -c 10.0.0.4 -t 5
```

### Stop Everything
```bash
# Terminal 1: Ctrl-C
# Terminal 2: Ctrl-C
# Terminal 3: mininet> exit
```

---

## Summary

You now have a complete guide to:
1. ✓ Set up the environment
2. ✓ Run adaptive ECMP
3. ✓ Test all scenarios
4. ✓ Debug issues
5. ✓ Compare with baselines
6. ✓ Benchmark performance
7. ✓ Modify code

Start with Part 3 to begin experimenting!

