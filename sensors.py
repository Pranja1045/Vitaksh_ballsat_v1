import time
import board
import busio
import subprocess
import Adafruit_DHT
import serial
import adafruit_bmp280

# Check if ADS1115 is connected before initializing it
def is_ads1115_connected():
    """Check if ADS1115 (0x48) is detected on the I2C bus."""
    try:
        result = subprocess.run(["i2cdetect", "-y", "1"], capture_output=True, text=True)
        return "48" in result.stdout
    except Exception as e:
        print(f"❌ I2C Error: {e}")
        return False

# Attempt to import ADS1115-related libraries if ADS1115 is connected
ADS1115_AVAILABLE = is_ads1115_connected()
if ADS1115_AVAILABLE:
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    i2c = busio.I2C(board.SCL, board.SDA)  # Initialize I2C once if ADS1115 is present

# --- Gas Sensors ---
class MQ2:
    def __init__(self, adc_channel=0, adc_address=0x48):
        if not ADS1115_AVAILABLE:
            print("❌ ADS1115 not detected. MQ2 will not be initialized.")
            self.adc = None
            return
        self.adc = ADS.ADS1115(i2c, address=adc_address)
        self.channel = AnalogIn(self.adc, getattr(ADS, f'P{adc_channel}'))

    def read_gas_level(self):
        return self.channel.value if self.adc else None

class MQ7:
    def __init__(self, adc_channel=1, adc_address=0x48):
        if not ADS1115_AVAILABLE:
            print("❌ ADS1115 not detected. MQ7 will not be initialized.")
            self.adc = None
            return
        self.adc = ADS.ADS1115(i2c, address=adc_address)
        self.channel = AnalogIn(self.adc, getattr(ADS, f'P{adc_channel}'))

    def read_gas_level(self):
        return self.channel.value if self.adc else None

class MQ131:
    def __init__(self, adc_channel=2, adc_address=0x48):
        if not ADS1115_AVAILABLE:
            print("❌ ADS1115 not detected. MQ131 will not be initialized.")
            self.adc = None
            return
        self.adc = ADS.ADS1115(i2c, address=adc_address)
        self.channel = AnalogIn(self.adc, getattr(ADS, f'P{adc_channel}'))

    def read_gas_level(self):
        return self.channel.value if self.adc else None

# --- DHT11 Sensor ---
class DHT11:
    def __init__(self, pin=4):
        self.pin = pin
        self.sensor = Adafruit_DHT.DHT11

    def read_data(self, retries=3):
        """Read temperature and humidity, retrying if necessary."""
        for _ in range(retries):
            humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
            if humidity is not None and temperature is not None:
                return {"temperature": temperature, "humidity": humidity}
            time.sleep(2)  # Wait before retrying
        return None  # Return None if all retries fail

# --- GPS Sensor (NEO6M) ---
class NEO6M:
    def __init__(self, port="/dev/ttyS0", baudrate=9600, timeout=1):
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)

    def read_coordinates(self):
        """Reads GPS coordinates from NEO6M module, handles missing data."""
        while True:
            data = self.ser.readline().decode('utf-8', errors='ignore')
            if "$GPGGA" in data:
                gps_data = data.split(",")
                if len(gps_data) > 4 and gps_data[2] and gps_data[4]:  # Ensure valid data
                    latitude = gps_data[2]
                    longitude = gps_data[4]
                    return {"latitude": latitude, "longitude": longitude}
        return None

# --- BMP280 Sensor ---
class BMP280:
    def __init__(self):
        """Initialize BMP280 sensor."""
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
        except Exception as e:
            print(f"❌ BMP280 Initialization Failed: {e}")
            self.sensor = None

    def read_pressure(self):
        """Reads atmospheric pressure in hPa."""
        if self.sensor:
            try:
                return self.sensor.pressure
            except Exception as e:
                print(f"❌ Error reading BMP280 pressure: {e}")
        return None

    def read_altitude(self):
        """Reads altitude in meters based on pressure."""
        if self.sensor:
            try:
                return self.sensor.altitude
            except Exception as e:
                print(f"❌ Error reading BMP280 altitude: {e}")
        return None
