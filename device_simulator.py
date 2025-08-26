#!/usr/bin/env python3
# Device simulator for MQTT / AMQP / CoAP (NON mode + no_response to avoid "Un-Matched")
import os, json, time, random, argparse, hashlib
from datetime import datetime, UTC

import paho.mqtt.client as mqtt
import pika

# CoAPthon
from coapthon.client.helperclient import HelperClient
from coapthon.messages.request import Request
from coapthon import defines

def banner(name):
    p = os.path.abspath(__file__)
    try:
        sha = hashlib.sha1(open(p, "rb").read()).hexdigest()[:10]
    except Exception:
        sha = "unknown"
    print(f"\n=== {name} START ===")
    print(f"__file__: {p}")
    print(f"cwd     : {os.getcwd()}")
    print(f"mtime   : {time.ctime(os.path.getmtime(p))}")
    print(f"sha1    : {sha}\n")

# ------------ config ------------
MQTT_BROKER, MQTT_PORT, MQTT_TOPIC = "localhost", 1883, "miot/hospital/ward1"
AMQP_HOST, AMQP_PORT, AMQP_QUEUE = "localhost", 5672, "miot_test_queue"
COAP_HOST, COAP_PORT, COAP_RESOURCE = "localhost", 5683, "miot"   # server registers "miot/"

LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ------------ helpers -----------
def iso8601(ts: float) -> str:
    return datetime.fromtimestamp(ts, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def write_log(device_id: str, record: dict):
    path = os.path.join(LOG_DIR, f"{device_id}_log.json")
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")

def build_metrics(device_id: str, event_type: str) -> dict:
    if "ventilator" in device_id:
        return {"respiratory_rate": random.randint(10, 24),
                "tidal_volume": random.randint(300, 600),
                "spo2": random.randint(94, 100)}
    if "heart_monitor" in device_id:
        return {"heart_rate": random.randint(60, 100),
                "spo2": random.randint(95, 100)}
    if "infusion_pump" in device_id:
        return {"infusion_rate": round(random.uniform(0.5, 5.0), 2),
                "volume_remaining": random.randint(50, 500)}
    if "ekg" in device_id:
        return {"heart_rate": random.randint(55, 110),
                "qrs_duration": random.randint(80, 120),
                "qt_interval": random.randint(300, 450)}
    return {"metric": random.randint(1, 100)}

# ------------ class -------------
class DeviceSimulator:
    def __init__(self, device_id: str, protocol: str):
        self.device_id = device_id
        self.protocol = protocol.upper()
        self.mqtt = None
        self.amqp_conn = None
        self.amqp_ch = None
        self.coap = None

        if self.protocol == "MQTT":
            self.mqtt = mqtt.Client(client_id=self.device_id, clean_session=True, protocol=mqtt.MQTTv311)
            self.mqtt.connect(MQTT_BROKER, MQTT_PORT, 60)

        elif self.protocol == "AMQP":
            params = pika.ConnectionParameters(host=AMQP_HOST, port=AMQP_PORT)
            self.amqp_conn = pika.BlockingConnection(params)
            self.amqp_ch = self.amqp_conn.channel()
            self.amqp_ch.queue_declare(queue=AMQP_QUEUE, durable=False, exclusive=False, auto_delete=False)

        elif self.protocol == "COAP":
            self.coap = HelperClient(server=(COAP_HOST, COAP_PORT))

        else:
            raise ValueError(f"Unknown protocol '{self.protocol}'")

    def close(self):
        try:
            if self.mqtt: self.mqtt.disconnect()
        except: pass
        try:
            if self.amqp_conn: self.amqp_conn.close()
        except: pass
        try:
            if self.coap: self.coap.stop()
        except: pass

    def _send_coap_non(self, payload_str: str):
        # Build NON request + tell client not to expect a response (no_response=True)
        req = Request()
        req.destination = (COAP_HOST, COAP_PORT)
        req.code = defines.Codes.POST.number
        req.type = defines.Types['NON']                     # Non-confirmable
        req.uri_path = f"{COAP_RESOURCE}/"                  # exact resource key, no leading slash
        req.payload = payload_str
        req.content_type = defines.Content_types['application/json']

        # no_response=True prevents HelperClient from tracking a transaction to match
        self.coap.send_request(req, None, None, True)
        print(f"[{self.device_id}] COAP NON sent")

    def send_event(self, event_type: str, extra: dict | None = None):
        ts = time.time()
        record = {
            "timestamp": ts,
            "logged_at": iso8601(ts),
            "device_id": self.device_id,
            "event_type": event_type
        }
        record.update(build_metrics(self.device_id, event_type))
        if extra: record.update(extra)

        # Forensic trail first
        write_log(self.device_id, record)
        payload = json.dumps(record)

        if self.protocol == "MQTT":
            self.mqtt.publish(MQTT_TOPIC, payload)
        elif self.protocol == "AMQP":
            self.amqp_ch.basic_publish(exchange="", routing_key=AMQP_QUEUE, body=payload)
        elif self.protocol == "COAP":
            self._send_coap_non(payload)

        print(f"[{self.device_id}] Event sent ({event_type})")

    # scenarios
    def simulate_normal(self): self.send_event("normal")
    def simulate_log_tampering(self): self.send_event("log_tampering")
    def simulate_unauthorized_access(self):
        self.send_event("unauthorized_access", {
            "username": random.choice(["admin", "nurse", "tech"]),
            "result": random.choice(["success", "failed"]),
            "ip": f"192.168.1.{random.randint(2,254)}"
        })
    def simulate_file_deletion(self):
        self.send_event("file_deletion", {"filename": f"/tmp/test_{random.randint(1000,9999)}.log"})
    def simulate_flood(self, count=30, interval=0.01):
        for i in range(count):
            self.send_event("flood", {"seq": i})
            time.sleep(interval)

# ------------- main ------------
def main():
    banner("device_simulator")
    ap = argparse.ArgumentParser(description="MIoT Device Simulator")
    ap.add_argument("device_id")
    ap.add_argument("protocol", choices=["MQTT","AMQP","COAP"])
    ap.add_argument("--interval", type=float, default=1.0)
    args = ap.parse_args()

    sim = DeviceSimulator(args.device_id, args.protocol)
    try:
        # small demo loop
        schedule = [
            ("normal", 3),
            ("unauthorized_access", 1),
            ("file_deletion", 1),
            ("log_tampering", 1),
            ("flood", 1)
        ]
        for ev, reps in schedule:
            for _ in range(reps):
                if ev == "normal": sim.simulate_normal()
                elif ev == "unauthorized_access": sim.simulate_unauthorized_access()
                elif ev == "file_deletion": sim.simulate_file_deletion()
                elif ev == "log_tampering": sim.simulate_log_tampering()
                elif ev == "flood": sim.simulate_flood(count=20, interval=0.01)
                time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        sim.close()

if __name__ == "__main__":
    main()
