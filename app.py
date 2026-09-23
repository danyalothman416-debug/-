import pygame
import sys

# دەستپێکردنی بزوێنەری یاری
pygame.init()

# دیاریکردنی قەبارەی شاشە
WIDTH, HEIGHT = 600, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("یەکەم یاریی من لەگەڵ دانیال")

# ڕەنگەکان
BLACK = (10, 12, 18)
WHITE = (255, 255, 255)
BLUE = (10, 132, 255)
GREEN = (48, 209, 88)
RED = (255, 69, 58)

# کاتژمێری خێرایی یاری
clock = pygame.time.Clock()

# زانیارییەکانی تەختەی کۆنتڕۆڵ (Paddle)
paddle_w, paddle_h = 100, 15
paddle_x = (WIDTH - paddle_w) // 2
paddle_y = HEIGHT - 40
paddle_speed = 8

# زانیارییەکانی تۆپەکە (Ball)
ball_size = 14
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_dx = 4
ball_dy = -4

score = 0
font = pygame.font.SysFont("Arial", 22, bold=True)

# ئەڵقەی سەرەکیی یاری (Game Loop)
running = True
while running:
    # ١. پشکنینی ڕووداوەکان و داخستن
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ٢. کۆنتڕۆڵکردنی تەختەکە بە کیبۆرد (تیرەکانی چەپ و ڕاست)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle_x > 0:
        paddle_x -= paddle_speed
    if keys[pygame.K_RIGHT] and paddle_x < WIDTH - paddle_w:
        paddle_x += paddle_speed

    # ٣. جووڵاندنی تۆپەکە
    ball_x += ball_dx
    ball_y += ball_dy

    # بەرکەوتن بە دیوارەکانی چەپ، ڕاست و سەرەوە
    if ball_x <= 0 or ball_x >= WIDTH - ball_size:
        ball_dx = -ball_dx
    if ball_y <= 0:
        ball_dy = -ball_dy

    # بەرکەوتنی تۆپەکە بە تەختەکە (Paddle)
    if (paddle_y <= ball_y + ball_size <= paddle_y + paddle_h) and (paddle_x <= ball_x <= paddle_x + paddle_w):
        ball_dy = -ball_dy
        score += 1

    # ئەگەر تۆپەکە بکەوێتە خوارەوە (دۆڕان و دووبارە دەستپێکردنەوە)
    if ball_y > HEIGHT:
        score = 0
        ball_x, ball_y = WIDTH // 2, HEIGHT // 2
        ball_dy = -4

    # ٤. کێشانی گرافیک لەسەر شاشە
    screen.fill(BLACK)
    
    # کێشانی تەختە و تۆپ
    pygame.draw.rect(screen, BLUE, (paddle_x, paddle_y, paddle_w, paddle_h), border_radius=6)
    pygame.draw.circle(screen, GREEN, (ball_x, ball_y), ball_size // 2)

    # پیشاندانی خاڵەکان (Score)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 20))

    # نوێکردنەوەی شاشە
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
