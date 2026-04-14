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
pygame.display.set_caption("Invader_Breaker")
clock = pygame.time.Clock()
font = get_korean_font(36)
font_big = get_korean_font(72)

# --- [수정] 레벨 설정 ---
LEVELS = [
    {"rows": 3, "ball_speed": 5, "label": "Lv.1", "block_interval": 3000}, # 3초
    {"rows": 5, "ball_speed": 6, "label": "Lv.2", "block_interval": 2000}, # 2.5초
    {"rows": 7, "ball_speed": 7, "label": "Lv.3", "block_interval": 1500}, # 2초
]

PAD_W, PAD_H = 100, 12
BALL_R = 8
BLOCK_W, BLOCK_H = 72, 22
BLOCK_COLS = 10
BLOCK_MARGIN = 5
BLOCK_TOP = 60

ITEM_W, ITEM_H = 40, 40
ITEM_SPEED = 3

# --- [추가] 화면 흔들림 설정 ---
SHAKE_INTENSITY = 10  # 얼마나 세게 흔들 것인가
SHAKE_DURATION = 15   # 얼마나 오래 흔들 것인가 (프레임 단위)

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


# --- [수정] 표면(surf)을 인자로 받도록 변경 ---
def draw_hud(surf, score, lives, level_cfg, ammo):
    surf.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    surf.blit(font.render(f"Lives: {'♥ ' * lives}", True, RED), (WIDTH - 250, 10))
    surf.blit(font.render(level_cfg["label"], True, YELLOW), (WIDTH // 2 - 25, 10))
    # 탄약 표시 (남은 개수가 적으면 빨간색으로 보이게)
    ammo_color = WHITE if ammo > 3 else RED
    surf.blit(font.render(f"Ammo: {ammo}", True, ammo_color), (10, 50))


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
    # --- 배경음악 로드 및 재생 ---
    try:
        pygame.mixer.music.load("./sounds/bgmusic.mp3")
        pygame.mixer.music.set_volume(0.3)  # 배경음악은 조금 작게 설정하는 것이 정신 건강에 좋습니다.
        pygame.mixer.music.play(-1)         # -1은 무한 반복을 의미합니다.
    except pygame.error:
        print("경고: ./sounds/bgmusic.mp3 파일을 찾을 수 없습니다.")
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
    
    # --- 총알 이미지 로드 ---
    # 파일 경로가 ./sprites/arrow_right.png 여야 합니다.
    try:
        bullet_img = pygame.image.load("./sprites/arrow_right.png").convert_alpha()
        
        # 크기 조절 (50%로 축소)
        IMAGE_SCALE_FACTOR = 0.5  # 원하시는 비율로 조절하세요 (0.0 ~ 1.0)
        orig_w, orig_h = bullet_img.get_size()
        new_size = (int(orig_w * IMAGE_SCALE_FACTOR), int(orig_h * IMAGE_SCALE_FACTOR))
        bullet_img_scaled = pygame.transform.scale(bullet_img, new_size)
        
        # 회전 (-90도, 시계 방향)
        bullet_img = pygame.transform.rotate(bullet_img_scaled, 90)
        
    except FileNotFoundError:
        print("에러: ./sprites/arrow_right.png 파일을 찾을 수 없습니다.")
        pygame.quit()
        sys.exit()
    
    # ---아이템 이미지 로드 ---
    try:
        # 1. 일단 원본 흰색 다이아몬드를 불러옵니다.
        item_img_raw = pygame.image.load("./sprites/suit_diamonds.png").convert_alpha()
        
        # 2. 크기를 왕창 키웁니다. (전역 상수 ITEM_W, ITEM_H 사용)
        item_img_scaled = pygame.transform.scale(item_img_raw, (ITEM_W, ITEM_H))
        
        # 3. [추가] 흰색 이미지를 초록색으로 물들이는 로직
        # 이미지가 흰색(255, 255, 255)일 때 아주 잘 작동합니다.
        # 같은 크기의 초록색 사각형을 만든 뒤 BLEND_RGBA_MULT 방식으로 덧칠합니다.
        color_surface = pygame.Surface((ITEM_W, ITEM_H)).convert_alpha()
        color_surface.fill((0, 200, 0, 255)) # 초록색 (RGB + 투명도 255)
        item_img_scaled.blit(color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # 4. 최종 변조된 이미지를 저장
        item_img = item_img_scaled
        
    except FileNotFoundError:
        print("경고: ./sprites/suit_diamonds.png 파일을 찾을 수 없습니다.")
        item_img = None
    
    BULLET_W, BULLET_H = bullet_img.get_size() # 탄환 크기
    BULLET_SPEED = 10 # 탄환 속도
    ammo = 10  # 초기 탄약 10발
    
    items = [] # 떨어지는 아이템들을 저장할 리스트
    
    # 블록 하강 관련 변수
    BLOCK_MOVE_INTERVAL = level_cfg["block_interval"]
    last_block_move = pygame.time.get_ticks()
    
    # --- [추가] 효과음 로드 ---
    try:
        shoot_sound = pygame.mixer.Sound("./sounds/gunFire.mp3")
        shoot_sound.set_volume(0.4) # 볼륨 (0.0 ~ 1.0)
    except FileNotFoundError:
        print("경고: ./sounds/gunFire.mp3 파일을 찾을 수 없습니다. 소리 없이 진행합니다.")
        shoot_sound = None
    
    # --- [추가] 튕김 효과음 로드 ---
    try:
        bounce_sound = pygame.mixer.Sound("./sounds/slight_boink.wav")
        bounce_sound.set_volume(0.5) # 적당한 볼륨으로 설정
    except FileNotFoundError:
        print("경고: ./sounds/slight_boink.wav 파일을 찾을 수 없습니다.")
        bounce_sound = None
        
    shake_timer = 0  # 화면 흔들림 남은 시간
    # 가상의 도화지 생성 (화면과 같은 크기)
    display_surface = pygame.Surface((WIDTH, HEIGHT))

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
                        # --- [수정] 스프라이트 이미지를 사용하는 방식으로 총알 생성 ---
                        # 이미지의 midbottom 좌표를 패들의 중앙 위쪽에 맞춥니다.
                        new_bullet = bullet_img.get_rect(midbottom=(pad.centerx, pad.top))
                        bullets.append(new_bullet)
                        ammo -= 1  # 발사 시 탄약 감소
                        
                        # --- [추가] 총소리 재생 ---
                        if shoot_sound:
                            shoot_sound.play()
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
                    shake_timer = 30
                    pygame.mixer.music.stop() # 메시지 창 띄우기 전에 음악 정지
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
            
            # 벽에 부딪혔을때 튕기는 코드
            if ball.left <= 0:
                if bounce_sound: bounce_sound.play()
                ball.left = 0  # 왼쪽 벽 밖으로 강제 위치 고정
                bx = -bx
            elif ball.right >= WIDTH:
                if bounce_sound: bounce_sound.play()
                ball.right = WIDTH  # 오른쪽 벽 밖으로 강제 위치 고정
                bx = -bx
            if ball.top <= 0:
                if bounce_sound: bounce_sound.play()
                by = -by

            if ball.colliderect(pad) and by > 0:
                if bounce_sound: bounce_sound.play()
                offset = (ball.centerx - pad.centerx) / (PAD_W / 2)
                bx = int(offset * level_cfg["ball_speed"]) or bx
                by = -abs(by)
            
            # 아이템 로직
            for item in items[:]:
                item["rect"].y += ITEM_SPEED # 아래로 낙하
            
                # 패들이 아이템을 먹었을 때
                if item["rect"].colliderect(pad):
                    ammo += 10  # 총알 10발 충전 (원하시는 만큼 조절하세요)
                    items.remove(item)
                    continue
                
                # 화면 밖으로 나가면 제거
                if item["rect"].top > HEIGHT:
                    items.remove(item)
            
            # --- 블록 충돌 로직 ---
            hit_block = None
            for b in blocks:
                if ball.colliderect(b["rect"]):
                    hit_block = b
                    
                    # 어느 면에서 부딪혔는지 계산하여 반사 방향 결정
                    overlap_left = abs(ball.right - b["rect"].left)
                    overlap_right = abs(ball.left - b["rect"].right)
                    overlap_top = abs(ball.bottom - b["rect"].top)
                    overlap_bottom = abs(ball.top - b["rect"].bottom)

                    if min(overlap_left, overlap_right) < min(overlap_top, overlap_bottom):
                        bx = -bx # 옆면 충돌
                    else:
                        by = -by # 윗면/아랫면 충돌
                    
                    break # 한 번에 블록 하나만 처리

            if hit_block:
                if bounce_sound: bounce_sound.play()
                hit_block["hp"] -= 1
                if hit_block["hp"] <= 0:
                    blocks.remove(hit_block)
                    score += 10
                    if random.random() < 0.1: # 10% 확률로 아이템 생성
                        new_item = {
                            "rect": pygame.Rect(hit_block["rect"].centerx - 10, hit_block["rect"].bottom, 20, 20),
                            "type": "AMMO"
                        }
                        items.append(new_item)
            
            # 공 놓쳤을때
            if ball.bottom >= HEIGHT:
                # miss_sound.play()
                lives -= 1
                shake_timer = SHAKE_DURATION
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
                    pygame.mixer.music.stop() # 메시지 창 띄우기 전에 음악 정지
                    if message_screen("GAME OVER", RED, score):
                        main()
                    return

            if not blocks:
                # clear_sound.play()
                level_idx += 1
                if level_idx >= len(LEVELS):
                    pygame.mixer.music.stop() # 최종 클리어 시 정지
                    if message_screen("CLEAR!", YELLOW, score):
                        main()
                    return
                
                level_cfg = LEVELS[level_idx]
                blocks = make_blocks(level_cfg["rows"])
                
                # --- [추가] 다음 레벨의 블록 하강 속도로 갱신 ---
                BLOCK_MOVE_INTERVAL = level_cfg["block_interval"]
                
                launched = False
                ball.center = (WIDTH // 2, HEIGHT // 2)
                bx, by = level_cfg["ball_speed"], -level_cfg["ball_speed"]
        
        
        # --- [수정] 화면 그리기 로직 ---
        # 1. 모든 그림은 이제 screen이 아니라 display_surface에 그립니다.
        display_surface.fill(GRAY)
        
        for b in blocks: pygame.draw.rect(display_surface, b["color"], b["rect"])
        pygame.draw.rect(display_surface, WHITE, pad)
        pygame.draw.ellipse(display_surface, WHITE, ball)
        for bullet in bullets: display_surface.blit(bullet_img, bullet)
        for item in items:
            if item_img: display_surface.blit(item_img, item["rect"])
            else: pygame.draw.rect(display_surface, GREEN, item["rect"])
        
        if not launched:
            text_surf = font.render("SPACE to launch", True, YELLOW)
            display_surface.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, HEIGHT // 2 + 40))
        
        draw_hud(display_surface, score, lives, level_cfg, ammo) # HUD도 가상 표면에 그림

        # 2. 흔들림 계산
        render_offset = [0, 0]
        if shake_timer > 0:
            render_offset[0] = random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
            render_offset[1] = random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
            shake_timer -= 1

        # 3. 가상 표면을 실제 screen에 오프셋을 줘서 붙임
        screen.fill(BLACK) # 배경을 검은색으로 비우고
        screen.blit(display_surface, render_offset)
        pygame.display.flip()
main()