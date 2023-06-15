import RPi.GPIO as GPIO
import threading
import time
# pullup pull down

CLK_GPIO = 16
SW_GPIO = 21
DT_GPIO = 20

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SW_GPIO, GPIO.IN,  pull_up_down=GPIO.PUD_UP)  # SW_GPIO
GPIO.add_event_detect(SW_GPIO ,GPIO.FALLING) # FALLING EVENT
GPIO.setup(DT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   # DT_GPIO
GPIO.setup(CLK_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # CLK_GPIO   


def handleEncoder():
    delta = 0
    CLK_reference = bool(GPIO.input(CLK_GPIO))  
    buttonState = GPIO.HIGH
    lastButtonState = GPIO.HIGH
    clickCount = 0
    timeLimitToDoubleClick = 0.25
    lastClickTime = 0

    while True:
        CLK = bool(GPIO.input(CLK_GPIO))
        DT = bool(GPIO.input(DT_GPIO))
        buttonState =  GPIO.input(SW_GPIO)

        if buttonState != lastButtonState:
            time.sleep(0.01)
            
            if buttonState == GPIO.LOW:
                if (time.time() - lastClickTime) < timeLimitToDoubleClick:
                    clickCount = 2
                else:
                    clickCount += 1
                lastClickTime = time.time()

        lastButtonState = buttonState

        if clickCount == 1 and (time.time() - lastClickTime) > timeLimitToDoubleClick:
            print("Clique único detectado")
            clickCount = 0


        elif clickCount == 2:
            print("Clique duplo detectado")

        if clickCount >= 2:
            clickCount = 0

        if CLK != CLK_reference:
            if DT != CLK:
                delta += 1
            else:
                delta -= 1
                
            print(delta)
           
        time.sleep(0.0003)
                
        CLK_reference = CLK
        



threading.Thread(target=handleEncoder).start()