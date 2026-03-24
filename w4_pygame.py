import pygame
import sys
import math

# 파이게임 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AABB & Bounding Circle Visualization")

# 색상 정의
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
DEEP_YELLOW = (255, 160, 0)  # 기존보다 진한 황금색 (테두리용)
BG_YELLOW = (255, 255, 180)   # 연한 노란색 (배경용)
GREEN = (0, 200, 0)           # 원형 바운딩 박스 표시용

# 움직이는 사각형 설정
move_rect_w, move_rect_h = 50, 50
move_x = (WIDTH // 4) - (move_rect_w // 2)
move_y = (HEIGHT // 2) - (move_rect_h // 2)
move_speed = 5

# 고정된 사각형 설정
fixed_rect_w, fixed_rect_h = 100, 100
fixed_x = (WIDTH // 2) - (fixed_rect_w // 2)
fixed_y = (HEIGHT // 2) - (fixed_rect_h // 2)

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. 키 입력 처리
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  move_x -= move_speed
    if keys[pygame.K_RIGHT]: move_x += move_speed
    if keys[pygame.K_UP]:    move_y -= move_speed
    if keys[pygame.K_DOWN]:  move_y += move_speed

    # 2. 충돌 감지 로직
    # A) AABB (사각형) 충돌
    collision_aabb = (
        move_x < fixed_x + fixed_rect_w and
        move_x + move_rect_w > fixed_x and
        move_y < fixed_y + fixed_rect_h and
        move_y + move_rect_h > fixed_y
    )

    # B) 원형 바운딩 박스 충돌
    # 각 사각형의 중심점 계산
    center_move = (move_x + move_rect_w / 2, move_y + move_rect_h / 2)
    center_fixed = (fixed_x + fixed_rect_w / 2, fixed_y + fixed_rect_h / 2)
    
    # 반지름 계산 (지름이 너비와 같으므로 R = W / 2)
    radius_move = move_rect_w / 2
    radius_fixed = fixed_rect_w / 2
    
    # 두 중심 사이의 거리 계산 (피타고라스 정리)
    dist = math.sqrt((center_move[0] - center_fixed[0])**2 + (center_move[1] - center_fixed[1])**2)
    
    # 거리 < 반지름의 합 이면 충돌
    collision_circle = dist < (radius_move + radius_fixed)

    # 3. 화면 그리기
    # 원형 충돌 시 배경색 변경
    current_bg = BG_YELLOW if collision_circle else WHITE
    screen.fill(current_bg)

    # 오브젝트(사각형) 그리기
    pygame.draw.rect(screen, GRAY, (move_x, move_y, move_rect_w, move_rect_h))
    pygame.draw.rect(screen, GRAY, (fixed_x, fixed_y, fixed_rect_w, fixed_rect_h))

    # AABB 표시 (충돌 시 진한 노란색)
    aabb_color = DEEP_YELLOW if collision_aabb else RED
    pygame.draw.rect(screen, aabb_color, (move_x, move_y, move_rect_w, move_rect_h), 2)
    pygame.draw.rect(screen, aabb_color, (fixed_x, fixed_y, fixed_rect_w, fixed_rect_h), 2)

    # [새 기능] 원형 바운딩 박스 표시 (초록색 테두리)
    pygame.draw.circle(screen, GREEN, (int(center_move[0]), int(center_move[1])), int(radius_move), 1)
    pygame.draw.circle(screen, GREEN, (int(center_fixed[0]), int(center_fixed[1])), int(radius_fixed), 1)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()