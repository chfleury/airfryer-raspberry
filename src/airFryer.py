import signal
import time

from modbus.modbus import ModBus
from power.power_control import PowerControl
from pid.pid import PID
from lcd_display.lcd_display import LCDController
from temperature.temperature_bme import Bme280
from temperature.temperature import Bmp280
import random

class AirFryer:
    def __init__(self):
        signal.signal(signal.SIGALRM, self.handle_SIGALRM)
        signal.signal(signal.SIGINT, self.controleOff)

        self.state = 'off' # 'on', 'off', 'running'
        self.runningState = 'preheating' # 'preheating', 'heating', 'cooling'
        self.mode = 'manual' # 'manual', 'auto'
        self.modBus = ModBus()
        
        self.powerControl = PowerControl()
        self.pid = PID(30, 0.2, 400)

        self.referenceTemperature = 0
        self.currentInternalTemperature = 0
        self.currentExternalTemperature = 0
        self.referenceTime = 0
        self.timeLeft = 0

        self.lcd = LCDController()
        self.lcd.init_lcd()
        self.lcd.turn_off_lcd_backlight()

        self.externalTemperatureSensor = Bmp280()

        self.presets = [
            {'name': 'Frango', 'referenceTime': 30, 'referenceTemperature': 55},
            {'name': 'Batata', 'referenceTime': 60, 'referenceTemperature': 65},
            {'name': 'Waffle', 'referenceTime': 25, 'referenceTemperature': 50}
        ]

    def handle_SIGALRM(self, _signum, _frame):
        self.controle()

    def controle(self):
        self.updateTemperatures()

        if self.state == 'on':
            self.lcd.lcd_string('Modo: Manual', self.lcd.LCD_LINE_1)
            # self.lcd_string('Modo: Automatico - Frango', self.LCD_LINE_1)

            self.lcd.lcd_string('Ref.: {:05.2f}*C'.format(self.referenceTemperature), self.lcd.LCD_LINE_2)
            # self.lcd_string('Tempo: 1min', self.LCD_LINE_2) self.referenceTime


        if self.state == 'running':
            signal.alarm(1)

            lcdLineOne = ''
            lcdLineTwo = ''
            if self.mode == 'manual':
                lcdLineOne = 'TI: {:.1f} *C Ref.: {:.1f} *C'.format(self.currentInternalTemperature, self.referenceTemperature)
               
                if self.runningState == 'cooling':
                    lcdLineTwo = 'Esfriando...'
                elif self.runningState == 'heating':
                    lcdLineTwo =  'Aquecendo...'
            elif self.mode == 'auto':
                self.timeLeft -= self.timeLeft
                lcdLineOne = 'TI: {:.1f} *C Ref.: {:.1f} *C'.format(self.currentInternalTemperature, self.referenceTemperature)
                # lcdLineOne = 'Frango - 50*C' todo pensar melhor
                if self.runningState == 'preheating':
                    lcdLineTwo = 'Pre-aquecendo...'
                elif self.runningState == 'cooling':
                    lcdLineTwo = 'Esfriando...'
                elif self.runningState == 'heating':
                    minutes, seconds = divmod(self.timeLeft, 60)
                    lcdLineTwo =  'Tempo: {:02d}:{:02d}'.format(minutes, seconds)

            self.lcd.lcd_string(lcdLineOne, self.lcd.LCD_LINE_2)
            self.lcd.lcd_string(lcdLineTwo, self.lcd.LCD_LINE_2)

            self.pid.updateReference(self.referenceTemperature)

            pidSignal = self.pid.pidControl(self.currentInternalTemperature)

            self.sendPidSignal(pidSignal)

            if pidSignal < 0:
                pidSignal *= -1
                self.powerControl.set_FAN_pwm(pidSignal)
            else:
                self.powerControl.set_resistor_pwm(pidSignal)

            print("SIGALRM received!")


    def updateTemperatures(self):
        self.modBus.write(0x01, 0x23, 0xC1 , (1, 6 ,0 , 2), None)
        time.sleep(0.2)
        data = self.modBus.read()
        if data != -1  and data != None:
            self.currentInternalTemperature = data['value']
        
        self.modBus.write(0x01, 0x23, 0xC2 , (1, 6 ,0 , 2), None)
        time.sleep(0.2)
        data = self.modBus.read()
        if data != -1  and data != None:
            self.referenceTemperature = data['value']

        self.currentExternalTemperature = self.externalTemperatureSensor.getTemperature()

        self.modBus.write(0x01, 0x16, 0xD6 , (1, 6 ,0 , 2), self.currentExternalTemperature)
        

    def mainLoop(self):
        while True:
            data = self.readUserCommands()
            print('readUserCommands',data)

            if data != -1 and data != None:
                if data['subcode'] == 0xC3:
                    if data['value'] == 0x01:
                        self.stateToOn()
                    elif data['value'] == 0x02:
                        self.stateToOff()
                    elif data['value'] == 0x03:
                        self.startRunning()
                    elif data['value'] == 0x04:
                        self.stopRunning()
                    elif data['value'] == 0x05:
                        self.incrementTime()
                    elif data['value'] == 0x06:
                        self.decrementTime()
                    elif data['value'] == 0x07:
                        self.toggleMode()
            time.sleep(0.2)

    def startRunning(self):
        self.state = 'running'
        if self.mode == 'auto':
            self.timeLeft = self.referenceTime
        self.controle()
        self.modBus.write(0x01, 0x16, 0xD5, (1, 6 ,0 , 2), 0b1)
        time.sleep(0.2)
        self.modBus.read()

    def stopRunning(self):
        self.state = 'on'
        self.sendPidSignal(0)
        self.powerControl.stop_pwm()


    def incrementTime(self):
        pass

    def decrementTime(self):
        pass

    def toggleMode(self):
        mode = 0b0
        if self.mode == 'auto':
            self.mode = 'manual'
        elif self.mode == 'manual':
            self.mode = 'auto'
            randomPreset = random.choice(self.presets)
            self.referenceTime = randomPreset['referenceTime']
            self.referenceTemperature = randomPreset['referenceTemperature']
            self.sendReferenceTemperature()
            mode = 0b1

        self.modBus.write(0x01, 0x16, 0xD4, (1, 6 ,0 , 2), mode)
        time.sleep(0.2)
        self.modBus.read()

    def stateToOn(self):
        self.state = 'on'
        # turn lcd on
        self.lcd.turn_on_lcd_backlight()
        self.modBus.write(0x01, 0x16, 0xD3, (1, 6 ,0 , 2), 0b1)
        time.sleep(0.2)
        self.modBus.read()


    def controleOff(self, _signum, _frame):
        self.stateToOff()
        # close uart

    def stateToOff(self):
        self.state = 'off'
        self.powerControl.stop_pwm()
        self.lcd.turn_off_lcd_backlight()
        self.modBus.write(0x01, 0x16, 0xD3, (1, 6 ,0 , 2), 0)
        time.sleep(0.2)
        self.modBus.read()

    def updateCurrentExternalTemperature(self):
        self.currentExternalTemperature = self.externalTemperatureSensor.getTemperature()

    def sendPidSignal(self, pidSignal):
        self.modBus.write(0x01, 0x16, 0xD1 , (1, 6 ,0 , 2), pidSignal)

    def sendReferenceTemperature(self):
        self.modBus.write(0x01, 0x16, 0xD2 , (1, 6 ,0 , 2), self.referenceTemperature)
   

    def readUserCommands(self):
        self.modBus.write(0x01, 0x23, 0xC3 , (1, 6 ,0 , 2), None)
        time.sleep(0.2)
        return self.modBus.read()