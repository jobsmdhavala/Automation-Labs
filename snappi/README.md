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