"""
Hybrid pyATS + Scapy ARP Lab

Steps:
1. Connect to PNETLab devices via pyATS.
2. Validate interface states.
3. Perform ARP scan using Scapy.
4. Sniff ARP packets for live updates.
5. Print combined results.
"""

from genie.testbed import load
from scapy.all import ARP, Ether, srp, sniff
import threading
import time

# ------------------------
# Step 1: Load pyATS Testbed
# ------------------------
testbed_file = "/home/ubuntu/Automation-Labs/pyats/testbeds/testbed.yaml"
tb = load(testbed_file)

print("\n=== pyATS Device Validation ===")
for device in tb.devices.values():
    device.connect()
    print(f"\nDevice: {device.name}")
    output = device.execute("show ip interface brief")
    print(output)
    device.disconnect()

# ------------------------
# Step 2: Scapy ARP Scan
# ------------------------
subnet = "192.168.0.0/24"
print(f"\n=== Scapy ARP Scan on {subnet} ===")
arp_req = ARP(pdst=subnet)
broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
arp_packet = broadcast / arp_req

answered_list = srp(arp_packet, timeout=2, verbose=1)[0]

for sent, received in answered_list:
    print(f"IP: {received.psrc}  MAC: {received.hwsrc}")

# ------------------------
# Step 3: Sniff ARP Packets
# ------------------------
print("\n=== Sniffing ARP packets for 10 seconds ===")
def arp_sniff_callback(pkt):
    if ARP in pkt and pkt[ARP].op in (1, 2):
        if pkt[ARP].op == 1:
            print(f"[Request] {pkt[ARP].psrc} is asking for {pkt[ARP].pdst}")
        elif pkt[ARP].op == 2:
            print(f"[Reply] {pkt[ARP].psrc} is at {pkt[ARP].hwsrc}")

# Run sniff in a separate thread to allow timeout
sniff_thread = threading.Thread(
    target=sniff,
    kwargs={
        "filter": "arp",
        "prn": arp_sniff_callback,
        "store": 0,
        "timeout": 10
    }
)
sniff_thread.start()
sniff_thread.join()

print("\n=== Hybrid pyATS + Scapy ARP Lab Complete ===")
