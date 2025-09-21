import os
import time
from pathlib import Path
from PIL import ImageGrab
import subprocess
import platform

class Maksim132:
    def __init__(self):
        self.screenshot = None
        self.filename = None
        self.desktop_path = Path.home() / "Desktop"
        
        # Создаем папку Desktop если её нет
        self.desktop_path.mkdir(exist_ok=True)
    
    def screenshot(self):
        """Делает скриншот экрана"""
        try:
            # Делаем скриншот
            self.screenshot = ImageGrab.grab()
            print("Скриншот сделан успешно!")
            return self
        except Exception as e:
            print(f"Ошибка при создании скриншота: {e}")
            return self
    
    def save(self, filename=None):
        """Сохраняет скриншот на рабочий стол"""
        if self.screenshot is None:
            print("Сначала нужно сделать скриншот! Используйте .screenshot()")
            return self
        
        try:
            # Генерируем имя файла если не указано
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                self.filename = f"screenshot_{timestamp}.png"
            else:
                self.filename = filename
                if not self.filename.endswith('.png'):
                    self.filename += '.png'
            
            # Полный путь к файлу
            file_path = self.desktop_path / self.filename
            
            # Сохраняем скриншот
            self.screenshot.save(file_path)
            print(f"Скриншот сохранен: {file_path}")
            return self
            
        except Exception as e:
            print(f"Ошибка при сохранении скриншота: {e}")
            return self
    
    def open(self):
        """Открывает сохраненный скриншот"""
        if self.filename is None:
            print("Сначала нужно сохранить скриншот! Используйте .save()")
            return self
        
        try:
            file_path = self.desktop_path / self.filename
            
            if not file_path.exists():
                print(f"Файл не найден: {file_path}")
                return self
            
            # Открываем файл в зависимости от операционной системы
            system = platform.system()
            
            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(file_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(file_path)])
            
            print(f"Скриншот открыт: {file_path}")
            return self
            
        except Exception as e:
            print(f"Ошибка при открытии скриншота: {e}")
            return self