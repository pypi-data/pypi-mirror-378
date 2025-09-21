import pygame
import threading
import time
from pygame import MOUSEMOTION

class MouseOverlay:
    def __init__(self):
        self.running = False
        self.thread = None
        self.color = (255, 0, 0)  # Красный по умолчанию
        self.size = 20
        self.cursor_type = "arrow"  # arrow, circle, cross
        
    def start_overlay(self):
        """Запускает поток с оверлеем курсора"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run_overlay, daemon=True)
        self.thread.start()
    
    def stop_overlay(self):
        """Останавливает оверлей"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def _run_overlay(self):
        """Основной цикл оверлея"""
        pygame.init()
        
        # Создаем прозрачное окно поверх всех окон
        screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
        pygame.display.set_caption("Mouse Overlay")
        
        # Делаем окно прозрачным и поверх всех окон
        screen.set_alpha(0)
        pygame.display.set_mode((0, 0), pygame.NOFRAME | pygame.FULLSCREEN)
        
        clock = pygame.time.Clock()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # Получаем позицию мыши
            x, y = pygame.mouse.get_pos()
            
            # Очищаем экран (прозрачный)
            screen.fill((0, 0, 0, 0))
            
            # Рисуем курсор в зависимости от типа
            if self.cursor_type == "arrow":
                self._draw_arrow(screen, x, y)
            elif self.cursor_type == "circle":
                self._draw_circle(screen, x, y)
            elif self.cursor_type == "cross":
                self._draw_cross(screen, x, y)
            
            pygame.display.flip()
            clock.tick(60)  # 60 FPS
        
        pygame.quit()
    
    def _draw_arrow(self, screen, x, y):
        """Рисует стрелку"""
        points = [
            (x, y),
            (x + self.size, y),
            (x + self.size * 0.8, y + self.size * 0.3),
            (x + self.size, y + self.size * 0.3),
            (x, y + self.size)
        ]
        pygame.draw.polygon(screen, self.color, points)
    
    def _draw_circle(self, screen, x, y):
        """Рисует кружок"""
        pygame.draw.circle(screen, self.color, (x, y), self.size // 2, 2)
        pygame.draw.circle(screen, self.color, (x, y), 2)
    
    def _draw_cross(self, screen, x, y):
        """Рисует крестик"""
        length = self.size // 2
        pygame.draw.line(screen, self.color, (x - length, y), (x + length, y), 2)
        pygame.draw.line(screen, self.color, (x, y - length), (x, y + length), 2)

# Глобальный экземпляр оверлея
_overlay = MouseOverlay()

def mousecolor(color_name, size=20, cursor_type="arrow"):
    """
    Меняет цвет виртуального курсора
    
    Args:
        color_name (str): название цвета ('red', 'green', 'blue', etc.)
        size (int): размер курсора (по умолчанию 20)
        cursor_type (str): тип курсора ('arrow', 'circle', 'cross')
    """
    color_map = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'purple': (128, 0, 128),
        'orange': (255, 165, 0),
        'pink': (255, 192, 203),
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'lime': (0, 255, 0),
        'maroon': (128, 0, 0),
        'navy': (0, 0, 128),
        'olive': (128, 128, 0),
        'teal': (0, 128, 128),
        'silver': (192, 192, 192),
        'gray': (128, 128, 128)
    }
    
    color = color_map.get(color_name.lower(), (255, 0, 0))
    
    _overlay.color = color
    _overlay.size = size
    _overlay.cursor_type = cursor_type
    
    if not _overlay.running:
        _overlay.start_overlay()

def stop():
    """Останавливает виртуальный курсор"""
    _overlay.stop_overlay()