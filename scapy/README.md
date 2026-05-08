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

Unlike pyATS, which focuses on device automation and CLI/API validation, Scapy works at the packet level.

Scapy allows us to:
- Build raw Ethernet/IP/TCP/UDP/ICMP packets
- Send custom packets into the network
- Capture and analyze responses
- Simulate traffic flows
- Validate protocol behavior
- Learn networking deeply at packet level

---

# Lab Architecture

## Automation VM

| Component | Value |
|---|---|
| VM Name | madhu-labs |
| OS | Ubuntu 24.04 |
| IP Address | 192.168.0.34 |

This VM hosts:
- Python virtual environments
- Scapy
- pyATS
- Automation scripts
- Testbeds
- Future traffic generation frameworks

---

## PNETLab VM

| Component | Value |
|---|---|
| Platform | PNETLab 5.3.13 |
| Purpose | Network emulation |

Devices used:

| Device | IP Address | OS |
|---|---|---|
| CSR | 192.168.0.101 | IOS-XE |
| R2 | 192.168.0.102 | IOS |

---

# Scapy Directory Structure

Location:

```bash
~/Automation-Labs/scapy
```

Structure:

```bash
scapy/
├── README.md
├── arp/
├── bgp/
├── icmp/
└── vxlan/
```

---

# Why Scapy Is Important

Scapy helps understand networking internally.

Examples:

| Use Case | Description |
|---|---|
| ICMP Testing | Send ping packets manually |
| ARP Testing | Generate ARP requests/replies |
| TCP Testing | Create custom TCP handshakes |
| VXLAN | Build VXLAN encapsulated packets |
| Packet Sniffing | Capture live traffic |
| Traffic Injection | Inject custom packets |
| Protocol Learning | Understand headers and fields |
| Security Testing | Simulate attacks or malformed packets |

---

# Virtual Environment

We are reusing the existing Python virtual environment created earlier for pyATS.

Location:

```bash
~/Automation-Labs/env/pyats
```

Activate it:

```bash
source ~/Automation-Labs/env/pyats/bin/activate
```

Prompt changes to:

```bash
(pyats) ubuntu@madhu-labs:~$
```

---

# Install Scapy

## Step 1 — Activate Virtual Environment

```bash
source ~/Automation-Labs/env/pyats/bin/activate
```

---

## Step 2 — Install Scapy

```bash
pip install scapy
```

---

## Step 3 — Verify Installation

```bash
python3
```

Inside Python:

```python
from scapy.all import *
```

If no errors appear, installation is successful.

Exit Python:

```python
exit()
```

---

# First Scapy Test

## Goal

Send ICMP Echo Request (Ping) packets from Automation VM to devices inside PNETLab.

---

# ICMP Script

Create file:

```bash
~/Automation-Labs/scapy/icmp/ping_test.py
```

Content:

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

# Execute Script

```bash
source ~/Automation-Labs/env/pyats/bin/activate

cd ~/Automation-Labs/scapy/icmp

python3 ping_test.py
```

---

# Expected Output

Example:

```bash
Sending ICMP packet to 192.168.0.101
Reply received from 192.168.0.101

Sending ICMP packet to 192.168.0.102
Reply received from 192.168.0.102
```

---

# What We Learned

## pyATS

- Device-level automation
- CLI interaction
- Execute commands
- Parse outputs
- Validation and testing

## Scapy

- Packet-level networking
- Build custom packets
- Inject traffic
- Capture responses
- Protocol experimentation

Both tools complement each other.

---

# Future Scapy Labs

## ICMP

- Ping
- Flood
- TTL experiments

## ARP

- ARP request generation
- Gratuitous ARP
- ARP spoofing labs

## TCP/UDP

- TCP SYN packets
- Port scanning
- UDP testing

## VXLAN

- Build VXLAN headers
- Encapsulation testing

## Packet Sniffing

- Live packet capture
- Filters
- Protocol analysis

## Traffic Simulation

- Generate large traffic streams
- Simulate clients/servers

---

# Important Notes

## Run as Root (Recommended)

Some Scapy operations require root privileges.

Example:

```bash
sudo ~/Automation-Labs/env/pyats/bin/python3 ping_test.py
```

or:

```bash
sudo su
source ~/Automation-Labs/env/pyats/bin/activate
```

---

# Architecture Decision

We intentionally separated:

| VM | Purpose |
|---|---|
| PNETLab VM | Network emulation |
| Automation VM | Automation frameworks |

Benefits:

- Cleaner architecture
- Easier upgrades
- Better stability
- Independent tooling
- Reduced dependency conflicts

---

# References

## Official Scapy Website

https://scapy.net/

## Documentation

https://scapy.readthedocs.io/

## GitHub

https://github.com/secdev/scapy

---

# Summary

We successfully:

- Built Automation VM
- Connected to PNETLab devices
- Installed pyATS
- Automated Cisco routers
- Installed Scapy
- Sent custom ICMP packets
- Established reusable automation architecture

This environment will now be expanded for:
- pyATS
- Scapy
- pytest
- snappi
- IXIA-c
- SONiC
- SpyTest
- Containerlab
- Traffic injection frameworks

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

Unlike pyATS, which focuses on device automation and CLI/API validation, Scapy works at the packet level.

Scapy allows us to:
- Build raw Ethernet/IP/TCP/UDP/ICMP packets
- Send custom packets into the network
- Capture and analyze responses
- Simulate traffic flows
- Validate protocol behavior
- Learn networking deeply at packet level

---

# Lab Architecture

## Automation VM

| Component | Value |
|----------|-------|
| VM Name | madhu-labs |
| OS | Ubuntu 24.04 |
| IP Address | 192.168.0.34 |

This VM hosts:
- Python virtual environments
- Scapy
- pyATS
- Automation scripts
- Testbeds
- Future traffic generation frameworks

---

## PNETLab VM

| Component | Value |
|----------|-------|
| Platform | PNETLab 5.3.13 |
| Purpose | Network emulation |

Devices used:

| Device | IP Address | OS |
|--------|------------|----|
| CSR | 192.168.0.101 | IOS-XE |
| R2 | 192.168.0.102 | IOS |

---

# Scapy Directory Structure

Location:
```bash
~/Automation-Labs/scapy
```

Structure:
```
scapy/
├── README.md
├── arp/
├── bgp/
├── icmp/
└── vxlan/
```

---

# Why Scapy Is Important

Scapy helps understand networking internally at packet level.

| Use Case | Description |
|----------|-------------|
| ICMP Testing | Send ping packets manually |
| ARP Testing | Generate ARP requests/replies |
| TCP Testing | Create custom TCP handshakes |
| VXLAN | Build VXLAN encapsulated packets |
| Packet Sniffing | Capture live traffic |
| Traffic Injection | Inject custom packets |
| Protocol Learning | Understand headers and fields |
| Security Testing | Simulate attacks or malformed packets |

---

# Virtual Environment

We reuse the existing Python virtual environment created for pyATS.

Location:
```bash
~/Automation-Labs/env/pyats
```

Activate it:
```bash
source ~/Automation-Labs/env/pyats/bin/activate
```

Prompt:
```bash
(pyats) ubuntu@madhu-labs:~$
```

---

# Install Scapy

## Step 1: Activate environment
```bash
source ~/Automation-Labs/env/pyats/bin/activate
```

## Step 2: Install Scapy
```bash
pip install scapy
```

## Step 3: Verify
```bash
python3 -c "from scapy.all import *; print('Scapy OK')"
```

---

# First Scapy Test (ICMP Ping)

## Goal
Send ICMP packets from Automation VM to PNETLab devices.

Targets:
- CSR → 192.168.0.101
- R2 → 192.168.0.102

---

## Script Location
```bash
~/Automation-Labs/scapy/icmp/ping_test.py
```

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

## If Permission Error Occurs

Scapy requires raw socket access.

Run with sudo + env python:

```bash
sudo ~/Automation-Labs/env/pyats/bin/python3 ping_test.py
```

OR recommended:

```bash
sudo -E python3 ping_test.py
```

---

## Working Fix (Best Practice)

If running inside venv:

```bash
sudo -E $(which python3) ping_test.py
```

---

# What We Learned

## pyATS vs Scapy

| Tool | Layer |
|------|------|
| pyATS | Device / CLI automation |
| Scapy | Packet level manipulation |

---

# Key Observations

- Raw packet injection requires root privileges
- Virtual env does NOT include system permissions
- Scapy works best with sudo + correct python path

---

# Architecture Decision

| VM | Role |
|----|------|
| PNETLab VM | Network devices |
| Automation VM | Python + automation frameworks |

Benefits:
- Clean separation
- Easy debugging
- Scalable lab design

---

# Future Scapy Labs

## ICMP
- Ping flood
- TTL manipulation

## ARP
- ARP spoofing
- Gratuitous ARP

## TCP/UDP
- SYN scan
- Port probing

## VXLAN
- Encapsulation testing

## Sniffing
- Live packet capture
- Filtering

---

# Troubleshooting Notes

### Issue: PermissionError
Cause: raw sockets require root

Fix:
```bash
sudo python3 script.py
```

---

### Issue: ModuleNotFoundError
Cause: sudo ignores venv

Fix:
```bash
sudo -E python3 script.py
```

---

# Summary

We successfully:
- Built Scapy lab structure
- Installed Scapy in Automation VM
- Connected to PNETLab devices
- Sent ICMP packets using custom scripts
- Understood packet-level automation

This lab is foundation for:
- Traffic generation
- Security testing
- Protocol validation
- Advanced automation frameworks
---
