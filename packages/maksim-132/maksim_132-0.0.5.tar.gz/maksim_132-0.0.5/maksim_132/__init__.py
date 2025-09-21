"""
Библиотека maksim_132 для управления сервомотором через Arduino
Автор: Максим Рогов
"""

from .servo_controller import ServoController

# Глобальный экземпляр
_servo_instance = None

def init(port='COM4', baudrate=9600):
    """
    Инициализация соединения с Arduino
    
    Args:
        port (str): COM порт (COM3, COM4, etc.)
        baudrate (int): Скорость передачи (по умолчанию 9600)
    """
    global _servo_instance
    _servo_instance = ServoController(port, baudrate)
    return _servo_instance

def servo(angle):
    """
    Поворот сервомотора на указанный угол
    
    Args:
        angle (int): Угол поворота (0-180 градусов)
    """
    global _servo_instance
    if _servo_instance is None:
        _servo_instance = ServoController()
    
    success = _servo_instance.set_angle(angle)
    if success:
        return f"Сервомотор повернут на {angle}°"
    else:
        return f"Ошибка поворота на {angle}°"

def sweep(start=0, end=180, step=10, delay=0.3):
    """
    Плавное движение сервомотора между углами
    """
    global _servo_instance
    if _servo_instance is None:
        _servo_instance = ServoController()
    
    _servo_instance.sweep(start, end, step, delay)

def cleanup():
    """Закрытие соединения с Arduino"""
    global _servo_instance
    if _servo_instance:
        _servo_instance.close()
    _servo_instance = None