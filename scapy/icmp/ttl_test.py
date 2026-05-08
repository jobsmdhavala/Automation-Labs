from scapy.all import IP, ICMP, sr1

target = "192.168.0.101"

print(f"\nSending ICMP with TTL=1 to {target}")

packet = IP(dst=target, ttl=1)/ICMP()

reply = sr1(packet, timeout=2, verbose=0)

if reply:
    print("Reply received:")
    reply.show()
else:
    print("No reply (expected if TTL expires before destination)")