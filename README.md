# MIoT Forensic Simulator & Evaluation Testbed

**Purpose:** End-to-end system for simulating, logging, aggregating, and evaluating MIoT device events and attacks for forensic framework benchmarking and hybridization research.

## Setup

### Dependencies
- Python 3.x
- pip install -r requirements.txt

### Required Servers/Brokers
- Mosquitto (MQTT), RabbitMQ (AMQP), and a CoAP server (`aiocoap` recommended, see install notes below!)

## Typical Steps

1. Start MQTT/AMQP/CoAP servers (`mosquitto`, `rabbitmq-server`, `python3 -m aiocoap.cli.server`).
2. Launch device fleet: `python3 orchestrator.py`
3. (Optional/advanced) Real file tampering: `python3 log_file_tamper.py`  
   Packet attacks: `python3 attack_packets.py`
4. Aggregate logs, phase mapping, and dashboard:  
   - `python3 aggregator.py`  
   - `python3 phase_mapper.py`  
   - `python3 phase_dashboard.py`  
   - Scoring: `python3 auto_scorer.py` (see event coverage)
   - Plots: `python3 visualize_report.py`
5. Review output:  
   - `logs/` for all device events  
   - `aggregated_events_report.csv`, `phase_event_summary.csv`, `device_event_phase_scorecard.csv`, and plots

_For details on each script, see code comments and docstrings!_

## Broker install (Debian/Ubuntu):
