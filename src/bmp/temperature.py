#!/usr/bin/env python

import time
from bmp280 import BMP280

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

# Initialise the BMP280
bus = SMBus(1)
bmp280 = BMP280(i2c_dev=bus)

def getTemperature():
    return bmp280.get_temperature()
  

# while True:
#     temperature = bmp280.get_temperature()
#     print('{:05.2f}*C'.format(temperature))
#     time.sleep(1)