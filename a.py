import keyboard
from menu import Menu

myMenu = Menu()
myMenu.menu(None)

def on_up_arrow():
    myMenu.menu('right')

def on_down_arrow():
    myMenu.menu('left')

def on_backspace():
    myMenu.menu('doubleClick')

def on_enter():
    myMenu.menu('singleClick')
def listen_keyboard():
    while True:
        event = keyboard.read_event()
        if event.event_type == "down":
            if event.name == "home":
                on_up_arrow()
            elif event.name == "end":
                on_down_arrow()
            elif event.name == "backspace":
                on_backspace()
            elif event.name == "enter":
                on_enter()

listen_keyboard()
