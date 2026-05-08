# Open Traffic Generator (OTG) / Ixia-C Lab

## Purpose

This section is used to explore **modern traffic generation frameworks** using:

- Open Traffic Generator (OTG)
- Ixia-C (container-based traffic generator)
- Traffic APIs (JSON/YAML-based control)
- Stateless + stateful traffic generation
- Validation of network behavior using generated traffic

This is the next evolution after:
- pyATS (device automation)
- Scapy (packet-level crafting)

OTG/Ixia-C works at **scale traffic generation level**, closer to real production validation.

---

# Lab Architecture

## Automation VM (Ubuntu 24.04)

| Component | Value |
|----------|------|
| VM | madhu-labs |
| IP | 192.168.0.34 |
| Role | Automation + Traffic Controller |
| Tools | pyATS, Scapy, OTG, Ixia-C |

---

## PNETLab VM

| Component | Value |
|----------|------|
| Platform | PNETLab 5.3.13 |
| Role | Network Emulator |
| Devices | CSR, R2, Docker nodes |

### Devices

| Device | IP |
|--------|----|
| CSR1000v | 192.168.0.101 |
| R2 (IOS) | 192.168.0.102 |

---

# What is OTG / Ixia-C?

## Open Traffic Generator (OTG)

OTG is a **standard API model** for traffic generation.

Instead of manual CLI tools, it uses:

- JSON traffic models
- API-driven configuration
- Port-based traffic generation
- Stateless execution model

---

## Ixia-C

Ixia-C is a **containerized traffic engine** implementing OTG API.

It provides:

- Controller (API server)
- Traffic engine
- Flow generation
- Metrics collection

---

## Key Concept
