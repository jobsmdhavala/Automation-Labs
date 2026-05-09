What is SPyTest?

SPyTest is an automation framework primarily developed for SONiC (Software for Open Networking in the Cloud) switches.
It allows engineers to:

Automate CLI commands and tests.
Validate network configurations and topologies.
Run regression tests for SONiC features.
Integrate with pytest for advanced reporting.

Key Point: SPyTest is tightly integrated with SONiC APIs and assumes SONiC-specific modules, hooks, and network abstractions.

What SPyTest is Meant For

SPyTest is not a generic Cisco/Juniper automation framework. It is designed for:

SONiC switches (physical or virtual).
Testing SONiC/SAI features like routing, MAC learning, VLANs, and switch ASIC behaviors.
Automated testbeds that use containerized SONiC images (Docker/LXC).

It is not intended for vanilla Cisco IOS/IOS-XE labs like your PNETLab CSR/R2 topology. Attempting to run SPyTest on Cisco devices will result in framework import errors, missing modules, or unsupported feature failures.

Installation Steps
Python Virtual Environment
mkdir -p ~/Automation-Labs/env
python3 -m venv ~/Automation-Labs/env/spytest
source ~/Automation-Labs/env/spytest/bin/activate
Install SPyTest
pip install -U pip
git clone https://github.com/Azure/sonic-mgmt.git ~/Automation-Labs/sonic-mgmt
cd ~/Automation-Labs/sonic-mgmt
pip install -r requirements.txt
Verify Installation
~/Automation-Labs/sonic-mgmt/spytest/bin/spytest --version

SPyTest Testbed
SPyTest uses YAML testbed files to define devices, services, and topologies.
Example device types it supports:
sonic (for SONiC switches)
vm (virtual machines hosting SONiC containers)
Testbed files for non-SONiC devices (like Cisco IOS) are not fully supported and will raise errors during execution.

Creating a SONiC Testbed

SPyTest supports SONiC/SAI labs using:

SONiC Docker images (official SONiC containers)
SONiC VM images (Hyper-V, VMware, or Proxmox)
Virtual testbed frameworks:
SONiC + PTF (Packet Test Framework)
Docker-based multi-ASIC SONiC labs
Containerlab + SONiC container topology

Key Points for Lab Placement:

Component	Recommended VM
SONiC Testbed VMs	PNETLab VM (for network emulation)
SPyTest Client	Automation VM (for running scripts and controlling the lab)
PNETLab can host SONiC/SAI containerized labs. Your Automation VM is used to run SPyTest scripts and connect to PNETLab devices over SSH/API.

Notes on PNETLab Support
PNETLab 5.x can emulate network devices using SONiC images.
Interfaces must be correctly mapped and Promiscuous Mode enabled on Proxmox bridges if traffic injection is needed.
Each SONiC VM/container can be assigned IPs for management, allowing SPyTest from the Automation VM to connect via SSH or gRPC.

Conclusion for Current Lab
Your current PNETLab topology (CSR/R2) is Cisco IOS devices, so SPyTest cannot run natively.
For Cisco automation, use pyATS, which works seamlessly with your existing testbed.
SPyTest is best used for future SONiC/SAI labs where:
The PNETLab VM hosts SONiC virtual switches.
The Automation VM runs SPyTest Python scripts.
Traffic and CLI operations are executed against SONiC APIs or SSH.
This separation ensures a production-like environment while preserving compatibility with SPyTest.

References:

SPyTest GitHub
SONiC Documentation
SPyTest Testbed Format

Perfect! Here’s a ready-to-use SONiC SPyTest testbed YAML and example Python script, fully compatible with PNETLab virtual SONiC switches. I’ve written it as a single markdown block so you can copy-paste directly into your README or lab folder

Purpose

This lab demonstrates how to run SPyTest against SONiC virtual switches in PNETLab. It uses a minimal testbed with two SONiC switches and verifies basic SSH connectivity and CLI commands.

Testbed File

Create: ~/Automation-Labs/spytest/testbeds/sonic_testbed.yaml

version: 2.0

# Services and configs are required for SPyTest parsing
services:
  default: {}
configs:
  default:
    current: []
    restore: []
params:
  def_dut: {}
  def_tg: {}
builds:
  default: {}

devices:
  SONiC1:
    device_type: sonic
    os: sonic
    access:
      protocol: ssh
      ip: 192.168.0.201  # Replace with your PNETLab SONiC VM IP
    credentials:
      username: admin
      password: Admin@123
    properties:
      config: default
      params: def_dut

  SONiC2:
    device_type: sonic
    os: sonic
    access:
      protocol: ssh
      ip: 192.168.0.202  # Replace with your second SONiC VM IP
    credentials:
      username: admin
      password: Admin@123
    properties:
      config: default
      params: def_dut

topology:
  SONiC1:
    interfaces: {}
  SONiC2:
    interfaces: {}

SPyTest Python Script

Create: ~/Automation-Labs/spytest/scripts/test_sonic_ssh.py

from spytest import st

def test_sonic_ssh_access():
    """Verify SPyTest can log into SONiC1 and SONiC2 and run CLI commands."""
    duts = ["SONiC1", "SONiC2"]

    for dut in duts:
        st.log(f"--- ATTEMPTING CONNECTION TO {dut} ---")
        # 'st.show' runs CLI commands on the DUT
        output = st.show(dut, "show interfaces status")

        # Validation logic
        if output:
            st.log(f"Successfully received output from {dut}")
            # Ensure at least one interface is listed
            assert "Ethernet" in output
        else:
            st.report_fail("no_console_output", dut)

How to Run

Activate your SPyTest virtual environment:

source ~/Automation-Labs/env/spytest/bin/activate

Run the test:

~/Automation-Labs/sonic-mgmt/spytest/bin/spytest \
scripts/test_sonic_ssh.py \
--testbed-file ../testbeds/sonic_testbed.yaml \
-vv \
--skip-init-config \
--feature-group none

Notes
PNETLab Setup for SONiC:
Deploy SONiC container/VMs in PNETLab.
Assign management IPs (e.g., 192.168.0.201, 192.168.0.202).
Enable Promiscuous Mode on Proxmox bridge for traffic visibility.
Automation VM:
Runs SPyTest scripts.
Connects to SONiC devices over SSH.
SPyTest Requirements:
Only works with SONiC/SAI devices.
Cisco IOS/IOS-XE devices will fail due to missing hooks/modules.
Topology Expansion:
Add more SONiC devices in devices section.
Define interfaces and links in the topology section for traffic and feature tests.

References
SPyTest GitHub
SONiC Official Documentation
SPyTest Testbed YAML


# SONiC Virtual Switch Lab in PNETLab

## What We Are Building

We want to create a complete SONiC virtual switch topology inside PNETLab so that:

- SPyTest can execute SONiC automation testcases
- pyATS can connect to SONiC switches
- Snappi / Ixia-c can generate traffic
- We can learn SONiC CLI, APIs, SAI, telemetry, and automation

---

# High-Level Architecture

```text
+------------------------------------------------------+
|                  Proxmox Host                        |
|                                                      |
|   +----------------------------------------------+   |
|   |                PNETLab VM                    |   |
|   |                                              |   |
|   |   +-------------+    +-------------+         |   |
|   |   | SONiC-VS-1  |----| SONiC-VS-2  |         |   |
|   |   +-------------+    +-------------+         |   |
|   |          |                    |              |   |
|   +----------|--------------------|--------------+   |
|              |                    |                  |
|   +----------|--------------------|--------------+   |
|   |          |    Automation VM   |              |   |
|   |          +---- pyATS          |              |   |
|   |          +---- SPyTest        |              |   |
|   |          +---- Snappi         |              |   |
|   |          +---- Ixia-c         |              |   |
|   +----------------------------------------------+   |
+------------------------------------------------------+

Important Design Decision
Where Should SONiC Nodes Run?
Recommended
Component	Recommended Location
SONiC Switches	PNETLab VM
Cisco Routers	PNETLab VM
Linux Hosts	PNETLab VM
Traffic Generator APIs	Automation VM
pyATS	Automation VM
SPyTest	Automation VM
Snappi	Automation VM
Ixia-c	Automation VM
Why SONiC Should Run Inside PNETLab

PNETLab is designed for:

Multi-node network topology simulation
Virtual switch interconnections
L2/L3 forwarding
Interface wiring
Packet flow visualization

SONiC virtual switches behave like network appliances, so PNETLab is the correct place.

Why Automation Tools Should Run in Automation VM

Automation tools need:

Python environments
Libraries
APIs
Git repos
Docker
CI/CD
Reports

Keeping them separate is cleaner and scalable.

Does PNETLab Support SONiC?
YES — Absolutely

PNETLab supports:

SONiC Virtual Switch (VS)
SONiC KVM Images
SONiC Cloud Images
SONiC Generic x86 Images

Many engineers use PNETLab/EVE-NG for SONiC labs.

Which SONiC Image Should We Use?
Recommended for Labs
SONiC-VS (Virtual Switch)

Why?

Lightweight
Runs well in KVM
Perfect for SPyTest
No ASIC required
Works for learning and automation
SONiC Image Sources
Official SONiC Builds
https://sonic.software/
Azure SONiC Builds
https://sonic-build.azurewebsites.net/
Community Builds
https://github.com/sonic-net/SONiC
Recommended SONiC Image Type

Use:

sonic-vs

or

genericx86_64-kvm_xxx.bin
Minimum Resources Per SONiC Node
Resource	Recommended
vCPU	2
RAM	4 GB
Disk	8-16 GB
PNETLab SONiC Installation Workflow
STEP 1 — Download SONiC Image

Example:

wget https://sonic-build.azurewebsites.net/ui/sonic-vs.img.gz
STEP 2 — Upload to PNETLab

Copy image to PNETLab server:

scp sonic-vs.img.gz root@PNETLAB:/opt/unetlab/addons/qemu/
STEP 3 — Create SONiC Folder

Inside PNETLab:

cd /opt/unetlab/addons/qemu
mkdir sonic-vs
cd sonic-vs
STEP 4 — Rename Image

PNETLab expects:

virtioa.qcow2

Example:

gunzip sonic-vs.img.gz
mv sonic-vs.img virtioa.qcow2

If qcow2 conversion required:

qemu-img convert -f raw -O qcow2 sonic.img virtioa.qcow2
STEP 5 — Fix Permissions
/opt/unetlab/wrappers/unl_wrapper -a fixpermissions
STEP 6 — Add SONiC Node in PNETLab GUI

Inside topology:

Add Node
→ QEMU
→ sonic-vs
STEP 7 — Connect Interfaces

Example:

SONiC1 Ethernet0 ---- Ethernet0 SONiC2

You can also connect:

Cisco CSR1000v
Linux hosts
Traffic generators
Default SONiC Credentials

Most images:

username: admin
password: YourPaSsWoRd

Some builds:

admin / admin
Verify SONiC Boot

Console should show:

show version
show interfaces status
show ip interface
Verify Interfaces

Example:

show interfaces status

You should see:

Ethernet0
Ethernet4
Ethernet8
...
Basic SONiC Configuration
Configure Management IP
sudo config interface ip add eth0 192.168.0.100/24
sudo config route add default 192.168.0.1
Enable SSH

Usually enabled by default.

Verify:

systemctl status ssh
Test SSH from Automation VM
ssh admin@192.168.0.100
SPyTest + SONiC Relationship
VERY IMPORTANT

SPyTest is NOT a generic network automation framework.

It is:

A SONiC-focused network test automation framework
What SPyTest Expects

SPyTest expects:

SONiC CLI
SONiC APIs
SONiC services
SONiC telemetry
SONiC filesystem
SONiC feature models

It internally imports:

apis.common.sonic_hooks

Which means:

SPyTest is tightly coupled with SONiC
Why Cisco IOS XE Failed

Your Cisco CSR devices do not have:

SONiC commands
SONiC services
SONiC architecture
SONiC APIs

Therefore SPyTest crashes internally.

Correct Conclusion
pyATS

Good for:

Cisco
Multi-vendor
Generic automation
SPyTest

Good for:

SONiC
SONiC regression testing
SONiC validation
SONiC feature automation
Recommended Future Lab Topology
Learning Topology
+------------+       +------------+
| SONiC-1    |-------| SONiC-2    |
+------------+       +------------+
      |                     |
      +----------+----------+
                 |
          +-------------+
          | Linux Host  |
          +-------------+
Advanced Topology
+------------+       +------------+
| SONiC Spine|-------| SONiC Leaf |
+------------+       +------------+
       |                    |
+-------------+      +-------------+
| Ixia-c TG   |      | Linux Host  |
+-------------+      +-------------+
Where Snappi/Ixia-c Fits

Snappi + Ixia-c can:

Generate packets
Validate throughput
Validate ECMP
Validate QoS
Validate VXLAN
Validate BGP convergence

against SONiC switches.

Final Recommended Learning Path
Phase 1
SONiC CLI
SONiC architecture
PNETLab SONiC setup
Phase 2
pyATS automation
SONiC SSH automation
Phase 3
SPyTest testcases
SONiC validation
Phase 4
Snappi + Ixia-c traffic testing
Phase 5
SAI testing
Datacenter fabrics
EVPN/VXLAN
QoS validation
Final Conclusion

Your lab should evolve into:

PNETLab
    → SONiC virtual switches
    → Cisco routers
    → Linux hosts

Automation VM
    → pyATS
    → SPyTest
    → Snappi
    → Ixia-c
    → Python automation

This is a realistic modern datacenter/network automation learning environment.
