import snappi

api = snappi.api(location='https://localhost:8443', verify=False)
config = api.config()

# 1. Map to engine
p1 = config.ports.port(name='p1', location='localhost:5555')[-1]

# 2. Define Flow
f1 = config.flows.flow(name='Dedicated-Flow')[-1]
f1.tx_rx.port.tx_name = p1.name
f1.metrics.enable = True # Enable for verification script

# 3. Headers (Using the new 10.10.10.x subnet)
eth, ip = f1.packet.ethernet().ipv4()
eth.src.value = "bc:24:11:fe:5f:f7" # Automation ens20 MAC
ip.src.value = "10.10.10.34"       # Fake source IP for Ixia
ip.dst.value = "10.10.10.101"      # CSR's new IP

# 4. Rate & Push
f1.duration.fixed_packets.packets = 1000
f1.rate.pps = 100
api.set_config(config)

# 5. Start
cs = api.control_state()
cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
api.set_control_state(cs)

print("Traffic started on Dedicated Cloud1!")
