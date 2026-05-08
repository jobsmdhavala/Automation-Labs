import snappi
import time

api = snappi.api(location='https://localhost:8443', verify=False)
config = api.config()

# 1. Port & Flow with Tracking Enabled
p1 = config.ports.port(name='p1', location='localhost:5555')[-1]
f1 = config.flows.flow(name='f1')[-1]
f1.tx_rx.port.tx_name = p1.name
f1.metrics.enable = True  # <--- CRITICAL FIX

# 2. Minimal Packet Headers
eth, ip = f1.packet.ethernet().ipv4()
eth.src.value = "bc:24:11:b0:aa:80"
ip.dst.value = "192.168.0.101"
f1.duration.fixed_packets.packets = 1000
f1.rate.pps = 100

# 3. Push and Start
api.set_config(config)
cs = api.control_state()
cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
api.set_control_state(cs)

# 4. Request Metrics
print("Traffic started. Fetching metrics...")
req = api.metrics_request()
req.flow.flow_names = [f1.name]

# Loop to see stats increase
for _ in range(5):
    metrics = api.get_metrics(req)
    for m in metrics.flow_metrics:
        print(f"Flow: {m.name} | Status: {m.transmit} | Tx Frames: {m.frames_tx}")
    time.sleep(2)
