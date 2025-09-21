import os
import time
from pathlib import Path
from PIL import ImageGrab
import subprocess
import platform

class Maksim132:
    def __init__(self):
        self.desktop_path = Path.home() / "Desktop"
        self.desktop_path.mkdir(exist_ok=True)
    
    def screenshot(self):
        """Делает скриншот экрана и возвращает объект изображения"""
        try:
            screenshot = ImageGrab.grab()
            print("Скриншот сделан успешно!")
            return screenshot
        except Exception as e:
            print(f"Ошибка при создании скриншота: {e}")
            return None
    
    def save(self, screenshot, filename=None):
        """Сохраняет скриншот на рабочий стол"""
        if screenshot is None:
            print("Нет скриншота для сохранения!")
            return None
        
        try:
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            elif not filename.endswith('.png'):
                filename += '.png'
            
            file_path = self.desktop_path / filename
            screenshot.save(file_path)
            print(f"Скриншот сохранен: {file_path}")
            return filename
            
        except Exception as e:
            print(f"Ошибка при сохранении скриншота: {e}")
            return None
    
    def open(self, filename):
        """Открывает сохраненный скриншот"""
        try:
            file_path = self.desktop_path / filename
            
            if not file_path.exists():
                print(f"Файл не найден: {file_path}")
                return
            
            system = platform.system()
            
            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":
                subprocess.run(["open", str(file_path)])
            else:
                subprocess.run(["xdg-open", str(file_path)])
            
            print(f"Скриншот открыт: {file_path}")
            
        except Exception as e:
            print(f"Ошибка при открытии скриншота: {e}")