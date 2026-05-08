import snappi
import time

api = snappi.api(location='https://localhost:8443', verify=False)
config = api.config()

# 1. Map to engine
p1 = config.ports.port(name='p1', location='localhost:5555')[-1]

# 2. Define Flow
f1 = config.flows.flow(name='Dedicated-Flow')[-1]
f1.tx_rx.port.tx_name = p1.name
f1.metrics.enable = True # CRITICAL: Allows us to fetch stats later

# 3. Headers
eth, ip = f1.packet.ethernet().ipv4()
eth.src.value = "bc:24:11:fe:5f:f7" # Automation ens20 MAC
ip.src.value = "10.10.10.34"       
ip.dst.value = "10.10.10.101"      

# 4. Rate & Push
f1.duration.fixed_packets.packets = 1000
f1.rate.pps = 100
api.set_config(config)

# 5. Start
cs = api.control_state()
cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
api.set_control_state(cs)
print("Traffic started on Dedicated Cloud1!")

# 6. MONITORING LOOP (New Section)
req = api.metrics_request()
req.flow.flow_names = [f1.name]

print(f"{'Flow Name':<15} | {'Status':<10} | {'Tx Frames':<10}")
print("-" * 45)

while True:
    res = api.get_metrics(req)
    for m in res.flow_metrics:
        print(f"{m.name:<15} | {m.transmit:<10} | {m.frames_tx:<10}")
        
        # Break if traffic has finished sending 1000 packets
        if m.transmit == 'stopped':
            print("\nTransmission Complete.")
            break
    else:
        time.sleep(1)
        continue
    break
