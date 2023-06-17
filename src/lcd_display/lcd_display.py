import smbus
import time

class LCDController:
    def __init__(self):
        self.I2C_ADDR = 0x27  
        self.LCD_WIDTH = 16  

        self.LCD_CHR = 1  
        self.LCD_CMD = 0  

        self.LCD_LINE_1 = 0x80  
        self.LCD_LINE_2 = 0xC0  
        self.LCD_LINE_3 = 0x94  
        self.LCD_LINE_4 = 0xD4  

        self.LCD_BACKLIGHT_ON = 0x08  
        self.LCD_BACKLIGHT_OFF = 0x00  

        self.ENABLE = 0b00000100  

        self.E_PULSE = 0.0005
        self.E_DELAY = 0.0005

        self.bus = smbus.SMBus(1)  

        self.lcd_backlight_state = 0x00

    def init_lcd(self):
        self.lcd_byte(0x33, self.LCD_CMD)  
        self.lcd_byte(0x32, self.LCD_CMD)  
        self.lcd_byte(0x06, self.LCD_CMD)  
        self.lcd_byte(0x0C, self.LCD_CMD)  
        self.lcd_byte(0x28, self.LCD_CMD)  
        self.lcd_byte(0x01, self.LCD_CMD)  
        time.sleep(self.E_DELAY)

    def lcd_byte(self, bits, mode):
        bits_high = mode | (bits & 0xF0) | self.lcd_backlight_state
        bits_low = mode | ((bits << 4) & 0xF0) | self.lcd_backlight_state

        self.bus.write_byte(self.I2C_ADDR, bits_high)
        self.lcd_toggle_enable(bits_high)

        self.bus.write_byte(self.I2C_ADDR, bits_low)
        self.lcd_toggle_enable(bits_low)

    def lcd_toggle_enable(self, bits):
        time.sleep(self.E_DELAY)
        self.bus.write_byte(self.I2C_ADDR, (bits | self.ENABLE))
        time.sleep(self.E_PULSE)
        self.bus.write_byte(self.I2C_ADDR, (bits & ~self.ENABLE))
        time.sleep(self.E_DELAY)

    def lcd_string(self, message, line):
        message = message.ljust(self.LCD_WIDTH, " ")
        self.lcd_byte(line, self.LCD_CMD)
        for i in range(self.LCD_WIDTH):
            self.lcd_byte(ord(message[i]), self.LCD_CHR)

    def turn_off_lcd_backlight(self):
        self.lcd_backlight_state = self.LCD_BACKLIGHT_OFF
        self.lcd_string(' ', self.LCD_LINE_1)
        self.lcd_string(' ', self.LCD_LINE_2)
    def turn_on_lcd_backlight(self):
        self.lcd_backlight_state = self.LCD_BACKLIGHT_ON
        self.lcd_string(' ', self.LCD_LINE_1)
        self.lcd_string(' ', self.LCD_LINE_2)
