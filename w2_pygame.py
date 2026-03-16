import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ancient Relic Particle - Sandstorm Edition")

clock = pygame.time.Clock()
particles = []

class Particle:
    def __init__(self, x, y, is_gold=True):
        self.x = x
        self.y = y
        angle = random.uniform(math.pi, math.pi * 2) 
        speed = random.uniform(2, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(30, 60)
        self.size = random.randint(2, 6)

        if is_gold:
            self.color = (random.randint(200, 255), random.randint(160, 210), 30)
        else:
            self.color = (30, random.randint(150, 200), random.randint(180, 220))

    def update(self, wind_power):
        self.vx += wind_power 
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            rect = pygame.Rect(int(self.x), int(self.y), self.size, self.size)
            pygame.draw.rect(surf, self.color, rect)

    # ⚠️ 방금 빼먹었던 생존 확인 센서입니다!
    def alive(self):
        return self.life > 0
    
def draw_background(surface, t):
    # range(0, HEIGHT, 2)에서 '2'를 빼서 모든 라인을 다 그려야 잔상이 지워집니다.
    for y in range(HEIGHT): 
        c = int(20 + 15 * math.sin(y * 0.005 + t))
        pygame.draw.line(surface, (10, c, c+10), (0, y), (WIDTH, y))

running = True
time = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse = pygame.mouse.get_pos()
    buttons = pygame.mouse.get_pressed()

    # 사인 함수를 이용한 유동적인 바람의 세기 계산
    # $$F_{wind} = \sin(time \times 2) \times 0.1$$
    wind_power = math.sin(time) * 0.12

    # 좌클릭: 일반 생성 / 우클릭: 폭주 모드
    if buttons[0]:
        for _ in range(5):
            particles.append(Particle(mouse[0], mouse[1], True))
    if buttons[2]:
        for _ in range(15):
            particles.append(Particle(random.randint(0, WIDTH), HEIGHT, False))

    time += 0.05
    draw_background(screen, time)

    for p in particles:
        p.update(wind_power)
        p.draw(screen)

    particles = [p for p in particles if p.alive()]

    # 기획자라면 챙겨야 할 UI (현재 입자 개수 확인)
    # print(f"Active Particles: {len(particles)}") 

    pygame.display.flip()
    clock.tick(60)

pygame.quit()