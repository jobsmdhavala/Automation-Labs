import snappi

# 1. Connect to Controller
api = snappi.api(location="https://localhost:8443", verify=False)
config = api.config()

# 2. Ports - Location must point to the Engine's IP:Port
# In your setup, this is localhost:5555
p1 = config.ports.port(name="p1", location="localhost:5555")[-1]

# 3. Traffic flow - Use [-1] to select the flow object
flow = config.flows.flow(name="f1")[-1]
flow.tx_rx.port.tx_name = p1.name
# Since we are sending to a CSR (one-arm), we don't need rx_name
# If you want to track stats, enable metrics:
flow.metrics.enable = True

flow.rate.pps = 100
flow.size.fixed = 128
flow.duration.fixed_packets.packets = 1000

# 4. Apply config
api.set_config(config)

# 5. Start traffic (Unified control_state for Keng)
cs = api.control_state()
cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
api.set_control_state(cs)

print("Traffic started using Snappi 1.x (Keng Controller)")
