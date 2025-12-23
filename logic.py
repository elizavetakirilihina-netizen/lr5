import math
import random
from typing import List, Tuple, Optional


class Ball:
    """Класс для представления шарика"""
    
    def __init__(self, x: float, y: float, radius: float = 20, color: Tuple[int, int, int] = None):
        self.x = x
        self.y = y
        self.radius = radius
        
        # Случайный цвет, если не указан
        if color is None:
            self.color = (
                random.randint(50, 200),
                random.randint(50, 200),
                random.randint(50, 200)
            )
        else:
            self.color = color
        
        # Скорость движения
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        
        # Флаг для отслеживания, находится ли шарик в инвентаре
        self.in_inventory = False
    
    def update_position(self, screen_width: int, screen_height: int):
        """Обновляет позицию шарика с учётом границ экрана"""
        if self.in_inventory:
            return
        
        # Движение
        self.x += self.vx
        self.y += self.vy
        
        # Отражение от границ экрана
        if self.x - self.radius <= 0 or self.x + self.radius >= screen_width:
            self.vx = -self.vx
            self.x = max(self.radius, min(screen_width - self.radius, self.x))
        
        if self.y - self.radius <= 0 or self.y + self.radius >= screen_height:
            self.vy = -self.vy
            self.y = max(self.radius, min(screen_height - self.radius, self.y))
    
    def get_distance(self, other: 'Ball') -> float:
        """Вычисляет расстояние между центрами двух шариков"""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)
    
    def is_colliding(self, other: 'Ball') -> bool:
        """Проверяет столкновение с другим шариком"""
        if self.in_inventory or other.in_inventory:
            return False
        distance = self.get_distance(other)
        return distance < (self.radius + other.radius)
    
    def is_point_inside(self, x: float, y: float) -> bool:
        """Проверяет, находится ли точка внутри шарика"""
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx * dx + dy * dy) <= self.radius


def mix_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """
    Смешивает два цвета путём математического усреднения RGB компонентов.
    Универсальный метод, работающий для любых комбинаций цветов.
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    
    # Простое математическое усреднение RGB компонентов
    r = int((r1 + r2) / 2)
    g = int((g1 + g2) / 2)
    b = int((b1 + b2) / 2)
    
    # Обеспечиваем корректный диапазон значений [0, 255]
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    
    return (r, g, b)


class GameLogic:
    """Основной класс для управления игровой логикой"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Список всех шариков на экране
        self.balls: List[Ball] = []
        
        # Инвентарь (шарики, которые "всасаны")
        self.inventory: List[Ball] = []
        
        # Зона удаления (нижняя часть экрана)
        self.delete_zone_height = 80
        self.delete_zone_y = screen_height - self.delete_zone_height
        
        # Позиция мыши для интерактивности
        self.mouse_x = 0
        self.mouse_y = 0
        
        # Радиус "всасывания" вокруг мыши
        self.suction_radius = 50
    
    def add_ball(self, x: float = None, y: float = None, color: Tuple[int, int, int] = None) -> Ball:
        """Добавляет новый шарик на экран"""
        if x is None:
            x = random.randint(50, self.screen_width - 50)
        if y is None:
            y = random.randint(50, self.screen_height - 50)
        
        ball = Ball(x, y, color=color)
        self.balls.append(ball)
        return ball
    
    def update(self):
        """Обновляет состояние игры (вызывается каждый кадр)"""
        # Обновляем позиции всех шариков
        for ball in self.balls:
            ball.update_position(self.screen_width, self.screen_height)
        
        # Проверяем столкновения и смешиваем цвета
        self._handle_collisions()
        
        # Проверяем шарики в зоне удаления
        self._check_delete_zone()
    
    def _handle_collisions(self):
        """Обрабатывает столкновения между шариками"""
        # Проверяем все пары шариков
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                ball1 = self.balls[i]
                ball2 = self.balls[j]
                
                if ball1.is_colliding(ball2):
                    # Смешиваем цвета
                    new_color = mix_colors(ball1.color, ball2.color)
                    
                    # Применяем новый цвет обоим шарикам
                    ball1.color = new_color
                    ball2.color = new_color
                    
                    # Шарики не отталкиваются (как указано в требованиях)
                    # Они просто проходят друг через друга, меняя цвет
    
    def _check_delete_zone(self):
        """Удаляет шарики, попавшие в зону удаления"""
        balls_to_remove = []
        
        for ball in self.balls:
            if not ball.in_inventory:
                # Проверяем, находится ли шарик в зоне удаления
                if ball.y + ball.radius >= self.delete_zone_y:
                    balls_to_remove.append(ball)
        
        # Удаляем шарики из списка
        for ball in balls_to_remove:
            self.balls.remove(ball)
    
    def update_mouse_position(self, x: float, y: float):
        """Обновляет позицию мыши"""
        self.mouse_x = x
        self.mouse_y = y
    
    def try_suck_ball(self) -> Optional[Ball]:
        """
        Пытается "всасать" шарик в инвентарь, если он находится рядом с мышкой.
        Возвращает всасанный шарик или None.
        """
        for ball in self.balls:
            if ball.in_inventory:
                continue
            
            # Проверяем расстояние до мыши
            dx = ball.x - self.mouse_x
            dy = ball.y - self.mouse_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= self.suction_radius:
                # "Всасываем" шарик в инвентарь
                ball.in_inventory = True
                self.inventory.append(ball)
                return ball
        
        return None
    
    def spit_ball(self, index: int = None) -> Optional[Ball]:
        """
        "Выплёвывает" шарик из инвентаря обратно на экран.
        Если индекс не указан, берётся последний шарик.
        Возвращает выплюнутый шарик или None.
        """
        if not self.inventory:
            return None
        
        if index is None:
            index = len(self.inventory) - 1
        
        if 0 <= index < len(self.inventory):
            ball = self.inventory.pop(index)
            ball.in_inventory = False
            
            # Размещаем шарик рядом с мышкой
            ball.x = self.mouse_x + random.randint(-30, 30)
            ball.y = self.mouse_y + random.randint(-30, 30)
            
            # Обеспечиваем, что шарик не выходит за границы
            ball.x = max(ball.radius, min(self.screen_width - ball.radius, ball.x))
            ball.y = max(ball.radius, min(self.delete_zone_y - ball.radius, ball.y))
            
            # Даём шарику случайную скорость
            ball.vx = random.uniform(-3, 3)
            ball.vy = random.uniform(-3, 3)
            
            return ball
        
        return None
    
    def get_balls(self) -> List[Ball]:
        """Возвращает список всех шариков на экране"""
        return [ball for ball in self.balls if not ball.in_inventory]
    
    def get_inventory(self) -> List[Ball]:
        """Возвращает список шариков в инвентаре"""
        return self.inventory.copy()
    
    def get_delete_zone(self) -> Tuple[int, int, int, int]:
        """Возвращает координаты зоны удаления (x, y, width, height)"""
        return (0, self.delete_zone_y, self.screen_width, self.delete_zone_height)
    
    def is_in_delete_zone(self, x: float, y: float) -> bool:
        """Проверяет, находится ли точка в зоне удаления"""
        return y >= self.delete_zone_y
    
    def clear_all_balls(self):
        """Удаляет все шарики с экрана"""
        self.balls.clear()
        self.inventory.clear()
    
    def get_ball_at_position(self, x: float, y: float) -> Optional[Ball]:
        """Возвращает шарик, находящийся в указанной позиции, или None"""
        for ball in self.balls:
            if not ball.in_inventory and ball.is_point_inside(x, y):
                return ball
        return None

