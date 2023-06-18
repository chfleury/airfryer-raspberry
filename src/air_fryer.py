import signal
import time

from modbus.modbus import ModBus
from power.power_control import PowerControl
from pid.pid import PID
from lcd_display.lcd_display import LCDController
from log.csv_log import writeLog
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
        self.selectedPreset = None
        self.modBus = ModBus()
        
        self.powerControl = PowerControl()
        self.pid = PID(30, 0.2, 600)

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
            {'label': 'Frango', 'referenceTime': 30, 'referenceTemperature': 30},
            {'label': 'Batata', 'referenceTime': 60, 'referenceTemperature': 40},
            {'label': 'Waffle', 'referenceTime': 25, 'referenceTemperature': 35}
        ]


    def mainLoop(self):
        while True:
            data = self.readUserCommands()

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


    def controllLoop(self):
        print('time', self.timeLeft, self.referenceTime)
        self.updateTemperatures()
        self.pid.updateReference(self.referenceTemperature)
        signal.alarm(1)

        if self.state == 'on':
            if self.mode == 'manual':
                minutes, seconds = divmod(self.referenceTime, 60)

                self.lcd.lcd_string('Manual T:{:02d}:{:02d}'.format(minutes, seconds), self.lcd.LCD_LINE_1)
                self.lcd.lcd_string('TR:{:05.2f} TA:{:05.2f}'.format(self.referenceTemperature, self.currentExternalTemperature), self.lcd.LCD_LINE_2)

            else:
                self.lcd.lcd_string('Auto: ' + self.selectedPreset['label'], self.lcd.LCD_LINE_1)
                minutes, seconds = divmod(self.referenceTime, 60)
                self.lcd.lcd_string('TR:{:05.2f} T:{:02d}:{:02d}'.format(self.referenceTemperature, minutes, seconds), self.lcd.LCD_LINE_2)
            
            

        elif self.state == 'running':
            self.modBus.write(0x01, 0x16, 0xD7 , (1, 6 ,0 , 2), self.timeLeft)

            lcdLineOne = ''
            lcdLineTwo = ''
   
            lcdLineOne = 'TI:{:.1f} TR:{:.1f}'.format(self.currentInternalTemperature, self.referenceTemperature)
            if self.runningState == 'preheating':
                lcdLineTwo = 'Pre-aquecendo...'
                lowerLimit = self.referenceTemperature - (self.referenceTemperature * 0.05)
                upperLimit = self.referenceTemperature + (self.referenceTemperature * 0.05) 
                if lowerLimit <= self.currentInternalTemperature <= upperLimit:
                    self.runningState = 'heating'
            elif self.runningState == 'cooling':
                self.pid.updateReference(self.currentExternalTemperature)
                lcdLineTwo = 'Esfriando...'
                lowerLimit = self.currentExternalTemperature - (self.currentExternalTemperature * 0.2)
                upperLimit = self.currentExternalTemperature + (self.currentExternalTemperature * 0.2) 
                if lowerLimit <= self.currentInternalTemperature <= upperLimit:
                    self.runningState = 'preheating'
                    self.stopRunning()
            elif self.runningState == 'heating':
                self.timeLeft -= 1

                minutes, seconds = divmod(self.timeLeft, 60)
                lcdLineTwo =  'Tempo: {:02d}:{:02d}'.format(minutes, seconds)
                if self.timeLeft < 1:
                    self.runningState = 'cooling'

            self.lcd.lcd_string(lcdLineOne, self.lcd.LCD_LINE_1)
            self.lcd.lcd_string(lcdLineTwo, self.lcd.LCD_LINE_2)

            pidSignal = int(round(self.pid.pidControl(self.currentInternalTemperature)))

            self.sendPidSignal(pidSignal)

            print('pidSignal', pidSignal)

            fanSignal = 0
            resistorSignal = 0
            if pidSignal < 0:
                pidSignal *= -1
                self.powerControl.set_FAN_pwm(pidSignal)
                self.powerControl.set_resistor_pwm(0)

                print('setou fan')
                fanSignal = pidSignal
            elif pidSignal > 0:
                self.powerControl.set_resistor_pwm(pidSignal)
                self.powerControl.set_FAN_pwm(0)

                print('setou resistor')
                resistorSignal = pidSignal

            writeLog(self.currentInternalTemperature, self.currentExternalTemperature, self.referenceTemperature, fanSignal, resistorSignal)
    
    
    def handle_SIGALRM(self, _signum, _frame):
        self.controllLoop()
    
    def updateTemperatures(self):
        self.modBus.write(0x01, 0x23, 0xC1 , (1, 6 ,0 , 2), None)
        time.sleep(0.2)
        data = self.modBus.read()
        if data != -1  and data != None:
            self.currentInternalTemperature = data['value']
            print('interna', self.currentInternalTemperature)
        
        if self.mode == 'manual':
            self.modBus.write(0x01, 0x23, 0xC2 , (1, 6 ,0 , 2), None)
            time.sleep(0.2)
            data = self.modBus.read()
            if data != -1  and data != None:
                self.referenceTemperature = data['value']

        self.currentExternalTemperature = self.externalTemperatureSensor.getTemperature()

        self.modBus.write(0x01, 0x16, 0xD6 , (1, 6 ,0 , 2), self.currentExternalTemperature)
        

    def startRunning(self):
        if self.referenceTime > 0:
            self.state = 'running'
            self.timeLeft = self.referenceTime
            self.modBus.write(0x01, 0x16, 0xD5, (1, 6 ,0 , 2), 0b1)
            time.sleep(0.2)
            self.modBus.read()

    def stopRunning(self):
        self.state = 'on'
        self.sendPidSignal(0)
        self.powerControl.stop_pwm()
        self.modBus.write(0x01, 0x16, 0xD5, (1, 6 ,0 , 2), 0b0)
        time.sleep(0.2)
        self.modBus.read()

    def incrementTime(self):
        self.referenceTime += 60
        self.modBus.write(0x01, 0x16, 0xD7 , (1, 6 ,0 , 2), self.referenceTime)


    def decrementTime(self):
        self.referenceTime -= 60
        if self.referenceTime < 0: self.referenceTime = 0
        self.modBus.write(0x01, 0x16, 0xD7 , (1, 6 ,0 , 2), self.referenceTime)


    def toggleMode(self):
        mode = 0b0
        if self.mode == 'auto':
            self.mode = 'manual'
        elif self.mode == 'manual':
            self.mode = 'auto'
            randomPreset = random.choice(self.presets)
            self.selectedPreset = randomPreset
            self.referenceTime = randomPreset['referenceTime']
            self.referenceTemperature = randomPreset['referenceTemperature']
            self.sendReferenceTemperature()
            mode = 0b1
            
            self.modBus.write(0x01, 0x16, 0xD7 , (1, 6 ,0 , 2), self.timeLeft)


        self.modBus.write(0x01, 0x16, 0xD4, (1, 6 ,0 , 2), mode)
        time.sleep(0.2)
        self.modBus.read()

    def stateToOn(self):
        self.state = 'on'
        self.controllLoop()
        self.lcd.turn_on_lcd_backlight()
        self.modBus.write(0x01, 0x16, 0xD3, (1, 6 ,0 , 2), 0b1)
        time.sleep(0.2)
        self.modBus.read()


    def controleOff(self, _signum, _frame):
        self.stateToOff()
        self.modBus.close()
        exit()

    def stateToOff(self):
        self.state = 'off'
        self.powerControl.stop_pwm()
        
        self.modBus.write(0x01, 0x16, 0xD5, (1, 6 ,0 , 2), 0b0)
        time.sleep(0.2)
        self.modBus.read()

        self.lcd.turn_off_lcd_backlight()
        self.modBus.write(0x01, 0x16, 0xD3, (1, 6 ,0 , 2), 0)
        time.sleep(0.2)
        self.modBus.read()

    def sendPidSignal(self, pidSignal):
        self.modBus.write(0x01, 0x16, 0xD1 , (1, 6 ,0 , 2), int(round(pidSignal)))

    def sendReferenceTemperature(self):
        self.modBus.write(0x01, 0x16, 0xD2 , (1, 6 ,0 , 2), self.referenceTemperature)
   

    def readUserCommands(self):
        self.modBus.write(0x01, 0x23, 0xC3 , (1, 6 ,0 , 2), None)
        time.sleep(0.2)
        return self.modBus.read()