import time
import json
from sensors import MQ2, DHT11, BMP180, NEO6M, ADCGasSensor
from power_management import PowerManager
from fault_tolerance import FaultTolerance
from data_logger import DataLogger
from communication import Communicator

def main():
    print("🚀 Satellite System Initializing...")

    # Initialize modules
    power_manager = PowerManager()
    fault_checker = FaultTolerance()
    data_logger = DataLogger()
    communicator = Communicator()

    # Initialize sensors
    mq2 = MQ2()
    dht = DHT11()
    bmp = BMP180()
    gps = NEO6M()
    mq7 = ADCGasSensor(channel=1)
    mq131 = ADCGasSensor(channel=2)

    while True:
        print("\n🔍 Running System Check...")

        # 1️⃣ **Power Management** (Decides sensor activation based on altitude)
        power_status = power_manager.manage_power()

        # 2️⃣ **Run Fault Tolerance Checks**
        fault_checker.run_health_check()

        # 3️⃣ **Collect Sensor Data**
        sensor_data = {
            "MQ2_Gas": mq2.read_gas_level(),
            "DHT11": dht.read_data(),
            "BMP180_Pressure": bmp.read_pressure(),
            "BMP180_Altitude": bmp.read_altitude(),
            "GPS_Coordinates": gps.read_coordinates(),
            "MQ7_Gas": mq7.read_sensor(),
            "MQ131_Gas": mq131.read_sensor(),
            "Power_Status": power_status
        }

        # 4️⃣ **Log Data to `serial.json`**
        data_logger.log_data(sensor_data)

        # 5️⃣ **Transmit Data to Ground Station**
        communicator.send_data(sensor_data)

        print("✅ Data Collection & Transmission Complete")
        print("-" * 50)

        time.sleep(10)  # Loop every 10 seconds

if __name__ == "__main__":
    main()
