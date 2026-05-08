from genie.testbed import load

# Load the testbed
tb = load("/home/ubuntu/Automation-Labs/pyats/testbeds/testbed.yaml")

for dev in tb.devices.values():
    dev.connect()
    output = dev.parse("show ip interface brief")
    print(f"\n===== {dev.name} =====")
    for intf, data in output["interface"].items():
        print(f"{intf}: {data['ip_address']} - {data['status']}/{data['protocol']}")
    dev.disconnect()