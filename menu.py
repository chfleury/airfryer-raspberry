import os

class Menu:
    def __init__(self):
        self.modes = ['Automatico', 'Manual']
        self.presets = [
            {'label': 'Frango', 'referenceTime': 30, 'referenceTemperature': 30},
            {'label': 'Batata', 'referenceTime': 60, 'referenceTemperature': 40},
            {'label': 'Waffle', 'referenceTime': 25, 'referenceTemperature': 35}
        ]
        self.state = 'pickMode' # 'pickMode', 'pickPreset', 'pickTemperature', 'pickTime'
        self.index = 0
        self.referenceTemperature = 0
        self.referenceTime = 0
    def clear(self):
        if os.name == 'posix':
            os.system('clear')
        if os.name == 'nt':  # Windows
            os.system('cls')
    def menu(self, command):
        self.clear()
        if self.state == 'pickMode':
            print('Escolha um Modo:')
 
            if command == None  or command == 'doubleClick':
                print('> ' + self.modes[0])
            if command == 'left' or command == 'right':
                self.index += 1
                rotated_index = self.index % len(self.modes)
                print('> ' + self.modes[rotated_index])
            if command == 'singleClick':
                if self.modes[self.index % len(self.modes)] ==  'Manual':
                    self.state = 'pickTemperature'
                    self.menu(None)
                    self.index == 0
                elif self.modes[self.index % len(self.modes)] ==  'Automatico':
                    self.state = 'pickPreset'
                    self.menu(None)
                    self.index == 0
        elif self.state == 'pickPreset':
            if command == None:
                print('Escolha um Alimento:'),
                print('> ' + self.presets[0]['label'])

            if command == 'left' or command == 'right':
                if command == 'right':
                    self.index += 1
                elif command == 'left':
                    self.index -= 1
                rotated_index = self.index % len(self.presets)
                print('Escolha um Alimento:')
                print('> '+self.presets[rotated_index]['label'])
            if command == 'doubleClick':
                self.state = 'pickMode'
                self.index = 0
                self.menu(None)
                
            if command == 'singleClick':
                rotated_index = self.index % len(self.presets)

                print('Você escolheu '+ self.presets[rotated_index]['label'],'Temperatura '+ str(self.presets[rotated_index]['referenceTemperature'])+ '*C', 'Tempo: '+ str(self.presets[rotated_index]['referenceTime']) + 'min')
                exit()
        elif self.state == 'pickTemperature':
            if command == None or command == 'doubleClick':
                print('Escolha a Temperatura:'),
                print('0 *C')
            if command == 'left' or command == 'right':
                if command == 'right':
                    self.referenceTemperature += 5
                    if self.referenceTemperature > 100:
                        self.referenceTemperature = 100
                elif command == 'left':
                    self.referenceTemperature -= 5
                    if self.referenceTemperature < 0:
                        self.referenceTemperature = 0
                print('Escolha a Temperatura:'),
                print(str(self.referenceTemperature)+' *C')
            if command == 'doubleClick':
                self.state = 'pickMode'
                self.index = 0
                self.menu(None)
            if command == 'singleClick':
                self.state = 'pickTime'
                self.menu(None)
        elif self.state == 'pickTime':
            if command == None:
                print('Escolha o tempo(min):'),
                print('0min')
            if command == 'left' or command == 'right':
                if command == 'right':
                    self.referenceTime += 1
                elif command == 'left':
                    self.referenceTime -= 1
                    if self.referenceTime < 0:
                        self.referenceTime = 0
                print('Escolha o tempo(min):'),
                print(str(self.referenceTime) +'min')
            if command == 'doubleClick':
                self.state = 'pickTemperature'
                self.referenceTemperature = 0
                self.menu(None)
            if command == 'singleClick':
                print('Você escolheu '+ str(self.referenceTemperature), '*C por', self.referenceTime, 'minutos')
                exit()