from modbus import crc
import struct

from modbus.uart.uart import Uart
from modbus.crc.crc import calcula_CRC

class ModBus:
    def __init__(self):
        self.myAddress = 0x00
        self.uart = Uart()
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

            # print('subcode', subcode)

            if subcode == 0xD1  or subcode == 0xD7 :
                tx_buffer += struct.pack('I', data)
                p_tx_buffer += 4

            if subcode == 0xD2  or subcode == 0xD6:
                tx_buffer += struct.pack('f', data)
                p_tx_buffer += 4
            elif subcode == 0xD3 or subcode == 0xD4 or subcode == 0xD5:
                tx_buffer += struct.pack('B', data)
                p_tx_buffer += 1           
            elif subcode == 0xD8:
                strLen = len(data)
                tx_buffer += struct.pack('B', strLen)
                tx_buffer += data.encode()
                p_tx_buffer += strLen


            tx_buffer += struct.pack('H', calcula_CRC(tx_buffer, p_tx_buffer))
            p_tx_buffer += 2



            self.uart.write_UART(tx_buffer)
        except Exception as e:
            print(e)


    def read(self):
        data_buffer = self.uart.read_UART()

       
        # print(data_buffer)
        # print('len', len(data_buffer))
        index = 0
        data = {"code": 0x00, "subcode": 0x00, "value": 0}
        if data_buffer != 0 and data_buffer != 1:

            # for i in data_buffer:
            #     print('read  ',i)
            if data_buffer[index] != self.myAddress:
                return -1
            index += 1
            data['code'] = data_buffer[index]
            index += 1
            data['subcode'] = data_buffer[index]
            index += 1
            if data['subcode'] ==0xC1 or data['subcode'] == 0xC2:
                data['value'] = struct.unpack('f', data_buffer[index:index+4])[0]
            else:
                data['value'] = struct.unpack('I', data_buffer[index:index+4])[0]
            index += 4

            # print('index', index, index+2)

            crc = struct.unpack('H', data_buffer[index:index+2])[0]
            # print('data', data)
            # print('crc', crc,  calcula_CRC(data_buffer[:-2], len(data_buffer) - 2))
            if crc != calcula_CRC(data_buffer[:-2], len(data_buffer) - 2):
                return -1
            
            return data
        return -1
        
