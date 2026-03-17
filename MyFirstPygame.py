import pygame
import sys
import random
import math

pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survival: Small and Fast")

# 색상 정의
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# 잔상 효과를 위한 투명 표면
bullet_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# 폰트 설정
font_main = pygame.font.SysFont(None, 80)
font_sub = pygame.font.SysFont(None, 40)
font_ui = pygame.font.SysFont(None, 25)

# 게임 상태 변수
game_over = False

def reset_game():
    global ball_x, ball_y, ball_radius, speed, particles, bullets, game_over, start_time
    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2
    ball_radius = 25
    speed = 5
    particles = []
    bullets = []
    game_over = False
    start_time = pygame.time.get_ticks()

reset_game()

class Bullet:
    def __init__(self, target_x, target_y, is_item=False):
        spawn_points = [(0, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH, HEIGHT)]
        self.x, self.y = random.choice(spawn_points)
        angle = math.atan2(target_y - self.y, target_x - self.x)
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
        bullet_speed = random.uniform(3, 7) + min(elapsed_time * 0.1, 5)
        self.vx = math.cos(angle) * bullet_speed
        self.vy = math.sin(angle) * bullet_speed
        self.size = 5
        self.is_item = is_item
        self.color = GREEN if is_item else RED
        self.afterimage_positions = [] 

    def update(self):
        self.afterimage_positions.insert(0, (self.x, self.y))
        self.afterimage_positions = self.afterimage_positions[:8] 
        self.x += self.vx
        self.y += self.vy

    def draw(self, surf):
        for i, pos in enumerate(self.afterimage_positions):
            alpha = max(0, 180 - i * 20)
            surf_color = (self.color[0], self.color[1], self.color[2], alpha)
            pygame.draw.circle(surf, surf_color, (int(pos[0]), int(pos[1])), self.size)
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.size)

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 10)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(40, 100)
        self.size = random.randint(5, 12)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1
        if self.size > 0.5: self.size -= 0.1

    def draw(self, surf):
        if self.life > 0:
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), int(self.size))

clock = pygame.time.Clock()
running = True

while running:
    # 1. 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_over:
                mouse_pos = event.pos
                if WIDTH//2 - 100 < mouse_pos[0] < WIDTH//2 + 100 and \
                   HEIGHT//2 + 50 < mouse_pos[1] < HEIGHT//2 + 110:
                    reset_game()
            else:
                dist = math.sqrt((event.pos[0] - ball_x)**2 + (event.pos[1] - ball_y)**2)
                if dist <= ball_radius:
                    for _ in range(30):
                        particles.append(Particle(event.pos[0], event.pos[1], BLUE))

    # 2. 로직 처리
    if not game_over:
        # [수정 포인트] 크기에 비례한 속도 조절
        # 기본 속도 5에, 줄어든 크기만큼 속도를 가산합니다.
        # 공이 작아질수록 기동성이 올라가지만 제어가 힘들어집니다.
        speed = 5 + (25 - ball_radius) * 0.2

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]): ball_x -= speed
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]): ball_x += speed
        if (keys[pygame.K_w] or keys[pygame.K_UP]): ball_y -= speed
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]): ball_y += speed

        elapsed_seconds = (pygame.time.get_ticks() - start_time) / 1000
        spawn_probability = 0.03 + min(elapsed_seconds * 0.001, 0.1) + (25 - ball_radius) * 0.002

        if random.random() < spawn_probability:
            bullets.append(Bullet(ball_x, ball_y, random.random() < 0.1))

        for b in bullets[:]:
            b.update()
            dist = math.sqrt((b.x - ball_x)**2 + (b.y - ball_y)**2)
            if dist < ball_radius + b.size:
                if b.is_item:
                    ball_radius += 3
                    for _ in range(20): particles.append(Particle(b.x, b.y, GREEN))
                else:
                    ball_radius -= 3
                    for _ in range(10): particles.append(Particle(b.x, b.y, BLUE)) 
                bullets.remove(b)
            elif b.x < -100 or b.x > WIDTH + 100 or b.y < -100 or b.y > HEIGHT + 100:
                bullets.remove(b)

        if ball_radius <= 5:
            game_over = True
            for _ in range(100): particles.append(Particle(ball_x, ball_y, BLUE))

        ball_radius = min(ball_radius, 50)
        ball_x = max(ball_radius, min(WIDTH - ball_radius, ball_x))
        ball_y = max(ball_radius, min(HEIGHT - ball_radius, ball_y))
    
    for p in particles: p.update()
    particles = [p for p in particles if p.life > 0]

    # 4. 화면 그리기
    screen.fill(WHITE)
    ui_text = font_ui.render(f"FPS: {int(clock.get_fps())} | Size: {int(ball_radius)} | Speed: {speed:.1f}", True, BLACK)
    screen.blit(ui_text, (10, 10))

    for p in particles: p.draw(screen)
    bullet_surface.fill((0, 0, 0, 0)) 
    if not game_over:
        for b in bullets: b.draw(bullet_surface)
        screen.blit(bullet_surface, (0, 0))
        pygame.draw.circle(screen, BLUE, (int(ball_x), int(ball_y)), int(ball_radius))
    else:
        msg = font_main.render("GAME OVER", True, RED)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 100))
        final_time_msg = font_sub.render(f"Survival Time: {int(elapsed_seconds)}s", True, BLACK)
        screen.blit(final_time_msg, (WIDTH//2 - final_time_msg.get_width()//2, HEIGHT//2))
        btn_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 60)
        pygame.draw.rect(screen, GRAY, btn_rect)
        pygame.draw.rect(screen, BLACK, btn_rect, 2)
        btn_msg = font_sub.render("RESTART", True, BLACK)
        screen.blit(btn_msg, (WIDTH//2 - btn_msg.get_width()//2, HEIGHT//2 + 95))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()