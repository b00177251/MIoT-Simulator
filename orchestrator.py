from subprocess import Popen
import time, csv

DEVICES = [
    ("miot_heart_monitor_001", "MQTT"),
    ("miot_infusion_pump_002", "AMQP"),
    ("miot_ventilator_003", "COAP"),
    ("miot_temp_sensor_004", "MQTT"),
    ("miot_ekg_005", "AMQP")
]
SCRIPT = "device_simulator.py"
def load_device_list():
    try:
        with open("configs/devices.csv") as csvfile:
            rdr = csv.reader(csvfile)
            return [(row[0], row[1]) for row in rdr if row]
    except: return DEVICES
if __name__ == "__main__":
    devlist = load_device_list()
    procs = []
    for devid, proto in devlist:
        print(f"Launching {devid} on {proto}")
        procs.append(Popen(["python3", SCRIPT, devid, proto]))
        time.sleep(2)
    try:
        while True: time.sleep(10)
    except KeyboardInterrupt:
        for p in procs: p.terminate()

