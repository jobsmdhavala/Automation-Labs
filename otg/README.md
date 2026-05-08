# Ixia-c Traffic Generator Integration: Automation VM to PNETLab

This project documents the setup and automation of an Open Traffic Generator (OTG) environment using **Ixia-c** and the **Keng Controller** within a Proxmox environment, targeting nodes inside a **PNETLab** topology.

---

## 🏗️ Architecture Overview

The setup consists of three main layers:

1.  **Proxmox (Hypervisor):** Host for all Virtual Machines.
    *   **VM 117 (PNETLab):** Runs the network lab.
    *   **VM 118 (Automation-Labs):** Runs the Ixia-c Docker containers and Python scripts.
    *   **Network Bridge (`vmbr0`):** Acts as a virtual switch connecting both VMs on the `192.168.0.x` management network.

2.  **Automation VM (Docker Containers):**
    *   **Keng Controller:** The "Brain." It receives instructions from the Python script (via HTTP/JSON) and manages the traffic engines.
    *   **Ixia-c Traffic Engine:** The "Muscles." It binds to the physical interface (`ens18`) and generates the actual high-speed packets.

3.  **PNETLab Topology:**
    *   **Cloud0 (Management):** Bridged to Proxmox `vmbr0`.
    *   **Target Nodes:** CSR (192.168.0.101) and R2 (192.168.0.102) connected to Cloud0.

---

## 🛠️ Step-by-Step Implementation

### 1. Preparation of the Automation VM
We enabled **Promiscuous Mode** on the management interface so the Docker container could inject and sniff traffic without restriction.
```bash
sudo ip link set ens18 up
sudo ip link set ens18 promisc on
```

### 2. Deploying the Control Plane
Initially, we tried `ixia-c-controller`, but it resulted in `BAD_REQUEST` errors due to a version mismatch with the modern `snappi` library. We successfully switched to the **Keng Controller**.

```bash
# Start Keng Controller (Control Plane)
docker run -d --name=ixia-controller --net=host \
  ghcr.io/open-traffic-generator/keng-controller:latest --accept-eula

# Start Ixia-c Traffic Engine (Data Plane)
docker run -d --name=ixia-engine --net=host --privileged \
  -e ARG_IFACE_LIST="virtual@af_packet,ens18" \
  -e OPT_NO_HUGEPAGES="Yes" \
  ghcr.io/open-traffic-generator/ixia-c-traffic-engine:latest
```

### 3. The Automation Script
Using the **Snappi** Python library, we created a script to define the traffic flows.

**File:** `test_management.py`
```python
import snappi

# 1. Initialize API (Talking to Keng Controller)
api = snappi.api(location='https://localhost:8443', verify=False)
config = api.config()

# 2. Define Port (Mapped to our Traffic Engine)
p1 = config.ports.port(name='p1', location='localhost:5555')[-1]

# 3. Define Flow (Traffic to CSR Router)
f1 = config.flows.flow(name='f1')[-1]
f1.tx_rx.port.tx_name = p1.name

# 4. Define Packet Headers
eth, ip = f1.packet.ethernet().ipv4()
eth.src.value = "bc:24:11:b0:aa:80" # Automation VM MAC
ip.src.value = "192.168.0.34"      # Automation VM IP
ip.dst.value = "192.168.0.101"     # CSR IP in Lab

# 5. Set Rate & Duration
f1.size.fixed = 128
f1.duration.fixed_packets.packets = 1000
f1.rate.pps = 100

# 6. Push Config and Start Traffic
api.set_config(config)
cs = api.control_state()
cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
api.set_control_state(cs)

print("SUCCESS: Traffic Flowing to PNETLab.")
```

---

## 💡 How it works (The Simple Version)

Imagine you are ordering a pizza:

*   **Your Script:** This is **You**. You write down exactly what you want (1000 packets, UDP, Pepperoni) and send the order to the shop.
*   **Keng Controller:** This is the **Shop Manager**. He takes your order, checks if it's valid, and tells the chef what to do. He translates your Python code into a language the engine understands.
*   **Ixia-c Engine:** This is the **Chef**. He doesn't talk to you directly; he just listens to the manager. He starts cooking (generating packets) and throws them onto the "Road" (`ens18` interface).
*   **Proxmox Bridge (`vmbr0`):** This is the **Road**. It carries the pizza (packets) from the Automation VM's driveway to the PNETLab VM's front door.
*   **PNETLab Cloud0:** This is the **Front Door**. It receives the packets and passes them to the internal routers (CSR/R2) in your lab.

---

## ⚠️ Troubleshooting Recap
*   **BAD_REQUEST 500:** Fixed by upgrading to `keng-controller`.
*   **Wireshark "Pipe Magic":** Caused by SSH host key rejection on Windows. Fixed by trusting the PNETLab IP via PuTTY or using the HTML5 Web Capture.
*   **Interface Selection:** In PNETLab, you don't select the interface inside Wireshark; PNETLab handles the "pipe" automatically when you start the capture from the Web UI.

# 🚀 Ixia-c Dedicated Traffic Setup (Isolated Bridge)

This section documents the transition from the Management network (Cloud0) to a **Dedicated Traffic Interface** using an isolated Proxmox bridge (`vmbr2`). This ensures management stability and higher traffic performance.

---

## 🏗️ Topology & Network Mapping


| Component | Interface / Object | Details |
| :--- | :--- | :--- |
| **Proxmox Bridge** | `vmbr2` | Isolated virtual switch for Ixia traffic |
| **Automation VM (118)** | `ens20` | MAC: `bc:24:11:fe:5f:f7` |
| **PNETLab VM (117)** | `eth1` / `pnet1` | Mapped to **Cloud1** in Lab UI |
| **Traffic Subnet** | `10.10.10.0/24` | Isolated from 192.168.0.0/24 |

---

## 🛠️ Configuration Steps

### 1. Engine Redeployment
The Ixia-c Traffic Engine must be restarted to bind to the dedicated `ens20` interface instead of the management port.

```bash
# Remove the old engine instance
docker stop ixia-engine && docker rm ixia-engine

# Start the engine on the dedicated ens20 interface
docker run -d --name=ixia-engine --net=host --privileged \
  -e ARG_IFACE_LIST="virtual@af_packet,ens20" \
  -e OPT_NO_HUGEPAGES="Yes" \
  ghcr.io/open-traffic-generator/ixia-c-traffic-engine:latest
```

### 2. PNETLab Node Configuration
1. **Cloud Mapping:** Connect your **CSR** and **R2** nodes to **Cloud1** (which points to `pnet1` / `vmbr2`).
2. **IP Addressing:** Update your router interfaces to the new subnet:
   * **CSR (Gi1):** `10.10.10.101/24`
   * **R2 (Gi1):** `10.10.10.102/24`

### 3. Automation Script (`test_dedicated.py`)
This script targets the dedicated interface and the new subnet.

```python
import snappi

# Initialize API to Keng Controller
api = snappi.api(location='https://localhost:8443', verify=False)
config = api.config()

# Define Port (Engine is on localhost:5555)
p1 = config.ports.port(name='p1', location='localhost:5555')[-1]

# Define Flow with Metrics Enabled
f1 = config.flows.flow(name='Dedicated-Traffic')[-1]
f1.tx_rx.port.tx_name = p1.name
f1.metrics.enable = True 

# Packet Headers (Subnet 10.10.10.x)
eth, ip = f1.packet.ethernet().ipv4()
eth.src.value = "bc:24:11:fe:5f:f7" # ens20 MAC
ip.src.value = "10.10.10.34"       # Automation VM Traffic IP
ip.dst.value = "10.10.10.101"      # CSR Target IP

# Rate and Duration
f1.duration.fixed_packets.packets = 1000
f1.rate.pps = 100
f1.size.fixed = 128

# Push Configuration
api.set_config(config)

# Start Traffic
cs = api.control_state()
cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
api.set_control_state(cs)

print("Traffic successfully started on Dedicated Interface (Cloud1)")
```

---

## ✅ Benefits of this Approach
*   **No Disconnections:** High-volume traffic will not crash the PNETLab Web UI or SSH sessions (since they remain on `vmbr0`).
*   **Reliable Captures:** Wireshark sessions are more stable because the capture data "pipe" is isolated from the traffic stream.
*   **Protocol Safety:** Prevents accidental leakage of lab protocols (like OSPF/BGP) into the management network.

# 🍕 How it Works: The "Pizza Delivery" Analogy

To understand how your Python script actually moves packets into a PNETLab router, think of the system as a specialized delivery service.

### 1. The Script (The Customer)
When you execute `test_dedicated.py`, your script acts as the **Customer**.
*   **Action:** It writes an "Order" (the **Config**). It specifies: "I want 1,000 UDP packets, addressed to `10.10.10.101`, delivered at 100 packets per second."
*   **Connection:** It sends this order via HTTPS to the Manager (Kong Controller).

### 2. Kong Controller (The Shop Manager)
The **Kong Controller** is the "Brain" of the shop. He handles the paperwork but doesn't cook.
*   **Action:** He receives the order, validates it, and translates your Python instructions into a technical language the kitchen understands.
*   **Connection:** He looks at the `location: localhost:5555` in your script and tells the worker at that station to start production.

### 3. Ixia-c Traffic Engine (The Chef)
The **Traffic Engine** is the "Muscles" or the **Chef**. This is the Docker container doing the heavy lifting.
*   **Action:** Once the Manager gives the word, the Chef starts "cooking" packets instantly. He physically pushes these packets out through the VM's delivery door (**`ens20`**).
*   **Connection:** He is "plugged in" to the dedicated network interface.

### 4. Proxmox Bridge / `vmbr2` (The Private Road)
The **`vmbr2` Linux Bridge** acts as a **Dedicated Road**.
*   **Action:** It provides a private lane that connects the Automation VM directly to the PNETLab VM.
*   **Connection:** Because this road is separate from the Management Road (`vmbr0`), your "Pizza Deliveries" (traffic) never cause a "Traffic Jam" (lag) for your Web UI or SSH sessions.

### 5. PNETLab Cloud1 (The Front Door)
Inside the lab, **Cloud1** is the **Front Door** of your virtual building.
*   **Action:** It catches packets arriving from the `vmbr2` road and passes them to whatever device is connected to it in the topology.
*   **Connection:** In your lab, you have a "cable" drawn between Cloud1 and the CSR Router.

### 6. CSR Device (The Receiver)
The **CSR 1000v** is the **End Destination**.
*   **Action:** It sees packets arriving on its `GigabitEthernet1` interface. It checks the address (`10.10.10.101`), sees it is the intended recipient, and increases its "Input Packets" counter.
*   **Verification:** This is why you see the counters go up when the script finishes!

---

## 🛰️ The Data Path Summary
**Python Script** → **Kong Controller** → **Ixia Engine** → **`ens20`** → **`vmbr2` Bridge** → **Cloud1** → **CSR Router**

## Tried and Failed Content

# OTG / Ixia-C (Open Traffic Generator) Lab

## Overview

This section documents the setup and usage of **Ixia-C (OTG - Open Traffic Generator)** in the Automation-Labs environment.

We use OTG to:
- Generate L2/L3 traffic
- Build traffic flows programmatically
- Validate packet transmission
- Simulate real network traffic on interfaces like `ens18`

This integrates with our existing lab:
- **pyATS**: Device automation
- **Scapy**: Packet-level testing
- **OTG / Ixia-C**: Traffic generation at scale

---

## Architecture

### Automation VM


| Component | Value |
|---|---|
| **Host** | madhu-labs |
| **OS** | Ubuntu 24.04 |
| **IP** | 192.168.0.34 |

**Runs:**
- Docker
- Python virtual env (`pyats`)
- OTG scripts

### PNETLab Devices


| Device | IP |
|---|---|
| **CSR** | 192.168.0.101 |
| **R2** | 192.168.0.102 |

---

## Interface Configuration

```bash
ens18 → 192.168.0.34
```
*Used by the OTG traffic engine for packet injection.*

---

## Installation & Setup

### 1. Docker Installation
If Docker is not already installed:
```bash
sudo apt update
sudo apt install docker.io -y
sudo systemctl enable docker
sudo systemctl start docker
```
**Verify:** `docker version`

### 2. Pull OTG Images
```bash
sudo docker pull ghcr.io/open-traffic-generator/ixia-c-controller:latest
sudo docker pull ghcr.io/open-traffic-generator/ixia-c-traffic-engine:latest
```

### 3. Run Ixia-C Controller
```bash
sudo docker run -d \
  --name ixia-controller \
  --net=host \
  ghcr.io/open-traffic-generator/ixia-c-controller:latest \
  --accept-eula
```

### 4. Run Ixia-C Traffic Engine (Working Configuration)
This is the final working setup used in the lab:
```bash
sudo docker run -d \
  --name ixia-engine \
  --net=host \
  --privileged \
  -e IXIA_C_CONTROLLER=127.0.0.1 \
  -e ARG_IFACE_LIST="virtual@af_packet,ens18" \
  -e OPT_NO_HUGEPAGES=Yes \
  -e ACCEPT_EULA=YES \
  ghcr.io/open-traffic-generator/ixia-c-traffic-engine:latest
```

**Why this works:**
- `ARG_IFACE_LIST`: Binds the engine to `ens18`.
- `virtual@af_packet`: Enables virtual packet interface mode.
- `OPT_NO_HUGEPAGES`: Avoids kernel memory dependency issues.
- `--privileged`: Required for direct raw socket packet operations.

---

## Verification & Usage

### Check Containers
```bash
sudo docker ps -a
```
**Expected Status:**
- `ixia-controller`: **Up**
- `ixia-engine`: **Up**

### Install Python Dependencies
Inside the `pyats` virtual environment:
```bash
source ~/Automation-Labs/env/pyats/bin/activate
pip install requests urllib3 jsonschema grpcio
```

### Working Basic Traffic Script
**File:** `~/Automation-Labs/otg/scripts/basic_traffic.py`

```python
import requests
import urllib3

# Suppress self-signed certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OTG_HOST = "127.0.0.1"
OTG_PORT = 8443
url = f"https://{OTG_HOST}:{OTG_PORT}/control/state"

# Payload structure for flow control
payload = {
    "choice": "traffic",
    "traffic": {
        "choice": "flow_transmit",
        "flow_transmit": {
            "state": "start"
        }
    }
}

try:
    print(f"Sending start traffic request to {url}...")
    response = requests.post(url, json=payload, verify=False, timeout=5)
    if response.status_code == 200:
        print("Success! Traffic started.")
    else:
        print(f"Status {response.status_code}: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
```

**Run Script:**
```bash
python3 ~/Automation-Labs/otg/scripts/basic_traffic.py
```

---

## How OTG Works (Flow Model)

1.  **Config Phase (`/config`):** Defines ports and flows.
    - Example: Map `ens18` to port `p1` and define flow `f1`.
2.  **Control Phase (`/control/state`):** Manages the execution.
    - Example: Start flow transmission and monitor metrics.

---

## Troubleshooting & Key Observations


| Issue | Fix |
|---|---|
| **Engine exits immediately** | Ensure `ARG_IFACE_LIST` matches the host interface name. |
| **Hugepages error** | Set `OPT_NO_HUGEPAGES=Yes` in engine environment. |
| **SSL EOF Errors** | Use `verify=False` and ensure correct IP/Port (127.0.0.1:8443). |
| **404 Page Not Found** | Verify the endpoint path (e.g., use `/control/state`). |
| **400: No flows configured** | Push a configuration to `/config` before sending the start command. |

---

## Summary
We have successfully built a Docker-based OTG lab with the Ixia-C controller and engine bound to `ens18`. This provides a programmable REST API foundation for high-scale traffic generation within the Automation-Labs framework.

## Retrieving Flow Statistics
Once traffic is running, you can fetch real-time metrics (e.g., packets sent/received, rates, and transmit state) using the /monitor/metrics endpoint

Python Script for Metrics
Add this code to a new file, get_metrics.py, to see how many packets your ens18 interface is processing

import requests
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HOST = "127.0.0.1"
PORT = 8443
URL = f"https://{HOST}:{PORT}/monitor/metrics"

# Payload to request flow-specific metrics
payload = {
    "choice": "flow",
    "flow": {
        "flow_names": ["f1"]  # Must match the flow name in your config
    }
}

try:
    print(f"Fetching metrics from {URL}...")
    response = requests.post(URL, json=payload, verify=False)
    
    if response.status_code == 200:
        metrics = response.json()
        # Parse and print key flow statistics
        for flow in metrics.get("flow_metrics", []):
            print(f"\nFlow Name: {flow['name']}")
            print(f"  Transmit State: {flow['transmit']}")
            print(f"  Frames Transmitted: {flow['frames_tx']}")
            print(f"  Frames Received: {flow['frames_rx']}")
            print(f"  TX Rate (fps): {flow['frames_tx_rate']}")
    else:
        print(f"Failed to fetch metrics: {response.status_code} - {response.text}")

except Exception as e:
    print(f"Error: {e}")

Key Metric Fields

frames_tx: Total packets sent.
frames_rx: Total packets received (if a receiver is configured).
transmit: Current state (e.g., started or stopped).
frames_tx_rate: Current throughput in frames per second.