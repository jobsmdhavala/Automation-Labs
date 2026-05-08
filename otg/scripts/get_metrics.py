import requests
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HOST = "127.0.0.1"
PORT = 8443
URL = f"https://{HOST}:{PORT}/monitor/metrics"

# Payload to request flow-specific metrics
payload = {
    "choice": "flow",
    "flow": {
        "flow_names": ["f1"]  # Must match the flow name in your config
    }
}

try:
    print(f"Fetching metrics from {URL}...")
    response = requests.post(URL, json=payload, verify=False)
    
    if response.status_code == 200:
        metrics = response.json()
        # Parse and print key flow statistics
        for flow in metrics.get("flow_metrics", []):
            print(f"\nFlow Name: {flow['name']}")
            print(f"  Transmit State: {flow['transmit']}")
            print(f"  Frames Transmitted: {flow['frames_tx']}")
            print(f"  Frames Received: {flow['frames_rx']}")
            print(f"  TX Rate (fps): {flow['frames_tx_rate']}")
    else:
        print(f"Failed to fetch metrics: {response.status_code} - {response.text}")

except Exception as e:
    print(f"Error: {e}")
