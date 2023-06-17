import bme280
import smbus2

 
class Bme280:
    def __init__(self):
        port = 1
        self.bus = smbus2.SMBus(port)
        self.address = 0x76
        self.calibration_params = bme280.load_calibration_params(self.bus, self.address)



    def getTemperature(self):
        return bme280.sample(self.bus, self.address, self.calibration_params).temperature
