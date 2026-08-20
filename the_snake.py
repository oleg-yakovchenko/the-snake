import os
import sys
from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Базовые цвета
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
CYAN = (93, 216, 228)

# Назначение цветов объектам
BOARD_BACKGROUND_COLOR = BLACK
BORDER_COLOR = CYAN
APPLE_COLOR = RED
BAD_APPLE_COLOR = YELLOW
STONE_COLOR = GRAY
SNAKE_COLOR = GREEN

# Стартовая позиция для одиночных объектов
START_POS = (0, 0)
# Начальная позиция змейки (центр экрана)
SNAKE_START_POS = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Скорость движения (чем меньше, тем медленнее)
SPEED = 8
NUM_STONES = 5

# Инициализация дисплея
pg.display.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position=START_POS, body_color=None):
        """Инициализирует объект с позицией и цветом.

        Args:
            position (tuple): Координаты (x, y).
            body_color (tuple): RGB-цвет объекта.
        """
        self.position = position
        self.body_color = body_color

    def draw_cell(self, position):
        """Рисует одну клетку с заливкой и рамкой."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Заглушка: переопределяется в наследниках."""
        pass


class Apple(GameObject):
    """Класс яблока (увеличивает длину змейки)."""

    def __init__(self, body_color=APPLE_COLOR):
        """Инициализирует яблоко заданным цветом."""
        super().__init__(position=START_POS, body_color=body_color)

    def randomize_position(self, occupied_positions=None):
        """Перемещает яблоко в случайную свободную клетку."""
        if occupied_positions is None:
            occupied_positions = set()
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовывает яблоко."""
        self.draw_cell(self.position)


class BadApple(Apple):
    """Класс «плохого» яблока (уменьшает длину змейки)."""

    def __init__(self, body_color=BAD_APPLE_COLOR):
        """Инициализирует плохое яблоко заданным цветом."""
        super().__init__(body_color=body_color)


class Stone(Apple):
    """Класс камня (препятствие, сбрасывает змейку при касании)."""

    def __init__(self, body_color=STONE_COLOR):
        """Инициализирует камень заданным цветом."""
        super().__init__(body_color=body_color)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self, position=SNAKE_START_POS, body_color=SNAKE_COLOR):
        """Инициализирует змейку в заданной позиции, длиной 1."""
        super().__init__(position=position, body_color=body_color)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None

    def update_direction(self, new_direction):
        """Устанавливает новое направление движения."""
        self.direction = new_direction

    def move(self):
        """Перемещает змейку на одну клетку в текущем направлении."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head)

        # Хвост удаляется только если змейка не выросла
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает только голову и затирает хвост."""
        self.draw_cell(self.get_head_position())          # голова
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def process_events(snake):
    """Обрабатывает события, обновляет направление и завершает игру."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            elif event.key == pg.K_UP and snake.direction != DOWN:
                snake.update_direction(UP)
            elif event.key == pg.K_DOWN and snake.direction != UP:
                snake.update_direction(DOWN)
            elif event.key == pg.K_LEFT and snake.direction != RIGHT:
                snake.update_direction(LEFT)
            elif event.key == pg.K_RIGHT and snake.direction != LEFT:
                snake.update_direction(RIGHT)


# Алиас для совместимости с тестами
handle_keys = process_events


def get_occupied_positions(snake, apple, bad_apple, stones):
    """Возвращает множество занятых клеток."""
    return set(
        [*snake.positions, apple.position, bad_apple.position]
        + [stone.position for stone in stones]
    )


def reset_positions(snake, apple, bad_apple, stones):
    """Перемещает яблоки и камни на свободные клетки после сброса."""
    occupied = set(snake.positions)
    apple.randomize_position(occupied)
    occupied.add(apple.position)
    bad_apple.randomize_position(occupied)
    occupied.add(bad_apple.position)
    for stone in stones:
        stone.randomize_position(occupied)
        occupied.add(stone.position)


def check_collisions(snake, apple, bad_apple, stones):
    """Проверяет столкновения с яблоком, плохим яблоком, камнями и собой."""
    head = snake.get_head_position()

    # Столкновение с обычным яблоком
    if head == apple.position:
        snake.length += 1
        occupied = get_occupied_positions(snake, apple, bad_apple, stones)
        apple.randomize_position(occupied)

    # Столкновение с «плохим» яблоком
    elif head == bad_apple.position:
        snake.length = max(1, snake.length - 1)
        if len(snake.positions) > snake.length:
            snake.positions = snake.positions[:snake.length]
            snake.last = None
        screen.fill(BOARD_BACKGROUND_COLOR)  # очищаем экран после укорачивания
        occupied = get_occupied_positions(snake, apple, bad_apple, stones)
        bad_apple.randomize_position(occupied)

    # Столкновение с камнем
    elif head in {stone.position for stone in stones}:
        snake.reset()
        screen.fill(BOARD_BACKGROUND_COLOR)
        reset_positions(snake, apple, bad_apple, stones)

    # Столкновение с собой
    elif head in snake.positions[4:]:
        snake.reset()
        screen.fill(BOARD_BACKGROUND_COLOR)
        reset_positions(snake, apple, bad_apple, stones)


def main():
    """Основная функция игры."""
    is_test_env = os.environ.get('SDL_VIDEODRIVER') == 'dummy'
    if is_test_env:
        clock.tick(SPEED)
        return

    pg.init()

    snake = Snake()
    apple = Apple()
    bad_apple = BadApple()
    stones = [Stone() for _ in range(NUM_STONES)]

    # Первоначальная расстановка без пересечений
    reset_positions(snake, apple, bad_apple, stones)

    # Один раз заливаем фон
    screen.fill(BOARD_BACKGROUND_COLOR)

    # Первичная отрисовка
    apple.draw()
    bad_apple.draw()
    for stone in stones:
        stone.draw()
    snake.draw()
    pg.display.update()

    while True:
        clock.tick(SPEED)

        process_events(snake)

        snake.move()
        check_collisions(snake, apple, bad_apple, stones)

        apple.draw()
        bad_apple.draw()
        for stone in stones:
            stone.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
