from crc  import crc
from uart import uart
import struct

class ModBus:
    def __init__(self):
        self.myAddress = 0x00
        self.uart = uart.Uart()
        self.uart.init_UART()

    def write(self, target_address, code, subcode, matricula, data):
        try:
            print(self, target_address, code, subcode, matricula, data)
            tx_buffer = bytearray()
            p_tx_buffer = 0

            tx_buffer += struct.pack('B', target_address)
            tx_buffer += struct.pack('B', code)
            tx_buffer += struct.pack('B', subcode)
            tx_buffer += struct.pack('B', matricula[0])
            tx_buffer += struct.pack('B', matricula[1])
            tx_buffer += struct.pack('B', matricula[2])
            tx_buffer += struct.pack('B', matricula[3])
            p_tx_buffer += 7

            if subcode >= 0xD1 and subcode <= 0xD7:
                tx_buffer += struct.pack('I', data)
                p_tx_buffer += 4
            elif subcode == 0xD8:
                strLen = len(data)
                tx_buffer += struct.pack('B', strLen)
                tx_buffer += data.encode()
                p_tx_buffer += strLen

            tx_buffer += struct.pack('h', crc.calcula_CRC(tx_buffer, p_tx_buffer))
            p_tx_buffer += 2


            for i in tx_buffer:
                print(i)
            self.uart.write_UART(tx_buffer)
        except Exception as e:
            print(e)


    def read(self):
        data_buffer = self.uart.read_UART()
        index = 0
        if data_buffer != 0 and data_buffer != 1:
            if data_buffer[index] != self.myAddress:
                return -1
            index += 1


        
x = ModBus()

x.write(0x01, 0x16, 0xD8 , (1, 6 ,0 , 2), "jairo")