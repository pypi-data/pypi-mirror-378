from .main import Maksim132

# Создаем экземпляр класса
_instance = Maksim132()

# Делаем методы доступными напрямую
def screenshot():
    return _instance.screenshot()

def save(screenshot, filename=None):
    return _instance.save(screenshot, filename)

def open(filename):
    return _instance.open(filename)