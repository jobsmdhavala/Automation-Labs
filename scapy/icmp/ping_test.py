from scapy.all import IP, ICMP, sr1

targets = ["192.168.0.101", "192.168.0.102"]

for ip in targets:
    print(f"\nSending ICMP packet to {ip}")

    packet = IP(dst=ip)/ICMP()

    reply = sr1(packet, timeout=2, verbose=0)

    if reply:
        print(f"Reply received from {ip}")
        print(reply.summary())
    else:
        print(f"No reply from {ip}")