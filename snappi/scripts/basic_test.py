import snappi
import time

# 1. Connect to Controller
api = snappi.api(location="https://localhost:8443", verify=False)
config = api.config()

# 2. Define Port
port = config.ports.port(name="p1", location="localhost:5555")[-1]

# 3. Define Flow
flow = config.flows.flow(name="f1")[-1]
flow.tx_rx.port.tx_name = port.name
flow.metrics.enable = True  # Required for flow metrics

# 4. Headers
eth, ip, udp = flow.packet.ethernet().ipv4().udp()
eth.dst.value = "ff:ff:ff:ff:ff:ff"
eth.src.value = "bc:24:11:fe:5f:f7" # Your ens20 MAC
ip.src.value = "10.10.10.34"
ip.dst.value = "10.10.10.101"

# 5. Traffic Properties
flow.size.fixed = 128
flow.rate.pps = 100
flow.duration.fixed_packets.packets = 1000 # Use fixed packets for easier verification

# 6. Push config and Start
try:
    print("Pushing configuration...")
    api.set_config(config)
    print("✓ Configuration accepted!")
    
    # NEW WAY: Use control_state for everything (Capture, Traffic, etc.)
    print("Starting traffic...")
    cs = api.control_state()
    cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
    api.set_control_state(cs)
    print("✓ Traffic is now active!")
    
    # Wait for traffic to finish
    time.sleep(5)
    
    # NEW WAY: Requesting metrics
    req = api.metrics_request()
    req.flow.flow_names = [flow.name]
    res = api.get_metrics(req)
    
    for m in res.flow_metrics:
        print(f"Flow: {m.name} | Frames TX: {m.frames_tx} | Status: {m.transmit}")
    
except Exception as e:
    print(f"Failed: {e}")
