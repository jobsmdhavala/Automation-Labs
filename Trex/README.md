# TRex Traffic Generator Setup with Proxmox + PNETLab + Automation VM

## Goal

Deploy and use Cisco TRex traffic generator inside the **Automation VM** so automation scripts can generate traffic toward devices running inside **PNETLab**.

Current topology:

- Proxmox Host
  - VM1 = PNETLab
    - CSR Router = `10.10.10.101`
    - R2 Router = `10.10.10.102`
    - Optional SONiC VS
  - VM2 = Automation VM
    - pyATS
    - Snappi
    - Scapy
    - pytest
    - ixia-c-traffic-engine
    - KENG controller
    - Future: TRex

---

# Why Install TRex in Automation VM?

Yes — this is the correct architecture.

## Recommended Design

| Component | Purpose |
|---|---|
| PNETLab VM | Network topology and virtual devices |
| Automation VM | Automation tools + traffic generators |
| TRex | Generates traffic from Automation VM toward lab devices |

This gives:

- Centralized automation
- Easier scripting
- Better reuse
- Easier CI/CD integration
- pyATS + TRex integration
- Future scalability

Your scripts in Automation VM will:

1. Connect to CSR / SONiC / routers
2. Configure interfaces/routes
3. Start TRex traffic
4. Validate counters/telemetry
5. Stop traffic
6. Generate reports

---

# Recommended Directory Structure

Create a new directory:

```bash
cd ~/Automation-Labs
mkdir trex
```

Recommended structure:

```bash
trex/
├── README.md
├── install/
│   ├── install_trex.sh
│   └── requirements.txt
├── configs/
│   ├── trex_cfg.yaml
│   └── device_inventory.yaml
├── scripts/
│   ├── simple_stateless.py
│   ├── bi_directional.py
│   ├── vlan_traffic.py
│   ├── imix_profile.py
│   └── pyats_trex_test.py
├── profiles/
│   ├── udp_profile.py
│   ├── tcp_profile.py
│   └── imix.py
├── captures/
├── logs/
└── notes/
```

---

# Network Architecture

## Logical Connectivity

```text
+--------------------------------------------------+
|                  Proxmox Host                    |
|                                                  |
|   +----------------+     +-------------------+   |
|   | PNETLab VM     |     | Automation VM     |   |
|   |                |     |                   |   |
|   | CSR            |     | pyATS             |   |
|   | SONIC VS       |<--->| TRex              |   |
|   | R2             |     | Scapy             |   |
|   |                |     | Snappi            |   |
|   +----------------+     +-------------------+   |
|                                                  |
+--------------------------------------------------+
```

---

# TRex Modes

TRex supports:

| Mode | Usage |
|---|---|
| Stateless (STL) | High scale traffic generation |
| Stateful (ASTF) | TCP/HTTP realistic flows |
| Emulation | BGP/ARP/DHCP emulation |

For lab learning:
- Start with **Stateless**
- Then move to ASTF

---

# System Requirements

## Recommended

| Resource | Value |
|---|---|
| vCPU | 4+ |
| RAM | 8 GB+ |
| NIC | vmxnet3 preferred |
| Ubuntu | 22.04 |

---

# Step 1 — Prepare Automation VM

Update packages:

```bash
sudo apt update
sudo apt install -y \
    build-essential \
    gcc \
    g++ \
    make \
    git \
    wget \
    net-tools \
    python3-pip \
    libnuma-dev \
    pciutils \
    ethtool
```

---

# Step 2 — Download TRex

Go to:

```bash
cd ~/Automation-Labs/trex
```

Download latest TRex:

```bash
wget https://trex-tgn.cisco.com/trex/release/latest
```

OR manually:

```bash
wget https://trex-tgn.cisco.com/trex/release/v3_03.tar.gz
```

Extract:

```bash
tar -xvf v3_03.tar.gz
mv v3_03 trex-core
```

Example:

```bash
cd trex-core
ls
```

You should see:

```text
t-rex-64
automation/
scripts/
```

---

# Step 3 — Install Python Client

TRex Python API:

```bash
cd ~/Automation-Labs/trex/trex-core/scripts
sudo ./trex-cfg
```

Install Python packages:

```bash
pip install zmq
pip install pyyaml
pip install scapy
pip install texttable
```

Install TRex Python API:

```bash
cd automation/trex_control_plane/interactive
pip install -e .
```

Verify:

```bash
python3
```

Inside Python:

```python
from trex.stl.api import *
```

No errors = success.

---

# Step 4 — Identify Interfaces

Check interfaces:

```bash
ip addr
```

Example:

```text
ens18  -> management
ens19  -> connected to CSR
ens20  -> connected to R2
```

You need:
- One interface toward CSR
- One toward R2
- Or bridge them through PNETLab cloud

---

# Step 5 — Configure PNETLab Connectivity

## Option A (Recommended)

Create Linux Bridge in Proxmox:

```text
vmbr10
```

Attach:
- Automation VM NIC
- PNETLab NIC

This allows L2 connectivity.

---

# Step 6 — Configure TRex

Create config:

```bash
mkdir -p ~/Automation-Labs/trex/configs
```

File:

```bash
vim ~/Automation-Labs/trex/configs/trex_cfg.yaml
```

Example:

```yaml
- version: 2
  interfaces:
    - "0"
    - "1"

  port_info:
      - ip: 10.10.10.10
        default_gw: 10.10.10.101

      - ip: 20.20.20.10
        default_gw: 20.20.20.1
```

---

# Step 7 — Start TRex

Run:

```bash
cd ~/Automation-Labs/trex/trex-core
sudo ./t-rex-64 -i
```

Expected:

```text
Starting  TRex...
```

Keep this terminal running.

---

# Step 8 — Verify Reachability

Ping CSR:

```bash
ping 10.10.10.101
```

Ping R2:

```bash
ping 10.10.10.102
```

---

# Step 9 — Simple Stateless Traffic Script

Create:

```bash
mkdir -p ~/Automation-Labs/trex/scripts
vim ~/Automation-Labs/trex/scripts/simple_stateless.py
```

Content:

```python
from trex.stl.api import *

client = STLClient()

try:
    client.connect()

    base_pkt = Ether()/IP(src="10.10.10.10", dst="10.10.10.101")/UDP(dport=12,sport=1025)

    pkt = STLPktBuilder(pkt=base_pkt)

    stream = STLStream(
        packet = pkt,
        mode = STLTXCont(pps=1000)
    )

    client.reset()

    client.add_streams(stream, ports=[0])

    client.start(ports=[0], duration=10)

    client.wait_on_traffic(ports=[0])

    stats = client.get_stats()

    print(stats)

finally:
    client.disconnect()
```

---

# Step 10 — Execute Script

Open another terminal:

```bash
cd ~/Automation-Labs/trex/scripts
python3 simple_stateless.py
```

Expected:
- Traffic generated
- Counters increase
- CSR receives packets

---

# Step 11 — Verify on CSR

On CSR:

```bash
show interfaces
show ip traffic
show arp
```

Optional packet capture:

```bash
monitor capture
```

---

# Step 12 — pyATS + TRex Integration

Future workflow:

```text
pyATS
  |
  +--> Configure Router
  +--> Configure VLAN/BGP/OSPF
  +--> Start TRex Traffic
  +--> Validate Counters
  +--> Stop Traffic
  +--> Generate Test Report
```

---

# Example pyATS + TRex Workflow

## pyATS testbed.yaml

```yaml
devices:
  csr:
    os: iosxe
    type: router
    connections:
      cli:
        protocol: ssh
        ip: 10.10.10.101
```

---

## pyATS Script

```python
from genie.testbed import load
from trex.stl.api import *

tb = load("testbed.yaml")

csr = tb.devices['csr']

csr.connect()

output = csr.execute("show ip int brief")

print(output)

client = STLClient()

client.connect()

print("Connected to TRex")

client.disconnect()

csr.disconnect()
```

---

# Using SONiC VS

You can connect TRex to SONiC VS.

Excellent for:
- ECMP testing
- ACL validation
- QoS
- Buffer testing
- VXLAN
- BGP scale testing

---

# Recommended Future Labs

## Beginner

- ICMP traffic
- UDP traffic
- VLAN tagged traffic
- Bidirectional traffic

## Intermediate

- IMIX profiles
- Flow statistics
- Latency testing
- Burst traffic

## Advanced

- BGP emulation
- Stateful HTTP traffic
- TRex ASTF mode
- pyATS automated validation
- SONiC scale testing

---

# Useful Commands

## Start TRex

```bash
sudo ./t-rex-64 -i
```

## Interactive Console

```bash
sudo ./trex-console
```

## Show Interfaces

```bash
ip addr
```

## Capture Traffic

```bash
sudo tcpdump -i ens19
```

---

# Common Issues

## Permission Error

Fix:

```bash
sudo setcap cap_net_raw,cap_net_admin=eip ./t-rex-64
```

---

## Interface Not Detected

Check:

```bash
ethtool -i ens19
```

---

## Cannot Ping Router

Verify:
- Proxmox bridge
- PNET cloud connection
- Interface IPs
- Linux firewall

---

# Suggested Next Enhancements

Add:
- pytest integration
- HTML reports
- Traffic profiles
- CI/CD
- Robot Framework
- Grafana dashboards
- Prometheus telemetry

---

# Final Recommended Architecture

```text
                +-------------------+
                |   Automation VM   |
                |-------------------|
                | pyATS             |
                | pytest            |
                | Scapy             |
                | Snappi            |
                | TRex              |
                +---------+---------+
                          |
                          |
                +---------+---------+
                |     PNETLab VM    |
                |-------------------|
                | CSR               |
                | SONiC VS          |
                | R2                |
                +-------------------+
```

---

# Learning Roadmap

## Phase 1
- Install TRex
- Send basic UDP packets
- Validate counters

## Phase 2
- VLAN traffic
- Multiple streams
- Traffic rates

## Phase 3
- pyATS integration
- Automated validations

## Phase 4
- SONiC testing
- QoS
- ECMP
- Scale

## Phase 5
- CI/CD pipelines
- Jenkins
- Robot
- Grafana

---

# References

TRex Official:
https://trex-tgn.cisco.com/

TRex Docs:
https://trex-tgn.cisco.com/trex/doc/index.html

pyATS:
https://developer.cisco.com/pyats/

SONiC:
https://sonic-net.github.io/SONiC/

---
