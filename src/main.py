import signal
import time

# Signal handler function
def controle(_signum, _frame):
    signal.alarm(1)

    print("SIGALRM received!")


# Register the signal handler for SIGALRM
signal.signal(signal.SIGALRM, controle)

# Set an alarm to trigger after 5 seconds

controle(0, 0)
# signal.alarm(1)
# main loop


def comandos():
    time.sleep(0.3)

while True:
    comandos()