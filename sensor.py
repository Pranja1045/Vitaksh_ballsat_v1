import time
import Adafruit_DHT
import Adafruit_ADS1x15  # For ADC-based gas sensors (MQ7, MQ131)
import Adafruit_BMP.BMP085 as BMP085
import serial

class MQ2:
    def __init__(self, adc_channel=0, adc_address=0x48):
        self.adc = Adafruit_ADS1x15.ADS1115(address=adc_address)
        self.channel = adc_channel

    def read_gas_level(self):
        return self.adc.read_adc(self.channel, gain=1)

class DHT11:
    def __init__(self, pin=4):  # GPIO Pin
        self.pin = pin
        self.sensor = Adafruit_DHT.DHT11

    def read_data(self):
        humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
        return {"temperature": temperature, "humidity": humidity}

class BMP180:
    def __init__(self):
        self.sensor = BMP085.BMP085()

    def read_pressure(self):
        return self.sensor.read_pressure()

    def read_altitude(self):
        return self.sensor.read_altitude()

class NEO6M:
    def __init__(self, port="/dev/ttyS0", baudrate=9600, timeout=1):
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)

    def read_coordinates(self):
        while True:
            data = self.ser.readline().decode('utf-8', errors='ignore')
            if "$GPGGA" in data:
                gps_data = data.split(",")
                latitude = gps_data[2]
                longitude = gps_data[4]
                return {"latitude": latitude, "longitude": longitude}

class ADCGasSensor:
    def __init__(self, channel, adc_address=0x48):
        self.adc = Adafruit_ADS1x15.ADS1115(address=adc_address)
        self.channel = channel

    def read_sensor(self):
        return self.adc.read_adc(self.channel, gain=1)
