import pygame
import sys
import math
from Sprites import load_sprite

# 파이게임 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Collision System Comparison")

# 폰트 설정
font = pygame.font.SysFont("arial", 24, bold=True)

# 색상 정의
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)        # AABB 용
GREEN = (0, 255, 0)      # OBB 용
BLUE = (0, 0, 255)       # Circle 용
BLACK = (0, 0, 0)

# 1. 플레이어(칼) 설정
move_rect_w, move_rect_h = 70, 70 
move_x, move_y = 200, 300
move_speed = 5
sword_img = load_sprite("sword", (move_rect_w, move_rect_h))
sword_angle = 0
rotation_speed = 3 

# 2. 고정된 사각형 (대상)
fixed_rect_w, fixed_rect_h = 100, 100
fixed_x, fixed_y = 400, 250

def get_obb_vertices(cx, cy, w, h, angle_rad):
    """중심점과 크기, 각도를 받아 OBB의 네 꼭짓점을 반환"""
    hw, hh = w / 2, h / 2
    points = []
    for lx, ly in [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]:
        # 이미지 회전 방향과 맞추기 위해 -angle_rad 사용
        rx = lx * math.cos(-angle_rad) - ly * math.sin(-angle_rad)
        ry = lx * math.sin(-angle_rad) + ly * math.cos(-angle_rad)
        points.append((cx + rx, cy + ry))
    return points

def check_obb_collision(poly1, poly2):
    """분리축 이론(SAT)을 이용한 두 다각형 간의 충돌 검사"""
    for poly in [poly1, poly2]:
        for i in range(len(poly)):
            # 변의 법선 벡터(분리축) 구하기
            p1, p2 = poly[i], poly[(i + 1) % len(poly)]
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            axis = (-edge[1], edge[0])
            
            # 축 정규화
            mag = math.sqrt(axis[0]**2 + axis[1]**2)
            axis = (axis[0]/mag, axis[1]/mag)
            
            # 투영
            def project(p, a):
                dots = [pt[0]*a[0] + pt[1]*a[1] for pt in p]
                return min(dots), max(dots)
            
            min1, max1 = project(poly1, axis)
            min2, max2 = project(poly2, axis)
            
            if max1 < min2 or max2 < min1:
                return False # 틈새 발견 (충돌 안 함)
    return True # 모든 축에서 겹침 (충돌 함)

clock = pygame.time.Clock()

while True:
    # 1. 상태 업데이트
    sword_angle = (sword_angle + rotation_speed) % 360
    rad_angle = math.radians(sword_angle)
    center_move = (move_x + move_rect_w / 2, move_y + move_rect_h / 2)
    center_fixed = (fixed_x + fixed_rect_w / 2, fixed_y + fixed_rect_h / 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  move_x -= move_speed
    if keys[pygame.K_RIGHT]: move_x += move_speed
    if keys[pygame.K_UP]:    move_y -= move_speed
    if keys[pygame.K_DOWN]:  move_y += move_speed

    # 2. 충돌 판정 계산
    # A) AABB
    collision_aabb = (move_x < fixed_x + fixed_rect_w and move_x + move_rect_w > fixed_x and
                      move_y < fixed_y + fixed_rect_h and move_y + move_rect_h > fixed_y)
    
    # B) Circle
    dist = math.sqrt((center_move[0] - center_fixed[0])**2 + (center_move[1] - center_fixed[1])**2)
    collision_circle = dist < (move_rect_w/2 + fixed_rect_w/2)
    
    # C) OBB (SAT 알고리즘 사용)
    vertices_sword = get_obb_vertices(center_move[0], center_move[1], move_rect_w, move_rect_h, rad_angle)
    vertices_fixed = get_obb_vertices(center_fixed[0], center_fixed[1], fixed_rect_w, fixed_rect_h, 0) # 고정 상자는 각도 0
    collision_obb = check_obb_collision(vertices_sword, vertices_fixed)

    # 3. 화면 그리기
    screen.fill(WHITE)
    pygame.draw.rect(screen, GRAY, (fixed_x, fixed_y, fixed_rect_w, fixed_rect_h)) # 대상 상자

    # 칼 이미지
    rotated_sword = pygame.transform.rotate(sword_img, sword_angle)
    rotated_rect = rotated_sword.get_rect(center=center_move)
    screen.blit(rotated_sword, rotated_rect.topleft)

    # --- 시각화 가이드라인 ---
    # 원형 (파란색)
    pygame.draw.circle(screen, BLUE, (int(center_move[0]), int(center_move[1])), int(move_rect_w/2), 1)
    pygame.draw.circle(screen, BLUE, (int(center_fixed[0]), int(center_fixed[1])), int(fixed_rect_w/2), 1)
    
    # AABB (빨간색)
    pygame.draw.rect(screen, RED, (move_x, move_y, move_rect_w, move_rect_h), 1)
    pygame.draw.rect(screen, RED, (fixed_x, fixed_y, fixed_rect_w, fixed_rect_h), 1)
    
    # OBB (초록색)
    pygame.draw.polygon(screen, GREEN, vertices_sword, 2)

    # --- UI 텍스트 표시 ---
    texts = [
        (f"Circle: {'HIT' if collision_circle else 'IDLE'}", BLUE),
        (f"AABB: {'HIT' if collision_aabb else 'IDLE'}", RED),
        (f"OBB: {'HIT' if collision_obb else 'IDLE'}", GREEN)
    ]
    
    for i, (msg, color) in enumerate(texts):
        surf = font.render(msg, True, color)
        screen.blit(surf, (20, 20 + (i * 30)))

    pygame.display.flip()
    clock.tick(60)