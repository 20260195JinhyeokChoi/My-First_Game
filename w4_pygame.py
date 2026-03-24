import pygame
import sys

# 파이게임 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AABB Visualization")

# 색상 정의
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
YELLOW = (255, 255, 0) # 충돌 시 표시할 색상

# 움직이는 사각형 설정
move_rect_width, move_rect_height = 50, 50
move_rect_x = (WIDTH // 4) - (move_rect_width // 2)
move_rect_y = (HEIGHT // 2) - (move_rect_height // 2)
move_speed = 5

# 고정된 사각형 설정
fixed_rect_width, fixed_rect_height = 100, 100
fixed_rect_x = (WIDTH // 2) - (fixed_rect_width // 2)
fixed_rect_y = (HEIGHT // 2) - (fixed_rect_height // 2)

# 시계 설정 (프레임 속도 제어)
clock = pygame.time.Clock()

# 메인 게임 루프
running = True
while running:
    # 1. 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. 키 입력 처리 (움직이는 사각형 이동)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        move_rect_x -= move_speed
    if keys[pygame.K_RIGHT]:
        move_rect_x += move_speed
    if keys[pygame.K_UP]:
        move_rect_y -= move_speed
    if keys[pygame.K_DOWN]:
        move_rect_y += move_speed

    # 3. 충돌 감지 로직 (AABB 충돌 테스트)
    # 두 사각형이 충돌했는지 확인하는 논리 연산입니다.
    # 각 사각형의 AABB가 x축과 y축 모두에서 겹칠 때 충돌입니다.
    collision = (
        move_rect_x < fixed_rect_x + fixed_rect_width and
        move_rect_x + move_rect_width > fixed_rect_x and
        move_rect_y < fixed_rect_y + fixed_rect_height and
        move_rect_y + move_rect_height > fixed_rect_y
    )

    # 충돌 여부에 따라 AABB 테두리 색상 결정
    aabb_color = YELLOW if collision else RED

    # 4. 화면 그리기
    # 배경 채우기
    screen.fill(WHITE)

    # 오브젝트 그리기 (회색 사각형)
    pygame.draw.rect(screen, GRAY, (move_rect_x, move_rect_y, move_rect_width, move_rect_height))
    pygame.draw.rect(screen, GRAY, (fixed_rect_x, fixed_rect_y, fixed_rect_width, fixed_rect_height))

    # [새로운 기능] AABB 표시 (빨간색 테두리)
    # pygame.draw.rect() 함수에 마지막 인자로 두께(width)를 주면 테두리만 그립니다.
    # 오브젝트 자체와 AABB가 일치하므로 오브젝트 테두리에 그리게 됩니다.
    pygame.draw.rect(screen, aabb_color, (move_rect_x, move_rect_y, move_rect_width, move_rect_height), 2)
    pygame.draw.rect(screen, aabb_color, (fixed_rect_x, fixed_rect_y, fixed_rect_width, fixed_rect_height), 2)

    # 5. 화면 업데이트
    pygame.display.flip()

    # 6. 프레임 속도 제한 (FPS)
    clock.tick(60)

# 파이게임 종료
pygame.quit()
sys.exit()