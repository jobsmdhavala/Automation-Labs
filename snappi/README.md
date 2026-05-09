# 🚀 Ixia-c & PNETLab Automation: The Complete Guide

This document covers the end-to-end setup of Ixia-c traffic generation into a PNETLab environment using a dedicated interface and the modern Keng Controller.

---

## 🏗️ Architecture & Network Mapping

To ensure high performance and stability, we use a dedicated Proxmox bridge (`vmbr2`) to isolate traffic from management tasks.


| Component | Detail | Mapping |
| :--- | :--- | :--- |
| **Hypervisor** | Proxmox | Hosts VM 117 (PNETLab) and VM 118 (Automation) |
| **Traffic Bridge** | `vmbr2` | Isolated virtual road for data packets |
| **Automation VM (118)** | `ens20` | Dedicated Ixia-c Traffic Engine Port |
| **PNETLab VM (117)** | `Cloud1` | Entry point for traffic into the Lab |
| **Traffic Subnet** | `10.10.10.0/24` | Isolated subnet (CSR IP: `10.10.10.101`) |

---

## 🍕 How it Works: The "Pizza Delivery" Analogy

If you find the connection between Docker, Proxmox, and PNETLab confusing, think of it like this:

1.  **The Script (The Customer):** You run the Python script to place an "Order." You specify 1,000 packets for address `10.10.10.101`.
2.  **Keng Controller (The Manager):** Receives the order via HTTPS. He checks the paperwork and tells the Chef what to cook.
3.  **Ixia-c Engine (The Chef):** A Docker container that physically "cooks" (generates) the packets and pushes them out the door (**`ens20`**).
4.  **vmbr2 Bridge (The Private Road):** A dedicated lane that carries the packets from the Automation VM straight to PNETLab without getting stuck in management traffic jams.
5.  **Cloud1 (The Front Door):** The entrance to your PNETLab topology. It catches the packets and hands them to the CSR Router.
6.  **CSR Device (The Receiver):** The final destination that accepts the packets and increases its "Input Counter."

---

## 🛠️ The Working "Keng" Script (`basic_test.py`)

This script is compatible with **Snappi 1.x** and the **Keng Controller**.

```python
import snappi
import time

# 1. Connect to Controller (The Manager)
api = snappi.api(location="https://localhost:8443", verify=False)
config = api.config()

# 2. Define Port (Use Network Location of the Engine)
port = config.ports.port(name="p1", location="localhost:5555")[-1]

# 3. Define Flow & Enable Stats
flow = config.flows.flow(name="f1")[-1]
flow.tx_rx.port.tx_name = port.name
flow.metrics.enable = True  

# 4. Headers (Targeting CSR on dedicated subnet)
eth, ip, udp = flow.packet.ethernet().ipv4().udp()
eth.src.value = "bc:24:11:fe:5f:f7" # ens20 MAC
ip.src.value = "10.10.10.34"
ip.dst.value = "10.10.10.101"

# 5. Traffic Properties
flow.size.fixed = 128
flow.rate.pps = 100
flow.duration.fixed_packets.packets = 1000

# 6. Push and Start
api.set_config(config)
cs = api.control_state()
cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
api.set_control_state(cs)

print("Traffic active! Monitoring metrics...")
time.sleep(5)

res = api.get_metrics(api.metrics_request(flow=api.flow_metrics_request(flow_names=[flow.name])))
for m in res.flow_metrics:
    print(f"Flow: {m.name} | Frames TX: {m.frames_tx} | Status: {m.transmit}")
```

---

## ⚠️ Migration & Troubleshooting (Snappi 0.x vs 1.x)

If your older scripts are failing with `AttributeError` or `404`, follow these rules for the **Keng Controller**:

1.  **The `[-1]` Rule:** Always add `[-1]` when creating ports or flows (e.g., `config.flows.flow()[-1]`). In Snappi 1.x, these are lists, and you must select the specific object.
2.  **Unified Control:** `api.transmit_state()` no longer exists. Use `api.control_state()` and set `cs.traffic.flow_transmit.state = 'start'`.
3.  **Opt-in Metrics:** Stats are disabled by default to save CPU. You **must** set `flow.metrics.enable = True` in your config to see Tx/Rx counts.
4.  **Keng vs Ixia-c Controller:** Use the `keng-controller` Docker image for best compatibility with the latest Python `snappi` library.
5.  **Location Mapping:** In the script, `location` should be the network address (e.g., `localhost:5555`), NOT the driver name (`af_packet`).

---


# # Before Keng Controller (ignore)

# Snappi (OTG Python SDK) Lab

## What is Snappi?

:contentReference[oaicite:0]{index=0} is the official Python SDK for Open Traffic Generator (OTG).

It is used to control traffic generators like:

- :contentReference[oaicite:1]{index=1}
- Spirent (OTG compatible systems)
- Other OTG-compliant platforms

---

## Simple Mental Model

Think of it like this:

| Component | Role |
|---|---|
| Ixia-C | Engine (does packet forwarding) |
| OTG | Standard API specification |
| Snappi | Python client / SDK (your controller) |

---

## Architecture in Your Lab
Python (Snappi)
↓
OTG API (gRPC/HTTP)
↓
Ixia-C Controller (Docker)
↓
Ixia-C Traffic Engine
↓
ens18 interface (actual packets)


---

## Why Snappi instead of `requests`?

Earlier we used:

- `requests.post()`
- Manual JSON payloads
- Manual API endpoints

That works, but is NOT scalable.

### Problems with raw requests:

- Hard to remember endpoints (`/control/state`, `/config`)
- Manual JSON construction
- No validation
- Easy to make mistakes
- No autocomplete

---

## Snappi Advantages

| Feature | Benefit |
|---|---|
| Python objects | No raw JSON needed |
| Auto-completion | Faster development |
| Schema validation | Prevents wrong configs |
| Cleaner code | Production-grade automation |
| OTG-native | Designed specifically for Ixia-C |

---

## Install Snappi

Activate your environment:

```bash
source ~/Automation-Labs/env/pyats/bin/activate

Install SDK:

pip install snappi

Verify:

python3 -c "import snappi; print('Snappi installed')"
Prerequisite (Must be running)

Before running Snappi scripts:

Docker containers must be UP
sudo docker ps

Expected:

ixia-controller → Running
ixia-engine → Running with ens18
First Snappi Script (Basic Connection Test)
File:
~/Automation-Labs/otg/snappi/basic_test.py
Snappi Example Code
import snappi

# Connect to Ixia-C Controller
api = snappi.api(location="https://127.0.0.1:8443", verify=False)

# Create configuration object
config = api.config()

# Define a port (mapped to engine interface ens18)
port = config.ports.port(name="p1", location="virtual@af_packet")

# Push config to controller
api.set_config(config)

print("Configuration pushed successfully to Ixia-C")
What this script does
Step 1

Connects to:

https://127.0.0.1:8443
Step 2

Creates a config object in Python

Step 3

Defines a port:

p1 → ens18 (via engine mapping)
Step 4

Pushes config to Ixia-C controller

Next Snappi Script (Traffic Flow)
File:
~/Automation-Labs/otg/snappi/traffic_flow.py
Example Flow Script
import snappi

api = snappi.api(location="https://127.0.0.1:8443", verify=False)
config = api.config()

# Ports
p1 = config.ports.port(name="p1", location="virtual@af_packet")

# Traffic flow
flow = config.flows.flow(name="f1")
flow.tx_rx.port.tx_name = "p1"
flow.tx_rx.port.rx_name = "p1"

flow.rate.pps = 100
flow.size.fixed = 128

# Apply config
api.set_config(config)

# Start traffic
ts = api.transmit_state()
ts.state = ts.START
api.set_transmit_state(ts)

print("Traffic started using Snappi")
How Snappi Works Internally
Step 1: Python Layer

You write Python objects:

config.flows.flow(...)
Step 2: Snappi SDK

Converts Python → OTG schema

Step 3: API Call

Sends structured request to:

Ixia-C Controller
Step 4: Engine Execution

Traffic engine pushes packets via:

ens18
Snappi vs Requests (Your Lab View)
Feature	requests	Snappi
API style	Raw JSON	Python objects
Ease of use	Hard	Easy
Validation	None	Built-in
Debugging	Difficult	Easy
Production use	Rare	Standard
Common Issues
1. SSL error

Fix:

verify=False
2. Connection refused

Check:

docker ps
3. Engine not running

Ensure:

ARG_IFACE_LIST="virtual@af_packet,ens18"
Recommended Learning Path
Option A (Best Path)
requests → Snappi → pytest integration → full OTG framework
Option B
Snappi only → fast production automation
Option C
Hybrid model:
- Snappi for config
- Scapy for packet validation
- pyATS for device verification
Integration in Your Lab
Tool	Purpose
pyATS	Device CLI validation
Scapy	Packet-level testing
Snappi	Traffic generation (OTG)
Final Summary
Snappi is the official Python SDK for OTG
It simplifies interaction with Ixia-C
Removes need for raw JSON + requests
Enables scalable traffic automation
Works directly with your Docker-based lab
Next Step Suggestions

If you continue this lab, next logical steps are:

1. Snappi + pyATS integration

Validate traffic from router CLI

2. Snappi + Scapy comparison

Generate traffic both ways and compare packets

3. Build framework
/otg/snappi/
/otg/scenarios/
/otg/results/