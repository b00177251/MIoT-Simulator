import os, json, time, random, glob

def tamper_log(filename):
    if os.path.exists(filename):
        with open(filename, "r+") as f:
            lines = f.readlines()
            if lines:
                idx = random.randint(0, len(lines)-1)
                event = json.loads(lines[idx])
                event["heart_rate"], event["spo2"], event["event_type"] = 0, 0, "tampered"
                lines[idx] = json.dumps(event) + "\n"
                f.seek(0); f.truncate(); f.writelines(lines)
                print(f"Tampered {filename} line {idx}")
    else: print(f"{filename} not found.")

def delete_log(filename):
    if os.path.exists(filename):
        os.remove(filename)
        print(f"Deleted {filename}")

for fname in glob.glob('./logs/*_log.json'):
    tamper_log(fname)
    time.sleep(1)
    delete_log(fname)

