import pygame
import random
import sys

# 初始化pygame
pygame.init()

# ---------- 游戏常量 ----------
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 700
PLAY_WIDTH = 300  # 游戏主区域宽度 (10个格子)
PLAY_HEIGHT = 600  # 游戏主区域高度 (20个格子)
BLOCK_SIZE = 30  # 每个方块大小

# 计算主区域在窗口中的偏移，使其居中
TOP_LEFT_X = (WINDOW_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = WINDOW_HEIGHT - PLAY_HEIGHT - 10

# ---------- 颜色定义 ----------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)

# ---------- 方块形状定义 ----------
# 每个形状由多个方块坐标组成，坐标系以形状的(0,0)为锚点
SHAPES = {
    'I': {'shape': [(0, 1), (1, 1), (2, 1), (3, 1)], 'color': CYAN},
    'O': {'shape': [(0, 0), (1, 0), (0, 1), (1, 1)], 'color': YELLOW},
    'T': {'shape': [(0, 0), (1, 0), (2, 0), (1, 1)], 'color': PURPLE},
    'S': {'shape': [(1, 0), (2, 0), (0, 1), (1, 1)], 'color': GREEN},
    'Z': {'shape': [(0, 0), (1, 0), (1, 1), (2, 1)], 'color': RED},
    'L': {'shape': [(0, 0), (0, 1), (0, 2), (1, 2)], 'color': ORANGE},
    'J': {'shape': [(1, 0), (1, 1), (1, 2), (0, 2)], 'color': BLUE},
}


def get_random_shape():
    """随机获取一个形状及其颜色"""
    name = random.choice(list(SHAPES.keys()))
    return name, SHAPES[name]['shape'], SHAPES[name]['color']


def rotate_shape(shape):
    """顺时针旋转形状矩阵"""
    # 找出形状的最小包围盒尺寸
    rows = max(y for x, y in shape) + 1
    cols = max(x for x, y in shape) + 1
    # 创建网格
    grid = [[False] * cols for _ in range(rows)]
    for x, y in shape:
        grid[y][x] = True
    # 顺时针旋转网格
    rotated_grid = list(zip(*grid[::-1]))
    # 转换回坐标列表
    new_shape = [(x, y) for y, row in enumerate(rotated_grid) for x, cell in enumerate(row) if cell]
    return new_shape


# ---------- 字体设置 ----------
def get_chinese_font(size, bold=False):
    """获取能显示中文的字体"""
    font_names = ["Microsoft YaHei", "SimHei", "SimSun", "FangSong", "KaiTi"]
    for name in font_names:
        try:
            font = pygame.font.SysFont(name, size, bold=bold)
            test_surface = font.render("测", True, WHITE)
            return font  # 成功创建则直接返回
        except:
            continue  # 失败则继续尝试下一个字体

    # 所有系统字体都失败，返回默认字体
    print("警告：未找到中文字体，将使用默认字体")
    return pygame.font.Font(None, size)


# ---------- 游戏类 ----------
class TetrisGame:
    def __init__(self):
        self.grid = [[BLACK for _ in range(10)] for _ in range(20)]  # 20行10列的游戏网格
        self.score = 0
        self.game_over = False
        self.current_piece = None  # 当前活动方块
        self.next_piece = None  # 下一个方块
        self.spawn_piece()

    def spawn_piece(self):
        """生成新的当前方块"""
        if self.next_piece is None:
            name, shape, color = get_random_shape()
            self.next_piece = {'name': name, 'shape': shape, 'color': color}

        # 当前方块变为下一个方块
        self.current_piece = {
            'name': self.next_piece['name'],
            'shape': self.next_piece['shape'].copy(),
            'color': self.next_piece['color'],
            'x': 3,  # 初始横向偏移
            'y': 0  # 初始纵向偏移
        }
        # 生成新的下一个方块
        name, shape, color = get_random_shape()
        self.next_piece = {'name': name, 'shape': shape, 'color': color}

        # 检查生成时是否立即碰撞（游戏结束）
        if self.check_collision(self.current_piece['shape'], self.current_piece['x'], self.current_piece['y']):
            self.game_over = True
            self.current_piece = None

    def check_collision(self, shape, offset_x, offset_y):
        """检查方块在给定偏移位置是否与网格边界或已有方块碰撞"""
        for x, y in shape:
            new_x = offset_x + x
            new_y = offset_y + y
            # 检查是否超出左右或下边界，或是否与已有方块重叠
            if new_x < 0 or new_x >= 10 or new_y >= 20 or new_y < 0:
                return True
            if new_y >= 0 and self.grid[new_y][new_x] != BLACK:
                return True
        return False

    def lock_piece(self):
        """将当前方块固定到网格上"""
        if self.current_piece is None:
            return
        for x, y in self.current_piece['shape']:
            grid_x = self.current_piece['x'] + x
            grid_y = self.current_piece['y'] + y
            if grid_y >= 0:
                self.grid[grid_y][grid_x] = self.current_piece['color']
        # 消除满行并更新分数
        self.clear_lines()
        # 生成下一个方块
        self.spawn_piece()

    def clear_lines(self):
        """消除所有满行并更新分数"""
        lines_cleared = 0
        y = 19  # 从最下面一行开始检查
        while y >= 0:
            if all(self.grid[y][x] != BLACK for x in range(10)):
                # 移除该行，并在顶部插入新空行
                del self.grid[y]
                self.grid.insert(0, [BLACK for _ in range(10)])
                lines_cleared += 1
                # 继续检查同一行（因为上面的行移下来了）
            else:
                y -= 1
        # 计分规则：消除行数的平方 * 10
        if lines_cleared > 0:
            self.score += (lines_cleared ** 2) * 10

    def move_down(self):
        """向下移动当前方块，如果无法移动则固定"""
        if self.current_piece is None or self.game_over:
            return
        if not self.check_collision(self.current_piece['shape'], self.current_piece['x'], self.current_piece['y'] + 1):
            self.current_piece['y'] += 1
        else:
            self.lock_piece()

    def move_side(self, dx):
        """左右移动当前方块"""
        if self.current_piece is None or self.game_over:
            return
        if not self.check_collision(self.current_piece['shape'], self.current_piece['x'] + dx, self.current_piece['y']):
            self.current_piece['x'] += dx

    def rotate_piece(self):
        """旋转当前方块"""
        if self.current_piece is None or self.game_over:
            return
        rotated_shape = rotate_shape(self.current_piece['shape'])
        if not self.check_collision(rotated_shape, self.current_piece['x'], self.current_piece['y']):
            self.current_piece['shape'] = rotated_shape

    def hard_drop(self):
        """硬降：直接落到底"""
        if self.current_piece is None or self.game_over:
            return
        while not self.check_collision(self.current_piece['shape'], self.current_piece['x'],
                                       self.current_piece['y'] + 1):
            self.current_piece['y'] += 1
        self.lock_piece()


# ---------- 绘制函数 ----------
def draw_grid(screen, game):
    """绘制游戏网格和方块"""
    # 绘制网格背景
    for y in range(20):
        for x in range(10):
            rect = pygame.Rect(
                TOP_LEFT_X + x * BLOCK_SIZE,
                TOP_LEFT_Y + y * BLOCK_SIZE,
                BLOCK_SIZE, BLOCK_SIZE
            )
            pygame.draw.rect(screen, game.grid[y][x], rect)
            # 绘制网格线 (浅灰色)
            pygame.draw.rect(screen, GRAY, rect, 1)

    # 绘制当前活动方块
    if game.current_piece and not game.game_over:
        for x, y in game.current_piece['shape']:
            rect = pygame.Rect(
                TOP_LEFT_X + (game.current_piece['x'] + x) * BLOCK_SIZE,
                TOP_LEFT_Y + (game.current_piece['y'] + y) * BLOCK_SIZE,
                BLOCK_SIZE, BLOCK_SIZE
            )
            pygame.draw.rect(screen, game.current_piece['color'], rect)
            pygame.draw.rect(screen, WHITE, rect, 1)


def draw_next_piece(screen, game):
    """绘制下一个方块预览"""
    font = get_chinese_font(24, bold=True)
    text = font.render("下一个:", True, WHITE)
    screen.blit(text, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y + 50))

    if game.next_piece:
        shape = game.next_piece['shape']
        color = game.next_piece['color']
        block_size = 25
        # 计算偏移让形状居中显示
        min_x = min(x for x, y in shape)
        max_x = max(x for x, y in shape)
        min_y = min(y for x, y in shape)
        max_y = max(y for x, y in shape)
        shape_width = (max_x - min_x + 1) * block_size
        shape_height = (max_y - min_y + 1) * block_size
        offset_x = TOP_LEFT_X + PLAY_WIDTH + 20 + (80 - shape_width) // 2 - min_x * block_size
        offset_y = TOP_LEFT_Y + 100 + (60 - shape_height) // 2 - min_y * block_size

        for x, y in shape:
            rect = pygame.Rect(
                offset_x + x * block_size,
                offset_y + y * block_size,
                block_size - 1, block_size - 1
            )
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)


def draw_score(screen, game):
    """绘制分数"""
    font = get_chinese_font(24, bold=True)
    text = font.render(f"得分: {game.score}", True, WHITE)
    screen.blit(text, (TOP_LEFT_X + PLAY_WIDTH + 20, TOP_LEFT_Y + 200))


def draw_game_over(screen, game):
    """绘制游戏结束画面"""
    if game.game_over:
        # 绘制半透明遮罩
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        font_title = get_chinese_font(48, bold=True)
        font_msg = get_chinese_font(28)

        text1 = font_title.render("游戏结束", True, WHITE)
        text2 = font_msg.render(f"最终得分: {game.score}", True, WHITE)
        text3 = font_msg.render("按 R 重新开始", True, WHITE)

        screen.blit(text1, (WINDOW_WIDTH // 2 - text1.get_width() // 2, WINDOW_HEIGHT // 2 - 80))
        screen.blit(text2, (WINDOW_WIDTH // 2 - text2.get_width() // 2, WINDOW_HEIGHT // 2 - 20))
        screen.blit(text3, (WINDOW_WIDTH // 2 - text3.get_width() // 2, WINDOW_HEIGHT // 2 + 40))
        pygame.display.flip()


# ---------- 主函数 ----------
def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("俄罗斯方块 - Tutor项目")
    clock = pygame.time.Clock()
    game = TetrisGame()

    # 计时器控制下落速度 (毫秒)
    fall_time = 0
    fall_speed = 500  # 初始500ms下落一格

    running = True
    while running:
        screen.fill(BLACK)

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game.game_over:
                    if event.key == pygame.K_r:
                        # 重新开始游戏
                        game = TetrisGame()
                        fall_time = 0
                    continue  # 游戏结束时不处理其他按键

                if event.key == pygame.K_LEFT:
                    game.move_side(-1)
                elif event.key == pygame.K_RIGHT:
                    game.move_side(1)
                elif event.key == pygame.K_DOWN:
                    game.move_down()
                elif event.key == pygame.K_UP:
                    game.rotate_piece()
                elif event.key == pygame.K_SPACE:
                    game.hard_drop()

        # 更新游戏状态 (非游戏结束)
        if not game.game_over:
            # 计时下落
            fall_time += clock.get_rawtime()
            if fall_time >= fall_speed:
                game.move_down()
                fall_time = 0

        # 绘制所有内容
        draw_grid(screen, game)
        draw_next_piece(screen, game)
        draw_score(screen, game)

        # 绘制游戏结束
        if game.game_over:
            draw_game_over(screen, game)

        pygame.display.update()
        clock.tick(60)  # 60 FPS


if __name__ == "__main__":
    main()