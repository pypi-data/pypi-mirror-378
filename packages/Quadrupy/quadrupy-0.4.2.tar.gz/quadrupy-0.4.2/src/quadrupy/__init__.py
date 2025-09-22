from .core import STQV1

# Auto-connect global dog instance
_dog = STQV1()

def walk():
    _dog.walk()

def writeScreen(text):
    _dog.writeScreen(text)

def writeMotor(val):
    _dog.writeMotor(val)

def reset():
    _dog.reset()

def led(state):
    _dog.led(state)

def close():
    _dog.close()

