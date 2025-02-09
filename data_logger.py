import json
import os
import time

class DataLogger:
    def __init__(self, filename="serial.json"):
        self.filename = filename
        self.ensure_file_exists()

    def ensure_file_exists(self):
        """Ensure the JSON file exists and has an empty dictionary if not."""
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump({}, f)

    def log_data(self, data):
        """Append new sensor data to the JSON file."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Human-readable timestamp
        data["timestamp"] = timestamp  # Add timestamp to data

        # Read existing data
        with open(self.filename, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = {}  # Reset if file is corrupted

        # Append new data
        logs[timestamp] = data

        # Write back to file
        with open(self.filename, "w") as f:
            json.dump(logs, f, indent=4)

        print(f"✅ Data logged at {timestamp}")
