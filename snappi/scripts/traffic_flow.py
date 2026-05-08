import snappi

api = snappi.api(location="https://127.0.0.1:8443", verify=False)
config = api.config()

# Ports
p1 = config.ports.port(name="p1", location="virtual@af_packet")

# Traffic flow
flow = config.flows.flow(name="f1")
flow.tx_rx.port.tx_name = "p1"
flow.tx_rx.port.rx_name = "p1"

flow.rate.pps = 100
flow.size.fixed = 128

# Apply config
api.set_config(config)

# Start traffic
ts = api.transmit_state()
ts.state = ts.START
api.set_transmit_state(ts)

print("Traffic started using Snappi")