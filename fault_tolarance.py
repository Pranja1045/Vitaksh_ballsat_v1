import time
import json
from sensors import MQ2, DHT11, BMP180, NEO6M, ADCGasSensor

class FaultTolerance:
    def __init__(self, log_file="errors.json"):
        self.log_file = log_file
        self.ensure_file_exists()

        # Initialize sensors
        self.sensors = {
            "MQ2": MQ2(),
            "DHT11": DHT11(),
            "BMP180": BMP180(),
            "NEO6M": NEO6M(),
            "MQ7": ADCGasSensor(channel=1),
            "MQ131": ADCGasSensor(channel=2)
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

        health_status["MQ2"] = self.check_sensor("MQ2", self.sensors["MQ2"].read_gas_level)
        health_status["DHT11"] = self.check_sensor("DHT11", self.sensors["DHT11"].read_data)
        health_status["BMP180_Pressure"] = self.check_sensor("BMP180", self.sensors["BMP180"].read_pressure)
        health_status["BMP180_Altitude"] = self.check_sensor("BMP180", self.sensors["BMP180"].read_altitude)
        health_status["GPS_Coordinates"] = self.check_sensor("NEO6M", self.sensors["NEO6M"].read_coordinates)
        health_status["MQ7"] = self.check_sensor("MQ7", self.sensors["MQ7"].read_sensor)
        health_status["MQ131"] = self.check_sensor("MQ131", self.sensors["MQ131"].read_sensor)

        print("\n🔍 Sensor Health Check Completed:\n", health_status)
        return health_status

if __name__ == "__main__":
    fault_checker = FaultTolerance()
    while True:
        fault_checker.run_health_check()
        print("-" * 50)
        time.sleep(10)  # Run every 10 seconds
