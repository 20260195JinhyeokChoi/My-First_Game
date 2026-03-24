import pygame
import sys
import math
from Sprites import load_sprite

# 파이게임 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spinning Sword OBB Visualization")

# 색상 정의
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
DEEP_YELLOW = (255, 160, 0)
BG_YELLOW = (255, 255, 180)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)

# 1. 플레이어(칼) 설정
move_rect_w, move_rect_h = 70, 70 
move_x = (WIDTH // 4) - (move_rect_w // 2)
move_y = (HEIGHT // 2) - (move_rect_h // 2)
move_speed = 5

# 칼 이미지 로드 및 초기 각도/회전 속도 설정
sword_img = load_sprite("sword", (move_rect_w, move_rect_h))
sword_angle = 0
rotation_speed = 3  # [수정됨] 매 프레임 돌아갈 일정한 회전 속도

# 2. 고정된 사각형
fixed_rect_w, fixed_rect_h = 100, 100
fixed_x = (WIDTH // 2) - (fixed_rect_w // 2)
fixed_y = (HEIGHT // 2) - (fixed_rect_h // 2)

clock = pygame.time.Clock()

running = True
while running:
    # 1. [수정됨] 일정한 속도로 각도 무한 증가 (마우스 추적 삭제)
    sword_angle = (sword_angle + rotation_speed) % 360
    rad_angle = math.radians(sword_angle)
    
    # 칼 중심점 계산
    center_move = (move_x + move_rect_w / 2, move_y + move_rect_h / 2)

    # 2. 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 3. 키 입력 처리 (이동)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  move_x -= move_speed
    if keys[pygame.K_RIGHT]: move_x += move_speed
    if keys[pygame.K_UP]:    move_y -= move_speed
    if keys[pygame.K_DOWN]:  move_y += move_speed

    # 4. 충돌 감지 로직
    center_fixed = (fixed_x + fixed_rect_w / 2, fixed_y + fixed_rect_h / 2)
    
    # A) AABB 충돌
    collision_aabb = (
        move_x < fixed_x + fixed_rect_w and
        move_x + move_rect_w > fixed_x and
        move_y < fixed_y + fixed_rect_h and
        move_y + move_rect_h > fixed_y
    )

    # B) 원형 충돌
    radius_move = move_rect_w / 2
    radius_fixed = fixed_rect_w / 2
    dist = math.sqrt((center_move[0] - center_fixed[0])**2 + (center_move[1] - center_fixed[1])**2)
    collision_circle = dist < (radius_move + radius_fixed)

    # 5. 화면 그리기
    current_bg = BG_YELLOW if collision_circle else WHITE
    screen.fill(current_bg)

    # 고정 오브젝트 (회색 사각형)
    pygame.draw.rect(screen, GRAY, (fixed_x, fixed_y, fixed_rect_w, fixed_rect_h))

    # 칼 이미지 회전 및 출력
    rotated_sword = pygame.transform.rotate(sword_img, sword_angle)
    rotated_rect = rotated_sword.get_rect(center=center_move)
    screen.blit(rotated_sword, rotated_rect.topleft)

    # AABB 및 원형 가이드라인 (테두리)
    aabb_color = DEEP_YELLOW if collision_aabb else RED
    pygame.draw.rect(screen, aabb_color, (move_x, move_y, move_rect_w, move_rect_h), 2)
    pygame.draw.rect(screen, aabb_color, (fixed_x, fixed_y, fixed_rect_w, fixed_rect_h), 2)
    pygame.draw.circle(screen, GREEN, (int(center_move[0]), int(center_move[1])), int(radius_move), 1)
    pygame.draw.circle(screen, GREEN, (int(center_fixed[0]), int(center_fixed[1])), int(radius_fixed), 1)

    # 6. OBB 꼭짓점 계산 및 그리기
    cx, cy = center_move
    rw, rh = move_rect_w / 2, move_rect_h / 2
    
    points = []
    # 회전 공식 적용 (-rad_angle 유지하여 이미지 회전과 동기화)
    for lx, ly in [(-rw, -rh), (rw, -rh), (rw, rh), (-rw, rh)]:
        rx = lx * math.cos(-rad_angle) - ly * math.sin(-rad_angle)
        ry = lx * math.sin(-rad_angle) + ly * math.cos(-rad_angle)
        points.append((cx + rx, cy + ry))
    
    # 파란색 테두리로 다각형 그리기
    pygame.draw.polygon(screen, BLUE, points, 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()