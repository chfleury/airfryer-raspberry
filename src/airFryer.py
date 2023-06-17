import signal
import time

from modbus.modbus import ModBus
from power.power_control import PowerControl
from pid.pid import PID
from lcd_display.lcd_display import LCDController
from temperature.temperature import Bmp280

class AirFryer:
    def __init__(self):
        signal.signal(signal.SIGALRM, self.controle)
        signal.signal(signal.SIGINT, self.stateToOff)

        self.state = 'off' # 'on', 'off', 'running'
        self.modBus = ModBus()
        
        self.powerControl = PowerControl()
        self.pid = PID(30, 0.2, 400)
        self.referencia = 0
        self.currentInternalTemperature = 0
        self.currentExternalTemperature = 0

        self.lcd = LCDController()
        self.lcd.init_lcd()
        self.lcd.turn_off_lcd_backlight()

        self.externalTemperatureSensor = Bmp280()

    # Signal handler function
    def controle(self, _signum, _frame):
        if self.state == 'running':
            signal.alarm(1)

            self.pid.updateReference(self.referencia)

            signal = self.pid.pidControl(self.currentInternalTemperature)

            if signal < 0:
                signal *= -1
                self.powerControl.set_FAN_pwm(signal)
            else:
                self.powerControl.set_resistor_pwm(signal)

            print("SIGALRM received!")

    def mainLoop(self):
        while True:
            data = self.readUserCommands()
            if data != -1:
                if data['subcode'] == 0xC3:
                    print(data['value'])
                    # dostuff
            time.sleep(0.2)

    def stateToRunning(self):
        self.state = 'running'
        self.controle(0, 0)

    def stateToOn(self):
        self.state = 'on'
        # turn lcd on
        self.lcd.turn_on_lcd_backlight()

    def stateToOff(self):
        self.state = 'off'
        self.powerControl.stop_pwm()
        self.lcd.turn_off_lcd_backlight()

    def updateCurrentExternalTemperature(self):
        self.currentExternalTemperature = self.externalTemperatureSensor.getTemperature()


    def readUserCommands(self):
        self.modBus.write(0x01, 0x23, 0xC3 , (1, 6 ,0 , 2), None)
        time.sleep(0.1)
        data = self.modBus.read()
        print('readUserCommands',data)