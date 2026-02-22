#!/bin/bash
# Automated comparison test and report generator

PROJECT_DIR=$(pwd)
REPORT_DIR="$PROJECT_DIR/comparison_reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$REPORT_DIR"

echo "╔════════════════════════════════════════════════════╗"
echo "║  📊 Adaptive vs Traditional ECMP Comparison      ║"
echo "║          Automated Test Report Generator          ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Pre-flight checks...${NC}"

# Check if Mininet is running
if ! pgrep -f "python3 simple_topo" > /dev/null; then
    echo -e "${RED}❌ Mininet not running!${NC}"
    echo "Start Mininet first: sudo python3 simple_topo.py"
    exit 1
fi
echo -e "${GREEN}✅ Mininet running${NC}"

# Check if controller is running
if ! pgrep -f "ryu-manager" > /dev/null; then
    echo -e "${RED}❌ Ryu controller not running!${NC}"
    echo "Start controller: ryu-manager adaptive_ecmp.py"
    exit 1
fi
echo -e "${GREEN}✅ Ryu controller running${NC}"

echo ""
echo -e "${BLUE}System ready. Starting tests...${NC}"
echo ""

# Test configuration
TEST_DURATION=15
PAUSE_BETWEEN=3

# Create report file
REPORT_FILE="$REPORT_DIR/comparison_${TIMESTAMP}.md"

cat > "$REPORT_FILE" << 'EOF'
# Adaptive ECMP vs Traditional ECMP - Comparison Report

## Metadata
- **Test Date**: $(date)
- **Duration**: 15 seconds per test
- **Controller**: Will be determined by test
- **Topology**: Spine-Leaf (4 switches, 4 hosts)

---

## Test Configuration

| Parameter | Value |
|-----------|-------|
| Test Duration | 15 seconds |
| Bandwidth Limit | Unlimited |
| Topology | simple_topo.py |
| Protocol | TCP (iperf) |

---

## Test Scenarios

### Scenario 1: Single Flow (Baseline)
**Command**: `h1 iperf -c 10.0.0.4 -t 15`

**Expected Result**:
- Both controllers should perform similarly
- Throughput: 4-5 Mbps

### Scenario 2: Dual Sequential Flows
**Command**: 
```
h1 iperf -c 10.0.0.4 -t 15
h2 iperf -c 10.0.0.4 -t 15 (after first completes)
```

**Expected Result**:
- Traditional: Lower throughput, possible congestion
- Adaptive: Better throughput, balanced paths

### Scenario 3: Parallel Flows (The Real Test!)
**Command**:
```
h1 iperf -c 10.0.0.4 -t 15 &
h2 iperf -c 10.0.0.4 -t 15 &
h2 iperf -c 10.0.0.3 -t 15 &
h3 iperf -c 10.0.0.4 -t 15 &
wait
```

**Expected Result**:
- This is where adaptive shines!
- Adaptive: Maintains high throughput
- Traditional: Severe congestion

---

## Results

### Adaptive ECMP Results
```
[Paste iperf output here]
```

### Traditional ECMP Results  
```
[Paste iperf output here]
```

---

## Analysis

- **Throughput Improvement**: X% better
- **Latency Impact**: X ms average
- **Path Utilization**: X paths used
- **Efficiency**: X% better

---

## Conclusion

Adaptive ECMP demonstrates superior performance in:
✅ Multi-flow scenarios
✅ Load balancing
✅ Path diversity
✅ Overall throughput

---

## Screenshots & Evidence

[Space for dashboard screenshots]

---

Generated: $(date)
EOF

echo "📝 Report file created: $REPORT_FILE"
echo ""

# Manual test instructions
echo "═══════════════════════════════════════════════════"
echo "📋 MANUAL TEST PROCEDURE"
echo "═══════════════════════════════════════════════════"
echo ""

# Go to mininet in screen/tmux or xterm
MININET_PID=$(pgrep -f "mininet>" | head -1)

if [ -z "$MININET_PID" ]; then
    echo -e "${YELLOW}⚠️  Mininet CLI not detected as interactive.${NC}"
    echo ""
    echo "Please open a third terminal and run tests manually in Mininet:"
    echo ""
else
    echo -e "${GREEN}✅ Mininet CLI detected${NC}"
    echo ""
fi

echo -e "${BLUE}Test 1: Single Flow${NC}"
echo "In Mininet CLI, run:"
echo -e "${YELLOW}  mininet> h1 iperf -c 10.0.0.4 -t ${TEST_DURATION}${NC}"
echo ""
read -p "Press Enter after Test 1 completes..."

echo ""
echo -e "${BLUE}Test 2: Dual Flows (Sequential)${NC}"
echo "In Mininet CLI, run:"
echo -e "${YELLOW}  mininet> h1 iperf -c 10.0.0.4 -t ${TEST_DURATION}${NC}"
echo -e "${YELLOW}  mininet> h2 iperf -c 10.0.0.4 -t ${TEST_DURATION}${NC}"
echo ""
read -p "Press Enter after Test 2 completes..."

echo ""
echo -e "${BLUE}Test 3: Parallel Flows (The Real Test!)${NC}"
echo "In Mininet CLI, run EACH command in SEPARATE windows:"
echo ""
echo -e "${YELLOW}  Window A: mininet> h1 iperf -c 10.0.0.4 -t ${TEST_DURATION}${NC}"
sleep 1
echo -e "${YELLOW}  Window B: mininet> h2 iperf -c 10.0.0.4 -t ${TEST_DURATION}${NC}"
sleep 1
echo -e "${YELLOW}  Window C: mininet> h1 iperf -c 10.0.0.3 -t ${TEST_DURATION}${NC}"
sleep 1
echo -e "${YELLOW}  Window D: mininet> h3 iperf -c 10.0.0.4 -t ${TEST_DURATION}${NC}"
echo ""
echo "💡 Or use xterm for each:"
echo -e "${YELLOW}  mininet> xterm h1 h2 h3${NC}"
echo "Then in each xterm:"
echo -e "${YELLOW}  # In h1: iperf -c 10.0.0.4 -t ${TEST_DURATION}${NC}"
echo -e "${YELLOW}  # In h2: iperf -c 10.0.0.4 -t ${TEST_DURATION}${NC}"
echo "etc."
echo ""
read -p "Press Enter after Test 3 completes..."

echo ""
echo "═══════════════════════════════════════════════════"
echo "📊 DASHBOARD MONITORING"
echo "═══════════════════════════════════════════════════"
echo ""
echo "🌐 Dashboard URL: http://localhost:5000"
echo ""
echo "Watch these metrics during tests:"
echo ""
echo -e "${BLUE}Comparison View:${NC}"
echo "  • Total Throughput comparison"
echo "  • Avg Latency comparison"  
echo "  • Packet Loss comparison"
echo "  • Paths Used (KEY: Adaptive > Traditional)"
echo ""
echo -e "${BLUE}Flow Details:${NC}"
echo "  • Adaptive: Flows should be balanced (green/4+ Mbps each)"
echo "  • Traditional: Some flows congested (red/2-3 Mbps)"
echo ""
echo "═══════════════════════════════════════════════════"
echo ""

# Generate summary
echo "📈 Quick Comparison Checklist:"
echo ""
echo "[ ] Verify Adaptive > Traditional throughput"
echo "[ ] Check Adaptive uses multiple paths (>1)"
echo "[ ] See Adaptive packet 'duplicates' (multi-path indicator)"
echo "[ ] Notice lower latency variance in Adaptive"
echo "[ ] Confirm balanced load distribution in Adaptive"
echo ""

# Open report
echo ""
echo -e "${GREEN}✅ Report generated:${NC}"
echo "   $REPORT_FILE"
echo ""
echo "📝 Tips for the report:"
echo "  1. Copy iperf output to report"
echo "  2. Screenshot dashboard metrics"
echo "  3. Calculate improvement percentages"
echo "  4. Add commentary about results"
echo ""

# Ask if user wants to open report
read -p "Open report in editor? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    nano "$REPORT_FILE" || vim "$REPORT_FILE" || cat "$REPORT_FILE"
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "🎉 Comparison test complete!"
echo "═══════════════════════════════════════════════════"
