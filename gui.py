import pygame
import sys
from logic import GameLogic, Ball

# ==================== НАСТРОЙКИ ====================
# Стартовое количество шариков
STARTING_BALLS_COUNT = 15

# Размеры окна
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 100, 100)
DELETE_ZONE_COLOR = (255, 200, 200, 180)  # Полупрозрачный красный
# ===================================================


class Game:
    """Класс для управления игрой и графическим интерфейсом"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Игра про шарики")
        self.clock = pygame.time.Clock()
        
        # Инициализируем игровую логику
        self.game_logic = GameLogic(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Создаём стартовые шарики
        self._create_starting_balls()
        
        # Флаг для отслеживания зажатой кнопки мыши
        self.mouse_pressed = False
        self.mouse_button = None
        
        # Шрифт для текста
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def _create_starting_balls(self):
        """Создаёт стартовые шарики на экране"""
        for _ in range(STARTING_BALLS_COUNT):
            self.game_logic.add_ball()
    
    def _draw_ball(self, ball: Ball):
        """Отрисовывает шарик на экране"""
        if ball.in_inventory:
            return
        
        # Рисуем шарик с градиентом (внешний круг темнее)
        pygame.draw.circle(
            self.screen,
            ball.color,
            (int(ball.x), int(ball.y)),
            int(ball.radius)
        )
        
        # Добавляем обводку для лучшей видимости
        pygame.draw.circle(
            self.screen,
            (max(0, ball.color[0] - 30), max(0, ball.color[1] - 30), max(0, ball.color[2] - 30)),
            (int(ball.x), int(ball.y)),
            int(ball.radius),
            2
        )
        
        # Добавляем блик для объёма
        highlight_x = int(ball.x - ball.radius * 0.3)
        highlight_y = int(ball.y - ball.radius * 0.3)
        highlight_radius = int(ball.radius * 0.3)
        highlight_color = (
            min(255, ball.color[0] + 50),
            min(255, ball.color[1] + 50),
            min(255, ball.color[2] + 50)
        )
        pygame.draw.circle(
            self.screen,
            highlight_color,
            (highlight_x, highlight_y),
            highlight_radius
        )
    
    def _draw_delete_zone(self):
        """Отрисовывает зону удаления"""
        delete_zone_x, delete_zone_y, delete_zone_width, delete_zone_height = \
            self.game_logic.get_delete_zone()
        
        # Создаём полупрозрачную поверхность
        delete_surface = pygame.Surface((delete_zone_width, delete_zone_height), pygame.SRCALPHA)
        delete_surface.fill(DELETE_ZONE_COLOR)
        self.screen.blit(delete_surface, (delete_zone_x, delete_zone_y))
        
        # Рисуем границу зоны удаления
        pygame.draw.rect(
            self.screen,
            RED,
            (delete_zone_x, delete_zone_y, delete_zone_width, delete_zone_height),
            3
        )
        
        # Текст "Зона удаления"
        text = self.font.render("ЗОНА УДАЛЕНИЯ", True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, delete_zone_y + delete_zone_height // 2))
        self.screen.blit(text, text_rect)
    
    def _draw_inventory(self):
        """Отрисовывает информацию об инвентаре"""
        inventory = self.game_logic.get_inventory()
        inventory_count = len(inventory)
        
        if inventory_count > 0:
            # Показываем количество шариков в инвентаре
            text = self.font.render(f"Инвентарь: {inventory_count} шариков", True, BLACK)
            self.screen.blit(text, (10, 10))
            
            # Показываем миниатюры шариков из инвентаря
            start_x = 10
            start_y = 40
            spacing = 35
            
            for i, ball in enumerate(inventory[:10]):  # Показываем максимум 10
                mini_x = start_x + i * spacing
                mini_y = start_y
                pygame.draw.circle(
                    self.screen,
                    ball.color,
                    (mini_x, mini_y),
                    12
                )
                pygame.draw.circle(
                    self.screen,
                    BLACK,
                    (mini_x, mini_y),
                    12,
                    1
                )
            
            if inventory_count > 10:
                text = self.small_font.render(f"+{inventory_count - 10}", True, BLACK)
                self.screen.blit(text, (start_x + 10 * spacing, start_y - 6))
    
    def _draw_suction_indicator(self, mouse_x, mouse_y):
        """Отрисовывает индикатор зоны всасывания вокруг мыши"""
        if self.mouse_pressed and self.mouse_button == 1:  # Левая кнопка мыши
            # Рисуем полупрозрачный круг зоны всасывания
            suction_surface = pygame.Surface(
                (self.game_logic.suction_radius * 2, self.game_logic.suction_radius * 2),
                pygame.SRCALPHA
            )
            pygame.draw.circle(
                suction_surface,
                (100, 150, 255, 100),  # Полупрозрачный синий
                (self.game_logic.suction_radius, self.game_logic.suction_radius),
                self.game_logic.suction_radius,
                2
            )
            self.screen.blit(
                suction_surface,
                (mouse_x - self.game_logic.suction_radius, mouse_y - self.game_logic.suction_radius)
            )
    
    def _draw_info(self):
        """Отрисовывает дополнительную информацию"""
        balls_count = len(self.game_logic.get_balls())
        text = self.small_font.render(f"Шариков на экране: {balls_count}", True, GRAY)
        self.screen.blit(text, (SCREEN_WIDTH - 200, 10))
        
        # Инструкции
        instructions = [
            "ЛКМ - всасывать шарики",
            "ПКМ - выпускать шарики",
        ]
        y_offset = SCREEN_HEIGHT - 50
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, GRAY)
            self.screen.blit(text, (10, y_offset + i * 20))
    
    def _handle_events(self):
        """Обрабатывает события"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEMOTION:
                # Обновляем позицию мыши в игровой логике
                mouse_x, mouse_y = event.pos
                self.game_logic.update_mouse_position(mouse_x, mouse_y)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pressed = True
                self.mouse_button = event.button
                
                if event.button == 1:  # Левая кнопка мыши - всасывание
                    self.game_logic.try_suck_ball()
                elif event.button == 3:  # Правая кнопка мыши - выпускание
                    self.game_logic.spit_ball()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_pressed = False
                self.mouse_button = None
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:  # R - перезапуск
                    self.game_logic.clear_all_balls()
                    self._create_starting_balls()
        
        return True
    
    def _update(self):
        """Обновляет состояние игры"""
        # Обновляем игровую логику
        self.game_logic.update()
        
        # Непрерывное всасывание при зажатой левой кнопке мыши
        if self.mouse_pressed and self.mouse_button == 1:
            self.game_logic.try_suck_ball()
    
    def _draw(self):
        """Отрисовывает всё на экране"""
        # Очищаем экран белым цветом
        self.screen.fill(WHITE)
        
        # Рисуем зону удаления
        self._draw_delete_zone()
        
        # Рисуем все шарики
        for ball in self.game_logic.get_balls():
            self._draw_ball(ball)
        
        # Рисуем индикатор зоны всасывания
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self._draw_suction_indicator(mouse_x, mouse_y)
        
        # Рисуем инвентарь
        self._draw_inventory()
        
        # Рисуем информацию
        self._draw_info()
        
        # Обновляем экран
        pygame.display.flip()
    
    def run(self):
        """Главный цикл игры"""
        running = True
        
        while running:
            # Обработка событий
            running = self._handle_events()
            
            # Обновление состояния
            self._update()
            
            # Отрисовка
            self._draw()
            
            # Ограничение FPS до 60
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
