import serial

class Uart:
    def __init__(self):
        self.uart0_filestream = 0

    def init_UART(self):
        print('chegou aqui')
        try:
            port = '/dev/serial0'
            baud_rate = 9600
            timeout = 0
            self.uart0_filestream = serial.Serial(port, baud_rate, timeout=timeout)
            if self.uart0_filestream.is_open:
                print("Serial port is already open.")
            else:
                self.uart0_filestream.open()
                print("Serial port opened successfully.")

            return self.uart0_filestream
        except serial.SerialException as e:

            print(f"Failed to open the serial port: {str(e)}")

    def write_UART(self, buffer):
        if self.uart0_filestream:
            self.uart0_filestream.write(buffer)
        else:
            print('failed to write')
    
    def read_UART(self):
        if self.uart0_filestream:
            data_buffer = bytearray()

            data = self.uart0_filestream.read(300)
            if data:
                data_buffer.extend(data)
                return data_buffer
            else:
                return 0
        else:
            print('failed to read')
            return -1

    def close_UART(self):
        self.uart0_filestream.close()