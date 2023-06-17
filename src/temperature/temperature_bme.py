try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus
from bme280 import BME280


class Bme280:
    def __init__(self):
        self.bus = SMBus(1)
        self.bme280 = BME280(i2c_dev=self.bus)



    def getTemperature(self):
        return self.bme280.get_temperature()
