from scapy.all import ARP, Ether, srp

# Define the subnet to scan
target_subnet = "192.168.0.0/24"

# Broadcast ARP requests
arp_request = ARP(pdst=target_subnet)
broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
arp_packet = broadcast / arp_request

print(f"Scanning subnet {target_subnet}...")

answered_list = srp(arp_packet, timeout=2, verbose=1)[0]

for sent, received in answered_list:
    print(f"IP: {received.psrc}, MAC: {received.hwsrc}")