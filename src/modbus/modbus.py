from crc  import crc
from uart import uart
import struct

class ModBus:
    def __init__(self):
        self.uart = uart.init_UART()

    def write(self, target_address, code, subcode, matricula, data):
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

        tx_buffer = struct.pack('h', crc.calcula_CRC(tx_buffer, p_tx_buffer))
        p_tx_buffer += 2

        uart.write_UART(self.uart, tx_buffer)
        #    printf("Digite o comando: ");
        # scanf("%x", &command);

        # unsigned int matricula[TAMANHO_MATRICULA] = {1, 6, 0, 2};
        # unsigned char tx_buffer[300];
        # unsigned char *p_tx_buffer;

        # p_tx_buffer = &tx_buffer[0];

        # // ADDRESS FIELD
        # *p_tx_buffer++ = target_device_address;
        # // CODE FIELD
        # *p_tx_buffer++ = mod_bus_code;

        # // DATA FIELD
        # memcpy(p_tx_buffer++, &command, 1);

        # if (command == 0xB1)
        # {
        #     int data;
        #     printf("Digite o inteiro a ser enviado.\n");

        #     scanf("%d", &data);

        #     memcpy(p_tx_buffer, &data, sizeof(data));
        #     p_tx_buffer += sizeof(data);
        # }
        # else if (command == 0xB2)
        # {
        #     float data;
        #     printf("Digite o float a ser enviado.\n");

        #     scanf("%f", &data);

        #     memcpy(p_tx_buffer, &data, sizeof(data));
        #     p_tx_buffer += sizeof(data);
        # }
        # else if (command == 0xB3)
        # {
        #     printf("Digite o tamanho da string a ser enviada.\n");
        #     int size;
        #     scanf("%d", &size);

        #     printf("Digite a string a ser enviada.\n");
        #     char data[256];

        #     scanf("%s", data);

        #     memcpy(p_tx_buffer++, &size, 1);
        #     memcpy(p_tx_buffer, &data[0], size);
        #     p_tx_buffer += size;
        # }

        # // for (int i = 0; i < TAMANHO_MATRICULA; i++)
        # // {
        # //     memcpy(p_tx_buffer++, &matricula[i], 1);
        # // }

        # // TODO
        # memcpy(p_tx_buffer++, &matricula[0], 1);
        # memcpy(p_tx_buffer++, &matricula[1], 1);
        # memcpy(p_tx_buffer++, &matricula[2], 1);
        # memcpy(p_tx_buffer++, &matricula[3], 1);

        # // CRC FIELD
        # int data_field_size = (p_tx_buffer - &tx_buffer[0]) - 2;
        # short CRC_16 = calcula_CRC(&tx_buffer[2], data_field_size);
        # memcpy(p_tx_buffer, &CRC_16, sizeof(CRC_16));

        # p_tx_buffer += sizeof(CRC_16);

        # printf("Buffers de memória criados!\n");

        # printf("Escrevendo caracteres na UART ...");

        # int count = write(uart0_filestream, &tx_buffer[0], (p_tx_buffer - &tx_buffer[0]));
        # if (count < 0)
        # {
        #     printf("UART TX error\n");
        # }
        # else
        # {
        #     printf("escrito.%d\n", count);
        # }
        # sleep(1);

x = ModBus()

x.write(0x01, 0x23, 0xC1 , (1, 6 ,0 , 2), False)