import wiringpi

class PowerControl:
    def __init__(self):
        self.RESISTOR_PIN = 23
        self.FAN_PIN = 24
        wiringpi.wiringPiSetup()
        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(self.RESISTOR_PIN, wiringpi.OUTPUT)
        wiringpi.pinMode(self.FAN_PIN, wiringpi.OUTPUT)

        wiringpi.softPwmCreate(self.RESISTOR_PIN, 0, 100)
        wiringpi.softPwmCreate(self.FAN_PIN, 0, 100)


    def set_resistor_pwm(self, signal):
        if signal > 100:
            signal = 100
        elif signal < 0:
            signal = 0
        print('pwm com singal', signal)
        wiringpi.softPwmWrite(self.RESISTOR_PIN, int(round(signal)))

    def set_FAN_pwm(self, signal):
        if signal > 0:
            if signal < 40:
                signal = 40
            print('wiringpi.softPwmWrite(self.FAN_PIN, signal)')
            wiringpi.softPwmWrite(self.FAN_PIN, int(round(signal)))
        else:
            wiringpi.softPwmWrite(self.FAN_PIN, 0)

    def stop_pwm(self):
        wiringpi.softPwmWrite(self.RESISTOR_PIN, 0)
        wiringpi.softPwmWrite(self.FAN_PIN, 0)

