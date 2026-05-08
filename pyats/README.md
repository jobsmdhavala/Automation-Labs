# pyATS Lab

## Overview

This lab is designed to explore and experiment with the Cisco **pyATS / Genie** network automation framework.

The setup consists of:

- **VM1 → PNETLab server**: Hosts virtual network devices.
- **VM2 → Automation VM (Ubuntu 24.04)**: Runs pyATS scripts to connect to devices inside PNETLab.

---

## Lab Topology

### Automation VM

| Component | Value |
|-----------|-------|
| Hostname  | madhu-labs |
| OS        | Ubuntu 24.04 |
| IP Address | 192.168.0.34 |
| User      | ubuntu |

### PNETLab VM

| Component | Value |
|-----------|-------|
| PNETLab Version | 5.3.13 |
| Ubuntu Base | Ubuntu 18 |
| Access URL | http://192.168.0.38 |

---

## Devices Used

| Device | Type | OS | Management IP |
|--------|------|----|---------------|
| CSR    | Cisco CSR1000v | IOS-XE | 192.168.0.101 |
| R2     | Cisco IOS Router | IOS | 192.168.0.102 |

---

## Directory Structure

```text
Automation-Labs/
└── pyats/
    ├── README.md
    ├── results/
    ├── scripts/
    │   ├── pyats_test.py
    │   └── show_interfaces.py
    └── testbeds/
        └── testbed.yaml

# pyATS Lab Documentation

## Purpose
This lab explores the Cisco pyATS automation framework in a controlled PNETLab environment.

It demonstrates:
- pyATS installation
- SSH connectivity
- Testbed creation
- Script execution
- Automation VM architecture
- Device communication with PNETLab

---

# Lab Architecture

| Component | Purpose | IP |
|---|---|---|
| Automation VM | Runs pyATS scripts | 192.168.0.34 |
| PNETLab VM | Hosts virtual routers | 192.168.0.38 |
| CSR1000v | IOS-XE router | 192.168.0.101 |
| R2 | IOS router | 192.168.0.102 |

---

# Directory Structure

```text
Automation-Labs/
└── pyats/
    ├── README.md
    ├── results/
    ├── scripts/
    │   └── pyats_test.py
    └── testbeds/
        └── testbed.yaml
```

---

# pyATS Installation

## Step 1: Create Python Virtual Environment

```bash
mkdir -p ~/Automation-Labs/env
python3 -m venv ~/Automation-Labs/env/pyats
```

## Step 2: Activate Virtual Environment

```bash
source ~/Automation-Labs/env/pyats/bin/activate
```

Prompt changes to:

```text
(pyats) ubuntu@madhu-labs:~$
```

## Step 3: Upgrade pip

```bash
pip install --upgrade pip
```

## Step 4: Install pyATS and Genie

```bash
pip install pyats[full]
pip install genie
```

> Always activate the virtual environment before running pyATS scripts.

---

# CSR1000v Configuration

## Configure Management Interface

```text
interface GigabitEthernet1
 ip address 192.168.0.101 255.255.255.0
 no shutdown
```

## Configure Username

```text
username admin privilege 15 secret admin
```

## Configure SSH

```text
ip domain name lab.local
crypto key generate rsa modulus 2048
ip ssh version 2
```

## Configure VTY

```text
line vty 0 4
 login local
 transport input ssh
```

---

# R2 Configuration

## Configure Management Interface

```text
interface FastEthernet0/0
 ip address 192.168.0.102 255.255.255.0
 no shutdown
```

## Configure Username

```text
username admin privilege 15 secret admin
```

## Configure SSH

```text
ip domain name lab.local
crypto key generate rsa modulus 1024
ip ssh version 2
```

## Configure VTY

```text
line vty 0 4
 login local
 transport input ssh
```

---

# SSH Compatibility for Older IOS

Ubuntu 24.04 blocks older SSH algorithms by default.

Create SSH config:

```bash
mkdir -p ~/.ssh
vi ~/.ssh/config
```

Add:

```text
Host 192.168.0.102
    KexAlgorithms +diffie-hellman-group1-sha1
    HostKeyAlgorithms +ssh-rsa
    PubkeyAcceptedAlgorithms +ssh-rsa
```

---

# Connectivity Validation

## Ping Test

```bash
ping 192.168.0.101
ping 192.168.0.102
```

## SSH Test

```bash
ssh admin@192.168.0.101
ssh admin@192.168.0.102
```

Both devices must be reachable before executing pyATS scripts.

---

# pyATS Testbed File

Location:

```text
~/Automation-Labs/pyats/testbeds/testbed.yaml
```

Content:

```yaml
devices:
  CSR:
    os: iosxe
    type: router
    connections:
      cli:
        protocol: ssh
        ip: 192.168.0.101
    credentials:
      default:
        username: admin
        password: admin

  R2:
    os: ios
    type: router
    connections:
      cli:
        protocol: ssh
        ip: 192.168.0.102
    credentials:
      default:
        username: admin
        password: admin
```

---

# First pyATS Script

Location:

```text
~/Automation-Labs/pyats/scripts/pyats_test.py
```

Content:

```python
from genie.testbed import load

tb = load("../testbeds/testbed.yaml")

for device in tb.devices.values():
    device.connect()

    output = device.execute("show version")

    print(f"\n===== {device.name} =====\n")
    print(output)

    device.disconnect()
```

---

# Running pyATS Scripts

```bash
source ~/Automation-Labs/env/pyats/bin/activate

cd ~/Automation-Labs/pyats/scripts

python3 pyats_test.py
```

---

# Successful Validation

Verified:
- SSH connectivity works
- pyATS connects successfully
- CSR and R2 reachable
- Commands execute correctly
- Output captured successfully
- Disconnect works properly

---

# Architecture Decisions

## Why Separate Automation VM?

Advantages:
- Cleaner architecture
- Easier package management
- Ubuntu 24 compatibility
- Avoids breaking PNETLab
- Easier framework upgrades
- Better scalability

## Final Design

| VM | Purpose |
|---|---|
| VM1 | PNETLab + Network Emulation |
| VM2 | Automation Frameworks |

---

# Future Work

Planned activities:
- pyATS testcases
- Genie parsers
- pyATS clean framework
- pytest integration
- Configuration automation
- Traffic validation
- Interface verification
- Routing validation
- CI/CD integration

---

# References

Cisco pyATS:
https://developer.cisco.com/pyats/

Cisco Genie:
https://developer.cisco.com/docs/genie-docs/

Cisco DevNet PubHub:
https://pubhub.devnetcloud.com/

---

# Notes

Guidelines:
- Keep scripts under scripts/
- Keep YAML files under testbeds/
- Keep outputs under results/
- Document failures and fixes
- Commit changes frequently to GitHub

