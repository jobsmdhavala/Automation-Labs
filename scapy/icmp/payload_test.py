from scapy.all import IP, ICMP, sr1

target = "192.168.0.101"

payload = "HELLO_FROM_SCAPY_LAB"

print(f"\nSending ICMP payload to {target}")

packet = IP(dst=target)/ICMP()/payload

reply = sr1(packet, timeout=2, verbose=0)

if reply:
    print("Reply:")
    reply.show()
else:
    print("No response")