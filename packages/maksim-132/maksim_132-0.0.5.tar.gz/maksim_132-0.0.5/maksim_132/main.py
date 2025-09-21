#!/usr/bin/env python3
import serial
import time
import sys

class ServoController:
    def __init__(self, port='COM4', baudrate=9600):
        """
        Контроллер сервомотора через Arduino
        
        Args:
            port (str): COM порт для подключения
            baudrate (int): Скорость передачи данных
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.connected = False
        
        self._connect()
    
    def _connect(self):
        """Установка соединения с Arduino"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Даем время Arduino на инициализацию
            time.sleep(2)
            
            # Очищаем буфер
            self.ser.reset_input_buffer()
            
            self.connected = True
            print(f"✅ Подключено к Arduino на порту {self.port}")
            
        except serial.SerialException as e:
            print(f"❌ Ошибка подключения к {self.port}: {e}")
            print("Проверьте:")
            print("1. Подключена ли Arduino к компьютеру")
            print("2. Правильный ли COM порт")
            print("3. Загружен ли скетч на Arduino")
            self.connected = False
            
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            self.connected = False
    
    def set_angle(self, angle):
        """
        Установка угла поворота сервомотора
        
        Args:
            angle (int): Угол от 0 до 180 градусов
            
        Returns:
            bool: True если успешно, False если ошибка
        """
        if not self.connected or self.ser is None:
            print("❌ Нет соединения с Arduino")
            return False
        
        if angle < 0 or angle > 180:
            print("❌ Угол должен быть от 0 до 180 градусов")
            return False
        
        try:
            # Отправка команды в формате: "ANGLE:90\n"
            command = f"ANGLE:{angle}\n"
            self.ser.write(command.encode('utf-8'))
            
            # Ждем ответ от Arduino
            time.sleep(0.1)
            
            # Читаем ответ
            if self.ser.in_waiting > 0:
                response = self.ser.readline().decode('utf-8').strip()
                print(f"📨 Ответ Arduino: {response}")
            
            print(f"✅ Команда отправлена: угол {angle}°")
            return True
            
        except serial.SerialException as e:
            print(f"❌ Ошибка связи с Arduino: {e}")
            self.connected = False
            return False
            
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return False
    
    def sweep(self, start=0, end=180, step=10, delay=0.3):
        """
        Плавное движение сервомотора между углами
        """
        if not self.connected:
            print("❌ Нет соединения с Arduino")
            return
        
        print(f"🔄 Плавное движение от {start}° до {end}°")
        
        # Движение вперед
        for angle in range(start, end + 1, step):
            if self.set_angle(angle):
                time.sleep(delay)
        
        # Движение назад
        for angle in range(end, start - 1, -step):
            if self.set_angle(angle):
                time.sleep(delay)
    
    def close(self):
        """Закрытие соединения"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("🔌 Соединение с Arduino закрыто")
        self.connected = False
    
    def __del__(self):
        """Деструктор - автоматическое закрытие соединения"""
        self.close()