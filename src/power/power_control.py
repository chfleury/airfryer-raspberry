import wiringpi

class PowerControl:
    def __init__(self):
        self.RESISTOR_PIN = 23
        self.FAN_PIN = 23

    def init_power_control(self):
        wiringpi.wiringPiSetup()

        wiringpi.softPwmCreate(self.RESISTOR_PIN, 0, 100)
        wiringpi.softPwmCreate(self.FAN_PIN, 0, 100)

    def set_resistor_pwm(self, signal):
        if signal > 100:
            signal = 100
        elif signal < 0:
            signal = 0
        wiringpi.softPwmWrite(self.RESISTOR_PIN, signal)

    def set_FAN_pwm(self, signal):
        if signal > 0:
            if signal < 40:
                signal = 40
            wiringpi.softPwmWrite(self.FAN_PIN, signal)
        else:
            wiringpi.softPwmWrite(self.FAN_PIN, 0)

    def stop_pwm(self):
        wiringpi.softPwmWrite(self.RESISTOR_PIN, 0)
        wiringpi.softPwmWrite(self.FAN_PIN, 0)

# try:
#     while True:
#         signal = int(input("Digite o valor do sinal (-100 a 100): "))
#          controller = ResistorVentoinhaController(23, 24)
#         controller.init_wiringpi()
#         set_resistor_pwm(signal)
#         set_FAN_pwm(signal)
# except KeyboardInterrupt:
#     pass
# finally:
