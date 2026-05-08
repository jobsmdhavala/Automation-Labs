import snappi

# 1. Connect to Controller
api = snappi.api(location="https://localhost:8443", verify=False)
config = api.config()

# 2. Define Single Port (for one-arm/tx-only test) [web:3][web:2]
port = config.ports.port(name="p1", location="localhost:5555")[-1]

# 3. Define Flow - One-arm unidirectional (tx_name ONLY, no rx_name) [web:2]
flow = config.flows.flow(name="f1")[-1]
flow.tx_rx.port.tx_name = port.name
# DO NOT set rx_name - use choice for port-based tx-only

# 4. Use Ethernet header (NOT custom bytes - more reliable) [web:3]
eth = flow.packet.ethernet()[-1]
eth.dst.value = "ff:ff:ff:ff:ff:ff"  # Broadcast MAC
eth.src.value = "bc:24:11:fe:5f:f7"  # Your ens20 MAC
# eth.type is auto-set when you add IPv4

# Optional: Add IPv4 header for valid packets
ip = flow.packet.ipv4()[-1]
ip.src.value = "192.168.1.100"
ip.dst.value = "192.168.1.1"

# Optional: Add UDP header so packets are valid
udp = flow.packet.udp()[-1]
udp.src_port.value = 12345
udp.dst_port.value = 5000

# 5. Traffic Properties
flow.size.fixed = 128
flow.rate.pps = 100
flow.duration.choice = flow.duration.CONTINUOUS

# 6. Push config and Start
try:
    print("Pushing configuration...")
    api.set_config(config)
    print("✓ Configuration accepted!")
    
    print("Starting capture (optional)...")
    cs = api.capture_state()
    cs.state = cs.START
    api.set_capture_state(cs)
    
    print("Starting traffic...")
    ts = api.transmit_state()
    ts.state = ts.START
    api.set_transmit_state(ts)
    print("✓ Traffic is now active!")
    
    # Wait a bit then fetch metrics
    import time
    time.sleep(5)
    
    req = api.metrics_request()
    req.port.port_names = [port.name]
    req.port.column_names = [req.port.FRAMES_TX, req.port.FRAMES_RX]
    res = api.get_metrics(req)
    print(f"Frames TX: {res.port_metrics[0].frames_tx}")
    
except Exception as e:
    print(f"Failed: {e}")