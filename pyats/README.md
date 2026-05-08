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
