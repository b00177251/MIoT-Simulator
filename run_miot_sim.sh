#!/bin/bash
# MIoT Simulator and Evaluation Automation Script

# === CONFIGURABLE PATHS ===
PROJECT_ROOT="$(cd "$(dirname "$0")"; pwd)"
LOGDIR="$PROJECT_ROOT/logs"

echo "=== MIoT Simulator Automated Run ==="
echo "Working dir: $PROJECT_ROOT"

# 1. Clean logs for reproducibility
echo "[Step 1] Cleaning old logs..."
rm -rf "$LOGDIR"
mkdir "$LOGDIR"

# 2. Start brokers/services (requires sudo privileges for system services)
echo "[Step 2] Starting brokers/services..."
sudo service mosquitto start
sudo service rabbitmq-server start
# CoAP server: leave running in separate terminal if using aiocoap ("python3 -m aiocoap.cli.server")
echo ">> Please ensure your CoAP server is running (in a separate terminal!)"

# 3. Orchestrate the simulator fleet (runs in the background)
echo "[Step 3] Starting orchestrator (device simulators)..."
python3 orchestrator.py &
ORCHESTRATOR_PID=$!
echo "Orchestrator PID: $ORCHESTRATOR_PID"
# Wait for simulators to finish (or replace with sleep for demo)
SIM_TIME=90   # Seconds to let simulators run (adjust if needed)
echo "   ...Simulating devices and attacks for $SIM_TIME seconds..."
sleep $SIM_TIME

# 4. (Optional) Advanced/log/packet attack plugins
# echo "[Step 4] Running file tampering and DoS attacks (optional)..."
# python3 log_file_tamper.py
# python3 attack_packets.py

# 5. Aggregate logs and generate reports
echo "[Step 5] Aggregating logs and building reports..."
python3 aggregator.py

# 6. Map events to forensic phases and create dashboards
python3 phase_mapper.py
python3 phase_dashboard.py

# 7. Visualize results (plots)
python3 visualize_report.py

# 8. Automatic scoring (if framework_detection_log.csv is filled)
if [ -f "framework_detection_log.csv" ]; then
    echo "[Step 8] Automatic framework scoring..."
    python3 auto_scorer.py
else
    echo "[Step 8] (Skipped) No framework_detection_log.csv found for scoring."
fi

echo "=== MIoT Simulation & Evaluation Run Complete ==="
echo "See logs/, aggregated_events_report.csv, phase_event_summary.csv, device_event_phase_scorecard.csv, events_per_device.png for results."
echo "Stop brokers with: sudo service mosquitto stop; sudo service rabbitmq-server stop"
echo "Kill orchestrator manually if needed: kill $ORCHESTRATOR_PID"
