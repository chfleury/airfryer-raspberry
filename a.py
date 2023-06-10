import struct


tx_buffer = bytearray()

tx_buffer += struct.pack('B', 0xC1)
tx_buffer += struct.pack('B', 33)
tx_buffer += struct.pack('B', 0xC1)

for i in tx_buffer:
    print(i)