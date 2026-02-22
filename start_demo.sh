#!/bin/bash
# Master startup script for Adaptive ECMP with Dashboard
# Usage: bash start_demo.sh

echo "╔════════════════════════════════════════════════════╗"
echo "║  🚀 Adaptive ECMP - Hackathon Demo Launcher       ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Check if running on Linux/WSL
if ! grep -qi microsoft /proc/version 2>/dev/null && ! uname -a | grep -qi linux; then
    echo "❌ This script requires Linux/WSL"
    exit 1
fi

# Check if Mininet is installed
if ! command -v sudo mn &> /dev/null; then
    echo "⚠️  Warning: Mininet may not be installed"
    echo "   Run: sudo apt-get install mininet"
fi

# Check if Ryu is installed
if ! command -v ryu-manager &> /dev/null; then
    echo "⚠️  Warning: Ryu may not be installed"
    echo "   Run: pip3 install ryu --break-system-packages"
fi

PROJECT_DIR="$(pwd)"
cd "$PROJECT_DIR" || exit

# Create temporary directory for logs
mkdir -p logs

echo "📋 Prerequisites:"
echo "   ✓ Mininet installed"
echo "   ✓ Ryu installed"
echo "   ✓ OpenFlow switch running"
echo ""

# Function to print colored text
print_step() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📍 STEP $1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Step 1: Clean up
print_step "1: Cleanup (if needed)"
echo "Cleaning up previous Mininet/OVS state..."
sudo mn -c 2>/dev/null || true
sudo pkill -f simple_topo 2>/dev/null || true
sudo pkill -f ryu-manager 2>/dev/null || true
echo "✅ Cleaned up"

# Step 2: Start OVS
print_step "2: Start OpenFlow Switch"
echo "Starting OpenFlow switch..."
sudo service openvswitch-switch restart
sleep 2
sudo service openvswitch-switch status | grep -q running && echo "✅ OpenFlow running" || echo "⚠️  OpenFlow may not be running"

# Step 3: Option selection
print_step "3: Select Controller Type"
echo ""
echo "1️⃣  Adaptive ECMP (Recommended - better performance)"
echo "2️⃣  Traditional ECMP (Baseline for comparison)"
echo ""
read -p "Choose (1 or 2): " CONTROLLER_CHOICE

case $CONTROLLER_CHOICE in
    1)
        CONTROLLER="adaptive_ecmp.py"
        CONTROLLER_NAME="Adaptive ECMP"
        ;;
    2)
        CONTROLLER="traditional_ecmp.py"
        CONTROLLER_NAME="Traditional ECMP"
        ;;
    *)
        echo "Invalid choice, using Adaptive ECMP"
        CONTROLLER="adaptive_ecmp.py"
        CONTROLLER_NAME="Adaptive ECMP"
        ;;
esac

echo "✅ Selected: $CONTROLLER_NAME"

# Step 4: Start components
print_step "4: Starting Components"
echo ""
echo "This will open multiple terminals..."
echo "💡 Tip: Don't close terminals - they'll stay running"
echo ""

# Terminal 1: Topology
echo "Starting Terminal 1: Network Topology..."
gnome-terminal --title="ECMP - Mininet Topology" -- bash -c "
    cd '$PROJECT_DIR'
    echo '🔄 Starting Mininet topology...'
    sudo python3 simple_topo.py 2>&1 | tee logs/topology.log
    bash
" 2>/dev/null || \
xterm -title "ECMP - Mininet Topology" -e bash -c "
    cd '$PROJECT_DIR'
    echo '🔄 Starting Mininet topology...'
    sudo python3 simple_topo.py 2>&1 | tee logs/topology.log
    bash
" &

sleep 3

# Terminal 2: Ryu Controller
echo "Starting Terminal 2: Ryu Controller ($CONTROLLER_NAME)..."
gnome-terminal --title="ECMP - Ryu Controller" -- bash -c "
    cd '$PROJECT_DIR'
    echo '🎮 Starting Ryu controller...'
    ryu-manager $CONTROLLER 2>&1 | tee logs/controller.log
    bash
" 2>/dev/null || \
xterm -title "ECMP - Ryu Controller" -e bash -c "
    cd '$PROJECT_DIR'
    echo '🎮 Starting Ryu controller...'
    ryu-manager $CONTROLLER 2>&1 | tee logs/controller.log
    bash
" &

sleep 2

# Terminal 3: Dashboard
echo "Starting Terminal 3: Web Dashboard..."
gnome-terminal --title="ECMP - Dashboard" -- bash -c "
    cd '$PROJECT_DIR'
    echo '📊 Starting dashboard...'
    python3 dashboard.py 2>&1 | tee logs/dashboard.log
    bash
" 2>/dev/null || \
xterm -title "ECMP - Dashboard" -e bash -c "
    cd '$PROJECT_DIR'
    echo '📊 Starting dashboard...'
    python3 dashboard.py 2>&1 | tee logs/dashboard.log
    bash
" &

sleep 3

# Step 5: Open Browser
print_step "5: Open Dashboard"
echo "Opening web browser to dashboard..."
sleep 2

# Try different browsers
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5000 &
elif command -v firefox &> /dev/null; then
    firefox http://localhost:5000 &
elif command -v chromium-browser &> /dev/null; then
    chromium-browser http://localhost:5000 &
else
    echo "⚠️  Please open browser manually: http://localhost:5000"
fi

# Step 6: Ready
print_step "6: Ready to Demo!"
echo ""
echo "✅ All components started!"
echo ""
echo "🎯 NEXT STEPS:"
echo ""
echo "1️⃣  Go to Mininet terminal (Terminal 1)"
echo "2️⃣  Wait for 'mininet>' prompt"
echo "3️⃣  Open dashboard in browser: http://localhost:5000"
echo "4️⃣  Run tests in Mininet:"
echo ""
echo "   For single flow:"
echo "   mininet> h1 iperf -c 10.0.0.4 -t 5"
echo ""
echo "   For dual flows (the real test!):"
echo "   mininet> h1 iperf -c 10.0.0.4 -t 10 &"
echo "   mininet> h2 iperf -c 10.0.0.4 -t 10 &"
echo "   mininet> wait"
echo ""
echo "5️⃣  Watch the dashboard update in real-time!"
echo ""
echo "🎨 Dashboard: http://localhost:5000"
echo ""
echo "📊 To compare:"
echo "   Restart with different controller (step 3)"
echo "   Run same tests"
echo "   Compare metrics on dashboard"
echo ""
echo "🏆 Demo Tips:"
echo "   • Screenshot key moments"
echo "   • Focus on throughput difference"
echo "   • Show packet duplication (sign of multi-path)"
echo "   • Highlight 'paths used' metric"
echo ""
echo "❌ To stop everything:"
echo "   1. Close terminals or Ctrl+C"
echo "   2. Run: sudo mn -c"
echo ""

# Final check
echo ""
echo "⏳ Waiting for components to initialize (30 seconds)..."
sleep 30

# Check if services are running
echo ""
echo "🔍 System Status:"
pgrep -f simple_topo > /dev/null && echo "   ✅ Topology running" || echo "   ❌ Topology not found"
pgrep -f "ryu-manager" > /dev/null && echo "   ✅ Controller running" || echo "   ❌ Controller not found"
pgrep -f "dashboard.py" > /dev/null && echo "   ✅ Dashboard running" || echo "   ❌ Dashboard not found"

echo ""
echo "🌐 Access:"
echo "   Dashboard: http://localhost:5000"
echo "   Mininet:   Check Terminal 1"
echo "   Controller: Check Terminal 2"
echo ""
echo "✨ Happy demoing! 🎉"
