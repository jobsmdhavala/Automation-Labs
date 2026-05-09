import pytest
import snappi
import time

# 1. Setup the API connection fixture
@pytest.fixture
def api():
    return snappi.api(location="https://localhost:8443", verify=False)

# 2. Define the list of targets (IPs and Names)
# This is where the magic happens. Pytest will run the test once for each item.
nodes_to_test = [
    ("10.10.10.101", "CSR-Router"),
    ("10.10.10.102", "R2-Router")
]

@pytest.mark.parametrize("target_ip, node_name", nodes_to_test)
def test_node_reachability(api, target_ip, node_name):
    """Verify that Ixia can reach multiple nodes using a single test logic."""
    print(f"\n--- Starting Test for {node_name} ({target_ip}) ---")
    
    config = api.config()
    port = config.ports.port(name="p1", location="localhost:5555")[-1]
    
    flow = config.flows.flow(name=f"flow-{node_name}")[-1]
    flow.tx_rx.port.tx_name = port.name
    flow.metrics.enable = True
    
    # Headers
    eth, ip = flow.packet.ethernet().ipv4()
    eth.src.value = "bc:24:11:fe:5f:f7" # Automation ens20 MAC
    ip.dst.value = target_ip           # This changes per iteration!
    
    flow.duration.fixed_packets.packets = 500
    flow.rate.pps = 100
    
    # Push and Start
    api.set_config(config)
    cs = api.control_state()
    cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
    api.set_control_state(cs)
    
    # Wait for 500 packets (approx 6-7 seconds)
    time.sleep(7)
    
    # Fetch Metrics
    req = api.metrics_request()
    req.flow.flow_names = [flow.name]
    res = api.get_metrics(req)
    
    tx_count = res.flow_metrics[0].frames_tx
    
    # Assertion
    assert tx_count == 500, f"FAILED: {node_name} only received {tx_count} packets"
    print(f"SUCCESS: {node_name} verified with {tx_count} packets.")
