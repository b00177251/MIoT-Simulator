import os, json, csv
from collections import Counter

LOG_DIR = "./logs"
def aggregate_logs():
    events = []
    for fname in os.listdir(LOG_DIR):
        if fname.endswith("_log.json"):
            with open(os.path.join(LOG_DIR, fname)) as f:
                for line in f:
                    try:
                        e = json.loads(line); e['logfile'] = fname
                        events.append(e)
                    except: pass
    return events
def summarize(events):
    etype = Counter(e.get('event_type','unknown') for e in events)
    device = Counter(e.get('device_id','unknown') for e in events)
    return etype, device
def write_csv(events, outfile="aggregated_events_report.csv"):
    if not events: return
    fieldnames = sorted(set().union(*(e.keys() for e in events)))
    with open(outfile, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader(); writer.writerows(events)
    print(f"CSV written: {outfile}")

if __name__ == "__main__":
    events = aggregate_logs()
    print(f"Aggregated {len(events)} events.")
    etype, device = summarize(events)
    print("--- Event Types ---"); print(dict(etype))
    print("--- Devices ---"); print(dict(device))
    write_csv(events)

