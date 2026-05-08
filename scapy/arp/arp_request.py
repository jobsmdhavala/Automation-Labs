from scapy.all import ARP, Ether, srp

target_ip = "192.168.0.101/24"

print(f"\nSending ARP request for subnet {target_ip}")

arp = ARP(pdst=target_ip)
ether = Ether(dst="ff:ff:ff:ff:ff:ff")

packet = ether/arp

result = srp(packet, timeout=2, verbose=0)[0]

for sent, received in result:
    print(f"IP: {received.psrc} | MAC: {received.hwsrc}")