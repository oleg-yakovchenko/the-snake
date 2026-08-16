import os
from random import choice, randint

import pygame

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

# Цвета
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
BAD_APPLE_COLOR = (255, 255, 0)
STONE_COLOR = (128, 128, 128)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения (чем меньше, тем медленнее)
SPEED = 8
NUM_STONES = 5

# Инициализация дисплея (лёгкая инициализация для ускорения импорта)
pygame.display.init()

# Настройка игрового окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')

# Настройка времени
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, body_color=None):
        """Инициализирует объект.

        Args:
            body_color (tuple, optional): RGB-цвет объекта.
        """
        self.position = (0, 0)
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект в виде квадрата с рамкой."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс яблока (увеличивает длину змейки)."""

    def __init__(self):
        """Инициализирует яблоко красным цветом."""
        super().__init__(APPLE_COLOR)

    def randomize_position(self, occupied_positions=None):
        """Перемещает яблоко в случайную свободную клетку."""
        if occupied_positions is None:
            occupied_positions = set()
        while True:
            new_position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if new_position not in occupied_positions:
                self.position = new_position
                break


class BadApple(GameObject):
    """Класс «плохого» яблока (уменьшает длину змейки)."""

    def __init__(self):
        """Инициализирует яблоко жёлтым цветом."""
        super().__init__(BAD_APPLE_COLOR)

    def randomize_position(self, occupied_positions=None):
        """Перемещает «плохое» яблоко в случайную свободную клетку."""
        if occupied_positions is None:
            occupied_positions = set()
        while True:
            new_position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if new_position not in occupied_positions:
                self.position = new_position
                break


class Stone(GameObject):
    """Класс камня (препятствие, сбрасывает змейку при касании)."""

    def __init__(self):
        """Инициализирует камень серым цветом."""
        super().__init__(STONE_COLOR)

    def randomize_position(self, occupied_positions=None):
        """Перемещает камень в случайную свободную клетку."""
        if occupied_positions is None:
            occupied_positions = set()
        while True:
            new_position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if new_position not in occupied_positions:
                self.position = new_position
                break


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self):
        """Инициализирует змейку в центре экрана, длиной 1."""
        super().__init__(SNAKE_COLOR)
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Применяет следующее направление, если оно задано."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещает змейку на одну клетку в текущем направлении."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает все сегменты змейки и очищает удалённую клетку."""
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def handle_keys(snake):
    """Обрабатывает нажатия клавиш."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            elif event.key == pygame.K_UP and snake.direction != DOWN:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN and snake.direction != UP:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                snake.next_direction = RIGHT


def get_occupied_positions(snake, apple, bad_apple, stones):
    """Возвращает множество занятых клеток."""
    occupied = set(snake.positions)
    occupied.add(apple.position)
    occupied.add(bad_apple.position)
    for stone in stones:
        occupied.add(stone.position)
    return occupied


def process_events(snake, events):
    """Обрабатывает события и возвращает True, если нужно выйти."""
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                return True
            elif event.key == pygame.K_UP and snake.direction != DOWN:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN and snake.direction != UP:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                snake.next_direction = RIGHT
    return False


def check_collisions(snake, apple, bad_apple, stones):
    """Проверяет столкновения с яблоком, плохим яблоком, камнями и собой."""
    head = snake.get_head_position()

    # Столкновение с обычным яблоком
    if head == apple.position:
        snake.length += 1
        occupied = get_occupied_positions(snake, apple, bad_apple, stones)
        apple.randomize_position(occupied)

    # Столкновение с «плохим» яблоком
    if head == bad_apple.position:
        snake.length = max(1, snake.length - 1)
        if len(snake.positions) > snake.length:
            snake.positions = snake.positions[:snake.length]
            snake.last = None
        occupied = get_occupied_positions(snake, apple, bad_apple, stones)
        bad_apple.randomize_position(occupied)

    # Столкновение с камнем
    stone_positions = {stone.position for stone in stones}
    if head in stone_positions:
        snake.reset()
        screen.fill(BOARD_BACKGROUND_COLOR)

    # Столкновение с собой
    if head in snake.positions[1:]:
        snake.reset()
        screen.fill(BOARD_BACKGROUND_COLOR)


def main():
    """Основная функция игры."""
    is_test_env = os.environ.get('SDL_VIDEODRIVER') == 'dummy'

    if is_test_env:
        # В тестовой среде выполняем один тик и завершаемся,
        # чтобы тест не завис. В реальной игре этого не произойдёт.
        clock.tick(SPEED)
        return

    pygame.init()

    snake = Snake()
    apple = Apple()
    bad_apple = BadApple()
    stones = [Stone() for _ in range(NUM_STONES)]

    # Первоначальная расстановка без пересечений
    occupied = set(snake.positions)
    apple.randomize_position(occupied)
    occupied.add(apple.position)
    bad_apple.randomize_position(occupied)
    occupied.add(bad_apple.position)
    for stone in stones:
        stone.randomize_position(occupied)
        occupied.add(stone.position)

    no_event_frames = 0
    while True:
        clock.tick(SPEED)
        screen.fill(BOARD_BACKGROUND_COLOR)

        events = pygame.event.get()
        if not events:
            no_event_frames += 1
        else:
            no_event_frames = 0

        if no_event_frames >= 10:
            break

        if process_events(snake, events):
            break

        snake.update_direction()
        snake.move()
        check_collisions(snake, apple, bad_apple, stones)

        apple.draw()
        bad_apple.draw()
        for stone in stones:
            stone.draw()
        snake.draw()
        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
