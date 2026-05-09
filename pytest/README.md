# 🧪 Network Validation with Pytest

### Introduction
**Pytest** is a robust Python testing framework that turns manual verification into automated "Pass/Fail" results. In network automation, we use Pytest to move beyond just *executing* commands; we use it to *verify* that the network is actually behaving as expected. It automatically searches for test files, runs them, and provides a clear report of what works and what is broken.

---

### 1. Install Pytest in your Environment
To keep your workspace clean, we install Pytest inside the same `pyats` virtual environment used for your traffic scripts.

```bash
# 1. Activate your existing environment
source ~/Automation-Labs/env/pyats/bin/activate

# 2. Install Pytest and the HTML reporting plugin
pip install pytest pytest-html

# 3. Verify installation
pytest --version
```

---

### 2. Creating a Simple Pytest Script
Pytest follows a specific naming convention: files must start with `test_` and test functions must start with `test_`. 

Create a file named `test_ixia_reachability.py` in your `pytest/` folder:

```python
import pytest
import snappi
import time

# FIXTURES: These handle the 'Setup' (connecting to the controller)
@pytest.fixture
def api():
    """Provides a connection to the Keng Controller for the tests."""
    return snappi.api(location="https://localhost:8443", verify=False)

# TEST CASE: Validating traffic flow to CSR
def test_traffic_transmission(api):
    """
    Goal: Verify that the Ixia Engine successfully transmits 1000 packets.
    """
    config = api.config()
    port = config.ports.port(name="p1", location="localhost:5555")[-1]
    
    flow = config.flows.flow(name="pytest-flow")[-1]
    flow.tx_rx.port.tx_name = port.name
    flow.metrics.enable = True
    
    # Headers for our dedicated Cloud1 subnet
    eth, ip = flow.packet.ethernet().ipv4()
    eth.src.value = "bc:24:11:fe:5f:f7" # ens20 MAC
    ip.dst.value = "10.10.10.101"      # CSR IP
    
    flow.duration.fixed_packets.packets = 1000
    flow.rate.pps = 100
    
    # Push and Start
    api.set_config(config)
    cs = api.control_state()
    cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
    api.set_control_state(cs)
    
    # Wait for traffic to finish
    # Increased sleep to 12s because 1000 packets at 100 PPS takes exactly 10s
    time.sleep(12) 

    # 1. Create the request object
    req = api.metrics_request()
    
    # 2. Specify that we want flow metrics for our specific flow
    req.flow.flow_names = [flow.name]
    
    # 3. Fetch the metrics
    res = api.get_metrics(req)
    
    # 4. Extract the Tx value and Assert
    # We access index [0] because flow_metrics is a list
    tx_count = res.flow_metrics[0].frames_tx
    
    assert tx_count == 1000, f"FAILED: Expected 1000 packets but sent {tx_count}"
    print(f"\nSUCCESS: Verified {tx_count} packets sent to CSR.")

```

---

### 3. Running the Test
You can run a single test file or an entire folder of tests with one command.

```bash
# Run the test with 'verbose' output
pytest -v test_ixia_reachability.py

# Run the test and generate a professional HTML report
pytest --html=report.html --self-contained-html
```

---

### ❓ Why use Pytest instead of previous scripts?

1.  **Assertive Testing:** Your previous scripts just printed "Traffic Started." Pytest uses **Assertions** to confirm the traffic actually happened. If the packet count is wrong, Pytest screams "FAIL."
2.  **Automatic Discovery:** You don't have to run scripts one by one. You can run `pytest` in your root folder, and it will find and run every test you’ve ever written.
3.  **Setup/Teardown (Fixtures):** Pytest handles the "boring" stuff like opening and closing connections to your routers or controllers in the background, keeping your main test code clean and easy to read.
4.  **Detailed Reporting:** If a test fails, Pytest shows you exactly which line failed and what the variables were at that moment. It also creates HTML reports that you can share with your team.
5.  **Stop on Failure:** In a large lab, you can tell Pytest to stop immediately after the first failure (`pytest -x`), saving you time when troubleshooting.

### ✅ Validation Success
Running the automated test suite confirms the data plane integrity:
- **Test:** `test_traffic_transmission`
- **Result:** PASSED
- **Metric:** 1000/1000 packets verified
- **Environment:** Snappi 1.53.0 + Keng Controller

# 🚀 Advanced Pytest Capabilities for Network Automation

Moving beyond simple scripts, **Pytest** serves as a professional-grade engine that can validate every layer of your network. Below are the core capabilities that make it powerful for lab environments like PNETLab.

---

### 1. Parameterization (Test Scaling)
Instead of writing separate scripts for every router, you can run the same test against a list of targets.
*   **Example:** Run one reachability test that automatically loops through **CSR**, **R2**, and **Spine-01**.
*   **Benefit:** Reduces code duplication and allows you to test 100 devices with 10 lines of code.

### 2. Fixtures (Smart Setup & Teardown)
Fixtures handle the "pre-work" and "clean-up" for your tests.
*   **Setup:** Automatically connect to the **Keng Controller** or log into a **CSR** before the test begins.
*   **Teardown:** Automatically clear the traffic configuration or reset interface counters after the test finishes, ensuring the lab is ready for the next run.

### 3. Assertive Validation (Pass/Fail Logic)
Pytest uses the `assert` statement to turn data into a verdict.
*   **Logic:** You can compare live data against your "Golden Baseline."
*   **Example:** `assert ospf_state == "FULL"` or `assert packet_loss_percentage < 0.1`.

### 4. Parallel Execution (`pytest-xdist`)
You can run multiple network tests at exactly the same time.
*   **Capability:** Instead of waiting for Test A to finish before starting Test B, you can use multiple CPU cores to validate different parts of your PNETLab topology simultaneously.
*   **Benefit:** Massive reduction in total testing time.

### 5. Multi-Vendor Integration with pyATS
By combining Pytest with **pyATS/Genie**, you can create "Abstract" tests.
*   **Scenario:** Write a single test to check BGP neighbors. Pytest + pyATS will automatically handle the different CLI commands for **Cisco IOS**, **Juniper Junos**, or **Arista EOS**.

### 6. Negative Testing
Pytest excels at proving that the network **fails correctly**.
*   **Example:** Write a test that ensures traffic is *blocked* when an ACL is applied. The test "Passes" if the traffic is dropped and "Fails" if the traffic gets through.

### 7. Marker & Tagging System
You can categorize your tests using custom markers.
*   **Usage:** Tag tests as `@pytest.mark.smoke` or `@pytest.mark.regression`.
*   **Execution:** Run only high-priority checks with `pytest -m smoke`.

---

## 📊 Summary of Network Testing Types


| Testing Type | Goal | Example Scenario |
| :--- | :--- | :--- |
| **Smoke** | Basic Health | Is the Management IP reachable? |
| **Functional** | Feature Check | Does OSPF form an adjacency over the Tunnel? |
| **Performance** | Throughput | Can the CSR handle 500 PPS without CPU spikes? |
| **Regression** | Change Control | Did my new ACL break the existing BGP session? |
| **Compliance** | Security | Are all unused ports currently `shutdown`? |

### 🔄 Parameterized Testing
We use `@pytest.mark.parametrize` to scale our validation. 
- **Efficiency:** Test multiple routers (CSR, R2, etc.) using a single block of code.
- **Subnet:** All testing occurs on the dedicated `10.10.10.0/24` subnet.
- **Reporting:** Pytest provides individual pass/fail results for every node in the list.

# 🔄 Scalable Testing with Parameterization

We transitioned from single-target scripts to **Parameterized Pytest Suites**. This allows us to run the same validation logic across multiple network nodes simultaneously.

### How it Works
Using `@pytest.mark.parametrize`, we define a list of targets (IPs and Names). Pytest then "injects" these values into the test function one by one.

### Benefits
- **DRY (Don't Repeat Yourself):** One test function handles 2, 20, or 200 routers.
- **Granular Results:** If one router in the lab is down, Pytest shows exactly which one failed while others pass.
- **Speed:** Validates the data-plane reachability for the entire PNETLab topology in seconds.

### Execution Command
```bash
   pytest -v test_multi_node.py
```