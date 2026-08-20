import pygame
import random
import sys
import os  # 新增：用于检查字体文件是否存在

# 初始化pygame
pygame.init()

# 游戏常量设置
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
GRID_SIZE = 20  # 每个格子的大小
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# 颜色定义 (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 150, 0)

# 方向常量
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


# ---------- 新增：字体设置函数 ----------
def get_chinese_font(size, bold=False):
    """
    获取一个能显示中文的字体
    优先使用系统自带的微软雅黑或宋体，如果找不到则使用pygame默认字体（可能不支持中文）
    """
    # 尝试常见的中文字体名称（按优先级排序）
    font_names = [
        "Microsoft YaHei",  # 微软雅黑（Win10/11 常见）
        "SimHei",  # 黑体
        "SimSun",  # 宋体
        "FangSong",  # 仿宋
        "KaiTi",  # 楷体
        "STHeiti",  # 华文黑体
        "STKaiti",  # 华文楷体
    ]

    for name in font_names:
        try:
            # 尝试用系统字体名创建字体
            font = pygame.font.SysFont(name, size, bold=bold)
            # 简单测试：渲染一个中文字符，如果不报错说明可用
            test_surface = font.render("测", True, WHITE)
            return font
        except:
            continue

    # 如果所有系统字体都失败，尝试加载一个项目目录下的字体文件（备用方案）
    # 你可以把下载的 .ttf 字体文件放在项目根目录，并取消下面几行的注释
    # local_font_path = os.path.join(os.path.dirname(__file__), "你的中文字体文件.ttf")
    # if os.path.exists(local_font_path):
    #     try:
    #         font = pygame.font.Font(local_font_path, size)
    #         return font
    #     except:
    #         pass

    # 最终保底：返回pygame默认字体（可能无法显示中文）
    print("警告：未找到中文字体，将使用默认字体，中文可能显示为方块。")
    return pygame.font.Font(None, size)


# ---------- 类定义 ----------
class Snake:
    """蛇类，管理蛇的状态和行为"""

    def __init__(self):
        # 初始蛇身：由头部和两节身体组成，位于屏幕中央附近
        head_x = GRID_WIDTH // 2
        head_y = GRID_HEIGHT // 2
        self.body = [
            [head_x, head_y],
            [head_x - 1, head_y],
            [head_x - 2, head_y]
        ]
        self.direction = RIGHT
        self.grow_flag = False

    def move(self):
        """移动蛇身"""
        head = self.body[0].copy()
        # 计算新头部位置
        new_head = [
            head[0] + self.direction[0],
            head[1] + self.direction[1]
        ]
        # 插入新头部
        self.body.insert(0, new_head)
        # 如果不需要成长，移除尾部
        if not self.grow_flag:
            self.body.pop()
        else:
            self.grow_flag = False

    def change_direction(self, new_dir):
        """改变方向，防止蛇直接掉头"""
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.direction = new_dir

    def grow(self):
        """标记蛇需要成长（吃到食物时调用）"""
        self.grow_flag = True

    def check_collision(self):
        """检查是否撞墙或撞自身"""
        head = self.body[0]
        # 检查撞墙
        if (head[0] < 0 or head[0] >= GRID_WIDTH or
                head[1] < 0 or head[1] >= GRID_HEIGHT):
            return True
        # 检查撞自身（头部是否与身体其他部分重叠）
        for segment in self.body[1:]:
            if head == segment:
                return True
        return False

    def get_head(self):
        return self.body[0]


class Food:
    """食物类，管理食物的位置"""

    def __init__(self, snake_body):
        self.position = self.generate_random_pos(snake_body)

    def generate_random_pos(self, snake_body):
        """在空白位置生成食物"""
        while True:
            pos = [
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            ]
            if pos not in snake_body:
                return pos

    def respawn(self, snake_body):
        """重新生成食物"""
        self.position = self.generate_random_pos(snake_body)


# ---------- 绘图函数 ----------
def draw_grid(surface):
    """绘制网格线（可选，辅助视觉）"""
    for x in range(0, WINDOW_WIDTH, GRID_SIZE):
        pygame.draw.line(surface, (40, 40, 40), (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, (40, 40, 40), (0, y), (WINDOW_WIDTH, y))


def draw_snake(surface, snake):
    """绘制蛇"""
    for i, segment in enumerate(snake.body):
        rect = pygame.Rect(
            segment[0] * GRID_SIZE,
            segment[1] * GRID_SIZE,
            GRID_SIZE - 1,  # 留出间隙，更清晰
            GRID_SIZE - 1
        )
        # 蛇头用亮绿色，身体用深绿色
        color = GREEN if i == 0 else DARK_GREEN
        pygame.draw.rect(surface, color, rect)


def draw_food(surface, food):
    """绘制食物"""
    rect = pygame.Rect(
        food.position[0] * GRID_SIZE,
        food.position[1] * GRID_SIZE,
        GRID_SIZE - 1,
        GRID_SIZE - 1
    )
    pygame.draw.rect(surface, RED, rect)


# ---------- 修改：显示游戏结束信息，使用中文字体 ----------
def show_game_over(screen, score):
    """显示游戏结束信息（中文）"""
    # 获取能显示中文的字体（标题大号，加粗）
    title_font = get_chinese_font(48, bold=True)
    msg_font = get_chinese_font(32)

    text1 = title_font.render("游戏结束!", True, WHITE)
    text2 = msg_font.render(f"得分: {score}", True, WHITE)
    text3 = msg_font.render("按 Q 退出 / 按 R 重新开始", True, WHITE)

    # 居中绘制
    screen.blit(text1, (WINDOW_WIDTH // 2 - text1.get_width() // 2, WINDOW_HEIGHT // 2 - 80))
    screen.blit(text2, (WINDOW_WIDTH // 2 - text2.get_width() // 2, WINDOW_HEIGHT // 2 - 20))
    screen.blit(text3, (WINDOW_WIDTH // 2 - text3.get_width() // 2, WINDOW_HEIGHT // 2 + 40))
    pygame.display.flip()


# ---------- 主函数 ----------
def main():
    """主游戏循环"""
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("贪吃蛇游戏 - Tutor项目")
    clock = pygame.time.Clock()

    # 游戏状态
    score = 0
    snake = Snake()
    food = Food(snake.body)
    game_over = False

    # 主循环
    running = True
    while running:
        # --- 事件处理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        # 重新开始
                        snake = Snake()
                        food = Food(snake.body)
                        score = 0
                        game_over = False
                    elif event.key == pygame.K_q:
                        running = False
                        pygame.quit()
                        sys.exit()
                else:
                    # 游戏进行中的按键控制
                    if event.key == pygame.K_UP:
                        snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction(RIGHT)

        if not game_over:
            # --- 游戏逻辑更新 ---
            snake.move()

            # 检查是否吃到食物
            if snake.get_head() == food.position:
                snake.grow()
                score += 1
                food.respawn(snake.body)

            # 检查碰撞
            if snake.check_collision():
                game_over = True

            # --- 绘制画面 ---
            screen.fill(BLACK)
            # draw_grid(screen)  # 如需网格线，取消注释
            draw_snake(screen, snake)
            draw_food(screen, food)

            # ---------- 修改：显示得分，使用中文字体 ----------
            score_font = get_chinese_font(30, bold=True)
            score_text = score_font.render(f"得分: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))

        else:
            # --- 游戏结束画面 ---
            show_game_over(screen, score)

        pygame.display.update()
        clock.tick(10)  # 控制游戏速度（10帧/秒）


if __name__ == "__main__":
    main()