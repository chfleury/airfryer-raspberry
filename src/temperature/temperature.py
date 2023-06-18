from bmp280 import BMP280

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

class Bmp280:
    def __init__(self):
        bus = SMBus(1)
        self.bmp280 = BMP280(i2c_dev=bus)


    def getTemperature(self):
        
        return float(self.bmp280.get_temperature())
