import pygame
import sys
import random

pygame.init()

#한국폰트 불러오기
def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return pygame.font.SysFont(None, size)


WIDTH, HEIGHT = 800, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
BLUE = (50, 120, 220)
RED = (220, 50, 50)
YELLOW = (240, 200, 0)
ORANGE = (240, 140, 0)
GREEN = (50, 200, 50)

BLOCK_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout")
clock = pygame.time.Clock()
font = get_korean_font(36)
font_big = get_korean_font(72)

# --- 레벨 설정 ---
LEVELS = [
    {"rows": 3, "ball_speed": 5, "label": "Lv.1"},
    {"rows": 5, "ball_speed": 6, "label": "Lv.2"},
    {"rows": 7, "ball_speed": 8, "label": "Lv.3"},
]

# --- 사운드 자리 ---
# hit_block_sound  = pygame.mixer.Sound("hit_block.wav")
# hit_wall_sound   = pygame.mixer.Sound("hit_wall.wav")
# miss_sound       = pygame.mixer.Sound("miss.wav")
# clear_sound      = pygame.mixer.Sound("clear.wav")

PAD_W, PAD_H = 100, 12
BALL_R = 8
BLOCK_W, BLOCK_H = 72, 22
BLOCK_COLS = 10
BLOCK_MARGIN = 5
BLOCK_TOP = 60


def make_blocks(rows):
    blocks = []
    for r in range(rows):
        for c in range(BLOCK_COLS):
            x = BLOCK_MARGIN + c * (BLOCK_W + BLOCK_MARGIN)
            y = BLOCK_TOP + r * (BLOCK_H + BLOCK_MARGIN)
            color = BLOCK_COLORS[r % len(BLOCK_COLORS)]
            blocks.append(
                {
                    "rect": pygame.Rect(x, y, BLOCK_W, BLOCK_H),
                    "color": color,
                    "hp": 1,
                    "original_y": y
                }
            )
    return blocks


def draw_hud(score, lives, level_cfg, ammo):
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Lives: {'♥ ' * lives}", True, RED), (WIDTH - 250, 10))
    screen.blit(font.render(level_cfg["label"], True, YELLOW), (WIDTH // 2 - 25, 10))
    # 탄약 표시 (남은 개수가 적으면 빨간색으로 보이게)
    ammo_color = WHITE if ammo > 3 else RED
    screen.blit(font.render(f"Ammo: {ammo}", True, ammo_color), (10, 50))


def message_screen(title, color, score):
    screen.fill(GRAY)
    screen.blit(font_big.render(title, True, color), (WIDTH // 2 - 180, 220))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (350, 310))
    screen.blit(font.render("R: Restart   Q: Quit", True, WHITE), (270, 360))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return True
                if e.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


def main():
    level_idx = 0
    level_cfg = LEVELS[level_idx]

    pad = pygame.Rect(WIDTH // 2 - PAD_W // 2, HEIGHT - 40, PAD_W, PAD_H)
    ball = pygame.Rect(WIDTH // 2 - BALL_R, HEIGHT // 2, BALL_R * 2, BALL_R * 2)
    bx, by = level_cfg["ball_speed"], level_cfg["ball_speed"]
    blocks = make_blocks(level_cfg["rows"])
    score = 0
    lives = 3
    launched = False
    pre_launch_bx = level_cfg["ball_speed"]
    
    bullets = [] # 탄환들을 저장할 리스트
    BULLET_W, BULLET_H = 4, 10 # 탄환 크기
    BULLET_SPEED = 10 # 탄환 속도
    ammo = 10  # 초기 탄약 10발
    
    items = [] # 떨어지는 아이템들을 저장할 리스트
    ITEM_W, ITEM_H = 20, 20
    ITEM_SPEED = 3
    
    # 블록 하강 관련 변수
    BLOCK_MOVE_INTERVAL = 3000  # 3초마다 하강
    last_block_move = pygame.time.get_ticks()

    while True:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # 위 방향키를 누르면 탄환 생성
            if e.type == pygame.KEYDOWN and e.key == pygame.K_UP:
                if launched: # 이 조건문이 핵심입니다!
                    if ammo > 0:
                        new_bullet = pygame.Rect(pad.centerx - BULLET_W // 2, pad.top - BULLET_H, BULLET_W, BULLET_H)
                        bullets.append(new_bullet)
                        ammo -= 1  # 발사 시 탄약 감소
                    else:
                        print("탄약 부족!")
                
            # 스페이스바 처리 부분 
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                # 공이 '아직' 발사되지 않은 상태일 때만 발사 로직을 실행합니다.
                if not launched: 
                    launched = True
                    # 아래(+speed)로 날아가게 설정
                    by = abs(level_cfg["ball_speed"]) 
                    # 현재 좌우 왕복하던 속도를 그대로 반영
                    bx = pre_launch_bx
                    # 발사하는 순간부터 3초를 새로 잽니다.
                    last_block_move = pygame.time.get_ticks()

        # 패들 이동 처리
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and pad.left > 0:
            pad.x -= 7
        if keys[pygame.K_RIGHT] and pad.right < WIDTH:
            pad.x += 7
        
        #발사 전 대기
        if not launched:
            # 1. 공의 좌우 왕복 이동 (y좌표는 고정)
            ball.x += pre_launch_bx
            
            # 2. 화면 벽에 부딪히면 튕기기
            if ball.left <= 0 or ball.right >= WIDTH:
                pre_launch_bx = -pre_launch_bx
        
        # 탄환 이동 및 블록 충돌 로직
        if launched:
            # 인베이더 스타일: 블록 하강 로직
            if current_time - last_block_move > BLOCK_MOVE_INTERVAL:
                for b in blocks:
                    b["rect"].y += 15  # 15픽셀씩 아래로
                last_block_move = current_time # 타이머 리셋
            
            # 압사 조건 체크: 블록이 패들 높이까지 내려오면 게임 오버
            for b in blocks:
                if b["rect"].bottom > pad.top:
                    if message_screen("CRUSHED!", RED, score):
                        main()
                
            for bullet in bullets[:]:  # 복사본으로 반복문 돌리기 (삭제 시 에러 방지)
                bullet.y -= BULLET_SPEED # 탄환을 위로 이동
            
                # 화면 밖으로 나가면 탄환 제거
                if bullet.bottom < 0:
                    bullets.remove(bullet)
                    continue

                # 탄환과 블록 충돌 체크
                for b in blocks[:]:
                    if bullet.colliderect(b["rect"]):
                        b["hp"] -= 1
                        if b["hp"] <= 0:
                            # 아이템 생성 로직
                            if random.random() < 0.1: # 10% 확률
                                new_item = {
                                    "rect": pygame.Rect(b["rect"].centerx - 10, b["rect"].bottom, 20, 20),
                                    "type": "AMMO"
                                }
                                items.append(new_item)
                            blocks.remove(b)
                            score += 10
                        # 탄환이 이미 리스트에 있을 때만 삭제 (중복 삭제 방지)
                        if bullet in bullets:
                            bullets.remove(bullet)
                        break
        
            ball.x += bx
            ball.y += by
            
            # 아이템 로직
            for item in items[:]:
                item["rect"].y += ITEM_SPEED # 아래로 낙하
            
                # 패들이 아이템을 먹었을 때
                if item["rect"].colliderect(pad):
                    ammo += 2  # 총알 2발 충전 (원하시는 만큼 조절하세요)
                    items.remove(item)
                    continue
                
                # 화면 밖으로 나가면 제거
                if item["rect"].top > HEIGHT:
                    items.remove(item)
            
            # 벽에 부딪혔을때 튕기는 코드
            if ball.left <= 0:
                ball.left = 0  # 왼쪽 벽 밖으로 강제 위치 고정
                bx = -bx
            elif ball.right >= WIDTH:
                ball.right = WIDTH  # 오른쪽 벽 밖으로 강제 위치 고정
                bx = -bx
            if ball.top <= 0:
                # hit_wall_sound.play()
                by = -by

            if ball.colliderect(pad) and by > 0:
                # hit_wall_sound.play()
                offset = (ball.centerx - pad.centerx) / (PAD_W / 2)
                bx = int(offset * level_cfg["ball_speed"]) or bx
                by = -abs(by)

            hit_block = None
            for b in blocks:
                if ball.colliderect(b["rect"]):
                    hit_block = b
                    break
            if hit_block:
                # hit_block_sound.play()
                hit_block["hp"] -= 1
                if hit_block["hp"] <= 0:
                    blocks.remove(hit_block)
                    score += 10
                    # [추가] 10% 확률로 아이템 생성
                    if random.random() < 0.1: # 0.0 ~ 1.0 사이 난수
                        new_item = {
                            "rect": pygame.Rect(hit_block["rect"].centerx - 10, hit_block["rect"].bottom, 20, 20),
                            "type": "AMMO"
                        }
                        items.append(new_item)
                by = -by
            
            # 공 놓쳤을때
            if ball.bottom >= HEIGHT:
                # miss_sound.play()
                lives -= 1
                launched = False
                ball.center = (WIDTH // 2, HEIGHT // 2)
                bullets.clear() # 날아가던 총알 삭제
                items.clear()   # 떨어지던 아이템 삭제
                # 모든 블록의 위치를 초기화
                # r (행 번호)을 다시 계산해서 원래 y 위치로 보냅니다.
                for b in blocks:
                    b["rect"].y = b["original_y"] # 기억해둔 원래 위치로 강제 소환
                
                # 타이머도 초기화해서 부활하자마자 블록이 내려오는 걸 방지
                last_block_move = pygame.time.get_ticks()

                if lives <= 0:
                    if message_screen("GAME OVER", RED, score):
                        main()
                    return

            if not blocks:
                # clear_sound.play()
                level_idx += 1
                if level_idx >= len(LEVELS):
                    if message_screen("CLEAR!", YELLOW, score):
                        main()
                    return
                level_cfg = LEVELS[level_idx]
                blocks = make_blocks(level_cfg["rows"])
                launched = False
                ball.center = (WIDTH // 2, HEIGHT // 2)
                bx, by = level_cfg["ball_speed"], -level_cfg["ball_speed"]
        
        
        # 화면 그리기
        screen.fill(GRAY)
        
        # 1. 블록 그리기
        for b in blocks:
            pygame.draw.rect(screen, b["color"], b["rect"])
            
        # 2. 패들/공 그리기
        pygame.draw.rect(screen, WHITE, pad)
        pygame.draw.ellipse(screen, WHITE, ball)
        
        # 3. 탄환 그리기
        for bullet in bullets:
            pygame.draw.rect(screen, YELLOW, bullet)
        
        # 4. 아이템 그리기
        for item in items:
            # 총알 아이템은 눈에 띄게 초록색이나 하늘색으로!
            pygame.draw.rect(screen, GREEN, item["rect"])
            
        # 5. 발사 전 안내 문구 (시작 안 했을 때만)
        if not launched:
            text_surf = font.render("SPACE to launch", True, YELLOW)
            screen.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, HEIGHT // 2 + 40))
            
        # 6. HUD 및 업데이트
        draw_hud(score, lives, level_cfg, ammo)
        pygame.display.flip()
main()