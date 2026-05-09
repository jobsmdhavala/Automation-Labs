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
