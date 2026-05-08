from scapy.all import sniff, ARP

def arp_monitor_callback(pkt):
    if ARP in pkt and pkt[ARP].op in (1,2):
        if pkt[ARP].op == 1:
            print(f"ARP Request: {pkt[ARP].psrc} is asking for {pkt[ARP].pdst}")
        elif pkt[ARP].op == 2:
            print(f"ARP Reply: {pkt[ARP].psrc} is at {pkt[ARP].hwsrc}")

print("Sniffing ARP packets on network...")
sniff(filter="arp", prn=arp_monitor_callback, store=0)