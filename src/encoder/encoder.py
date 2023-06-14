import RPi.GPIO as GPIO
import threading
import time
# pullup pull down
SW_GPIO = 7
DT_GPIO = 8
CLK_GPIO = 25

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SW_GPIO, GPIO.IN,  pull_up_down=GPIO.PUD_UP)  # SW_GPIO
GPIO.add_event_detect(SW_GPIO ,GPIO.FALLING) # FALLING EVENT
GPIO.setup(DT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   # DT_GPIO
GPIO.setup(CLK_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # CLK_GPIO   


def handleEncoder():
    delta = 0
    CLK_reference = bool(GPIO.input(CLK_GPIO))  
    estadoBotao = GPIO.HIGH  # Estado atual do botão
    ultimoEstadoBotao = GPIO.HIGH  # Estado anterior do botão
    contadorCliques = 0  # Contador de cliques
    tempoLimite = 0.25  # Tempo limite entre os cliques duplos (em segundos)
    tempoUltimoClique = 0  # Tempo em que o último clique ocorreu

    while True:
        CLK = bool(GPIO.input(CLK_GPIO))
        DT = bool(GPIO.input(DT_GPIO))
        estadoBotao =  GPIO.input(SW_GPIO)

        # Verificar se houve uma mudança de estado
        if estadoBotao != ultimoEstadoBotao:
            time.sleep(0.01)
            
            # Verificar se o botão foi pressionado (passou de HIGH para LOW)
            if estadoBotao == GPIO.LOW:
                # Verificar se ocorreu um clique duplo dentro do tempo limite
                if (time.time() - tempoUltimoClique) < tempoLimite:
                    contadorCliques = 2  # Clique duplo detectado
                else:
                    contadorCliques += 1  # Contabilizar clique único
                tempoUltimoClique = time.time()  # Atualizar o tempo do último clique

        # Atualizar o estado anterior do botão
        ultimoEstadoBotao = estadoBotao

        # Realizar ações com base no número de cliques detectados
        if contadorCliques == 1 and (time.time() - tempoUltimoClique) > tempoLimite:
            # Ação para clique único
            print("Clique único detectado")
            contadorCliques = 0


        elif contadorCliques == 2:
            # Ação para clique duplo
            print("Clique duplo detectado")

        # Reiniciar o contador de cliques após realizar as ações
        if contadorCliques >= 2:
            contadorCliques = 0

        # Pequeno atraso para evitar detecção falsa de cliques

        if CLK != CLK_reference:
            if DT != CLK:
                delta += 1
            else:
                delta -= 1
            # while bool(GPIO.input(CLK_GPIO)):
            #     pass
                
            print(delta)
           
            # time.sleep(0.003)
                
        CLK_reference = CLK
        



threading.Thread(target=handleEncoder).start()