import os
import json
import pandas as pd

LOG_DIR = './logs'
PHASE_MAP = {
    "normal": ["identification", "collection"],
    "unauthorized_access": ["identification", "analysis", "reporting"],
    "log_tampering": ["preservation", "integrity", "analysis"],
    "file_deletion": ["preservation", "chain_of_custody", "completeness"],
    "tampered": ["preservation", "integrity"],    # (for events with _type tampered)
    "flood": ["identification", "reporting"],
}
def aggregate_logs():
    events = []
    for fname in os.listdir(LOG_DIR):
        if fname.endswith("_log.json"):
            with open(os.path.join(LOG_DIR, fname), "r") as f:
                for line in f:
                    try:
                        event = json.loads(line)
                        event["source_file"] = fname
                        event_type = event.get("event_type", "unknown")
                        event["phases_tested"] = PHASE_MAP.get(event_type, ["unknown"])
                        events.append(event)
                    except Exception:
                        continue
    return events

events = aggregate_logs()
df = pd.DataFrame(events)
df = df.explode("phases_tested")
phase_summary = pd.crosstab(df['event_type'], df['phases_tested'])
print("\nEvent Type x Forensic Phase Coverage:\n")
print(phase_summary)
phase_summary.to_csv("phase_event_summary.csv")
scorecard = pd.crosstab([df['device_id'],df['event_type']], df['phases_tested'])
print("\nDevice+Event x Phase Scorecard:\n")
print(scorecard)
scorecard.to_csv("device_event_phase_scorecard.csv")

