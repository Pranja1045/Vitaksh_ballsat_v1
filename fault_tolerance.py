import time
import json
from sensors import MQ2, MQ7, MQ131, DHT11, NEO6M, BMP280

class FaultTolerance:
    def __init__(self, log_file="errors.json"):
        self.log_file = log_file
        self.ensure_file_exists()

        # Initialize sensors
        self.sensors = {
            "MQ2": MQ2(),
            "MQ7": MQ7(),
            "MQ131": MQ131(),
            "DHT11": DHT11(),
            "NEO6M": NEO6M(),
            "BMP280": BMP280()
        }

    def ensure_file_exists(self):
        """Ensure the JSON file exists."""
        try:
            with open(self.log_file, "r") as f:
                json.load(f)  # Check if valid JSON
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.log_file, "w") as f:
                json.dump({}, f)

    def check_sensor(self, sensor_name, read_function):
        """Check if a sensor is working and return its value or log an error."""
        try:
            value = read_function()
            if value is None:
                raise ValueError("No Data Received")
            return value
        except Exception as e:
            self.log_error(sensor_name, str(e))
            return None

    def log_error(self, sensor_name, error_message):
        """Log sensor errors into a JSON file."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        error_entry = {timestamp: {sensor_name: error_message}}

        with open(self.log_file, "r") as f:
            try:
                error_log = json.load(f)
            except json.JSONDecodeError:
                error_log = {}

        error_log.update(error_entry)

        with open(self.log_file, "w") as f:
            json.dump(error_log, f, indent=4)

        print(f"❌ Error in {sensor_name}: {error_message}")

    def run_health_check(self):
        """Run a full health check on all sensors."""
        health_status = {}

        for sensor_name, sensor_obj in self.sensors.items():
            if sensor_obj:
                health_status[sensor_name] = self.check_sensor(sensor_name, getattr(sensor_obj, "read_gas_level", sensor_obj.read_data) if sensor_name != "BMP280" else sensor_obj.read_pressure)

        print("\n🔍 Sensor Health Check Completed:\n", health_status)
        return health_status

if __name__ == "__main__":
    fault_checker = FaultTolerance()
    while True:
        fault_checker.run_health_check()
        print("-" * 50)
        time.sleep(10)  # Run every 10 seconds
