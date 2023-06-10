import serial

def init_UART():
    print('chegou aqui')
    try:
        port = '/dev/serial0'  # Replace with the actual port name (e.g., '/dev/ttyUSB0' on Linux)
        baud_rate = 9600  # Set the baud rate
        timeout = 0
        uart0_filestream = serial.Serial(port, baud_rate, timeout=timeout)

        uart0_filestream.open()
 
        return uart0_filestream
    except serial.SerialException as e:

        print(f"Failed to open the serial port: {str(e)}")

def write_UART(uart0_filestream, buffer):
    if uart0_filestream:
        uart0_filestream.write(buffer)
    else:
        print('failed to write')
 
def read_UART(uart0_filestream):
    if uart0_filestream:
        data = uart0_filestream.read()
        return data
    else:
        print('failed to read')
        return -1