import keyboard

def on_up_arrow():
    print("Seta para cima pressionada")

def on_down_arrow():
    print("Seta para baixo pressionada")

def on_backspace():
    print("Backspace pressionado")

def on_enter():
    print("Enter pressionado")

def listen_keyboard():
    while True:
        event = keyboard.read_event()
        if event.event_type == "down":
            if event.name == "up":
                on_up_arrow()
            elif event.name == "down":
                on_down_arrow()
            elif event.name == "backspace":
                on_backspace()
            elif event.name == "enter":
                on_enter()

listen_keyboard()