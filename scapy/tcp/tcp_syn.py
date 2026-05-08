from scapy.all import IP, TCP, sr1

target = "192.168.0.101"
port = 22

print(f"\nSending TCP SYN to {target}:{port}")

packet = IP(dst=target)/TCP(dport=port, flags="S")

reply = sr1(packet, timeout=2, verbose=0)

if reply:
    reply.show()
else:
    print("No response")