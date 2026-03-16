import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chaos Relic: System Overload")

clock = pygame.time.Clock()
particles = []

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        # 속도 대폭 상향: 사방으로 튀어나가게 설정
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(4, 15) # 훨씬 빠름

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        # 수명과 크기를 더 극단적으로 설정
        self.life = random.randint(20, 100)
        self.size = random.randint(1, 10)

        # 색상: 가끔 '네온 핑크'나 '번개색'이 섞이도록 도박수 추가
        if random.random() > 0.9:
            self.color = (255, 255, 255) # 하얀 섬광
        else:
            self.color = (
                random.randint(100, 255),
                random.randint(50, 255),
                random.randint(0, 100)
            )

    def update(self):
        # 공기 저항 및 지그재그 움직임 추가
        self.vx *= 0.98
        self.vx += random.uniform(-0.5, 0.5) 
        self.x += self.vx
        self.y += self.vy

        self.vy += 0.2 # 중력 강화
        self.life -= 1

    def draw(self, surf, offset_x=0, offset_y=0):
        if self.life > 0:
            # 화면 흔들림 오프셋 적용
            pos = (int(self.x + offset_x), int(self.y + offset_y))
            # 원과 사각형을 섞어서 출력 (더 정신없음)
            if self.size > 5:
                pygame.draw.circle(surf, self.color, pos, self.size)
            else:
                pygame.draw.rect(surf, self.color, (*pos, self.size * 2, self.size * 2))

def draw_background(surface, t):
    # 배경색이 시간에 따라 미세하게 번쩍임
    bg_tint = int(30 + 20 * math.sin(t * 10))
    surface.fill((10, bg_tint // 2, bg_tint))
    
    # 격자무늬 노이즈 추가
    for _ in range(5):
        y = random.randint(0, HEIGHT)
        pygame.draw.line(surface, (50, 50, 80), (0, y), (WIDTH, y), 1)

running = True
time = 0
shake_amount = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse = pygame.mouse.get_pos()
    buttons = pygame.mouse.get_pressed()

    # 화면 흔들림 계산
    if shake_amount > 0:
        shake_x = random.uniform(-shake_amount, shake_amount)
        shake_y = random.uniform(-shake_amount, shake_amount)
        shake_amount *= 0.9 # 서서히 줄어듦
    else:
        shake_x, shake_y = 0, 0

    # 마우스 클릭 시 폭발적 생성 및 화면 흔들림 유발
    if buttons[0]: # 좌클릭: 집중 포화
        shake_amount = 5
        for _ in range(20):
            particles.append(Particle(mouse[0], mouse[1]))
    
    if buttons[2]: # 우클릭: 화면 전체 붕괴
        shake_amount = 15
        for _ in range(50):
            particles.append(Particle(random.randint(0, WIDTH), random.randint(0, HEIGHT)))

    time += 0.1
    draw_background(screen, time)

    for p in particles:
        p.update()
        p.draw(screen, shake_x, shake_y)

    particles = [p for p in particles if p.life > 0]

    pygame.display.flip()
    clock.tick(60)

pygame.quit()