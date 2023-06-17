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
        signal.signal(signal.SIGINT, self.controleOff)

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
            print('readUserCommands',data)

            if data != -1 and data != None:
                if data['subcode'] == 0xC3:
                    if data['value'] == 1:
                        self.stateToOn()
                    elif data['value'] == 2:
                        self.stateToOff()
                    elif data['value'] == 3:
                        self.startRunning()
                    elif data['value'] == 4:
                        self.stopRunning()
                    elif data['value'] == 5:
                        self.incrementTime()
                    elif data['value'] == 6:
                        self.decrementTime()
                    elif data['value'] == 7:
                        self.toggleMode()
                    # dostuff
            time.sleep(0.2)

    def startRunning(self):
        self.state = 'running'
        self.controle(0, 0)
        self.modBus.write(0x01, 0x23, 0xD3, (1, 6 ,0 , 2), 1)
        time.sleep(1)
        self.modBus.read()

    def stopRunning(self):
        self.state = 'on'

    def incrementTime(self):
        pass

    def decrementTime(self):
        pass

    def toggleMode(self):
        pass

    def stateToOn(self):
        self.state = 'on'
        # turn lcd on
        self.lcd.turn_on_lcd_backlight()
        self.modBus.write(0x01, 0x23, 0xD3, (1, 6 ,0 , 2), 1)
        time.sleep(1)
        self.modBus.read()


    def controleOff(self, _signum, _frame):
        self.stateToOff()

    def stateToOff(self):
        self.state = 'off'
        self.powerControl.stop_pwm()
        self.lcd.turn_off_lcd_backlight()
        self.modBus.write(0x01, 0x23, 0xD3, (1, 6 ,0 , 2), 0)
        time.sleep(1)
        self.modBus.read()

    def updateCurrentExternalTemperature(self):
        self.currentExternalTemperature = self.externalTemperatureSensor.getTemperature()

    def readUserCommands(self):
        self.modBus.write(0x01, 0x23, 0xC3 , (1, 6 ,0 , 2), None)
        time.sleep(1)
        return self.modBus.read()