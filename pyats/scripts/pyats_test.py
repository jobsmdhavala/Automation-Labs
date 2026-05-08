from genie.testbed import load

tb = load("/home/ubuntu/Automation-Labs/pyats/testbeds/testbed.yaml")
for device in tb.devices.values():
    device.connect(log_stdout=True)
    output = device.execute("show version")
    print(f"\n===== {device.name} =====\n")
    print(output)