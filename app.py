import pygame
import random
import sys

# دەستپێکردنی Pygame
pygame.init()

# ڕەهەندەکانی شاشە
WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Danyal Car Racing 🏎️")
clock = pygame.time.Clock()

# ڕەنگەکان
ASPHALT = (35, 39, 45)
GRASS = (34, 139, 34)
LINE_COLOR = (240, 240, 240)
RED_CAR = (230, 40, 40)
BLUE_CAR = (30, 144, 255)
YELLOW_CAR = (255, 215, 0)
WHITE = (255, 255, 255)
DARK = (15, 15, 20)

# ڕێکخستنی شەقام
ROAD_X = 80
ROAD_WIDTH = 340
ROAD_RIGHT = ROAD_X + ROAD_WIDTH

font = pygame.font.SysFont("Arial", 24, bold=True)
big_font = pygame.font.SysFont("Arial", 40, bold=True)

def draw_car(surface, x, y, color, is_player=False):
    w, h = 48, 85
    # چەرخەکان
    pygame.draw.rect(surface, DARK, (x - 4, y + 10, 8, 18), border_radius=3)
    pygame.draw.rect(surface, DARK, (x + w - 4, y + 10, 8, 18), border_radius=3)
    pygame.draw.rect(surface, DARK, (x - 4, y + h - 28, 8, 18), border_radius=3)
    pygame.draw.rect(surface, DARK, (x + w - 4, y + h - 28, 8, 18), border_radius=3)
    
    # لاشەی سەیارەکە
    pygame.draw.rect(surface, color, (x, y, w, h), border_radius=12)
    # جامی پێشەوە و دواوە
    pygame.draw.rect(surface, (20, 25, 35), (x + 6, y + (22 if is_player else 45), w - 12, 16), border_radius=4)
    pygame.draw.rect(surface, (20, 25, 35), (x + 8, y + (55 if is_player else 18), w - 16, 12), border_radius=3)
    # سەقف
    pygame.draw.rect(surface, color, (x + 8, y + 36, w - 16, 18))

    # لایتی پێشەوە
    light_color = (255, 255, 180)
    if is_player:
        pygame.draw.circle(surface, light_color, (x + 8, y + 4), 4)
        pygame.draw.circle(surface, light_color, (x + w - 8, y + 4), 4)
    else:
        pygame.draw.circle(surface, (255, 70, 70), (x + 8, y + 4), 3)
        pygame.draw.circle(surface, (255, 70, 70), (x + w - 8, y + 4), 3)

def main():
    # زانیارییەکانی یاریزان
    p_w, p_h = 48, 85
    px = ROAD_X + (ROAD_WIDTH - p_w) // 2
    py = HEIGHT - 130
    pspeed = 7

    # هێڵەکانی شەقام بۆ دروستکردنی جووڵە
    stripes = [i * 90 for i in range(10)]
    stripe_speed = 9

    # سەیارەکانی تر (ئاستەنگەکان)
    traffic = []
    enemy_colors = [BLUE_CAR, YELLOW_CAR, (180, 50, 220), (255, 140, 0)]
    spawn_timer = 0

    score = 0
    game_over = False

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_SPACE:
                    return main()

        if not game_over:
            keys = pygame.key.get_pressed()
            # جووڵەی سەیارەی یاریزان بە چوار ئاراستە
            if keys[pygame.K_LEFT] and px > ROAD_X + 8:
                px -= pspeed
            if keys[pygame.K_RIGHT] and px < ROAD_RIGHT - p_w - 8:
                px += pspeed
            if keys[pygame.K_UP] and py > 40:
                py -= 5
            if keys[pygame.K_DOWN] and py < HEIGHT - p_h - 20:
                py += 5

            # جووڵاندنی هێڵی شەقامەکان
            for i in range(len(stripes)):
                stripes[i] += stripe_speed
                if stripes[i] > HEIGHT:
                    stripes[i] = -70

            # دروستکردنی سەیارەی نوێ
            spawn_timer += 1
            if spawn_timer > 45:
                spawn_timer = 0
                ex = random.randint(ROAD_X + 15, ROAD_RIGHT - p_w - 15)
                espeed = random.randint(5, 8)
                ecolor = random.choice(enemy_colors)
                traffic.append([ex, -100, espeed, ecolor])

            # جووڵەی سەیارەکانی تر و پشکنینی پێکدادان
            player_rect = pygame.Rect(px + 4, py + 4, p_w - 8, p_h - 8)

            for enemy in traffic[:]:
                enemy[1] += enemy[2] + (stripe_speed // 3)
                enemy_rect = pygame.Rect(enemy[0] + 4, enemy[1] + 4, p_w - 8, p_h - 8)

                # پێکدادان (Collision)
                if player_rect.colliderect(enemy_rect):
                    game_over = True

                # سەیارەکە لە شاشە دەچێتە دەرەوە و خاڵ زیاد دەکات
                if enemy[1] > HEIGHT:
                    traffic.remove(enemy)
                    score += 10
                    # زیادکردنی کەمێک لە خێرایی شەقامەکە لەگەڵ بەرزبوونەوەی خاڵەکان
                    if score % 50 == 0 and stripe_speed < 18:
                        stripe_speed += 1

        # کێشانی شاشە
        screen.fill(GRASS)
        # کێشانی قیر
        pygame.draw.rect(screen, ASPHALT, (ROAD_X, 0, ROAD_WIDTH, HEIGHT))
        # هێڵە زەردەکانی قەراغ
        pygame.draw.line(screen, (255, 200, 0), (ROAD_X, 0), (ROAD_X, HEIGHT), 5)
        pygame.draw.line(screen, (255, 200, 0), (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 5)

        # هێڵە سپییەکانی ناوەڕاستی شەقام
        lane_x1 = ROAD_X + ROAD_WIDTH // 3
        lane_x2 = ROAD_X + (ROAD_WIDTH // 3) * 2
        for sy in stripes:
            pygame.draw.rect(screen, LINE_COLOR, (lane_x1 - 3, sy, 6, 45))
            pygame.draw.rect(screen, LINE_COLOR, (lane_x2 - 3, sy, 6, 45))

        # کێشانی سەیارەکانی تر
        for enemy in traffic:
            draw_car(screen, enemy[0], enemy[1], enemy[3], is_player=False)

        # کێشانی سەیارەی یاریزان
        draw_car(screen, px, py, RED_CAR, is_player=True)

        # پیشاندانی خاڵ
        score_surface = font.render(f"SCORE: {score}", True, WHITE)
        screen.blit(score_surface, (20, 20))

        # شاشەی دۆڕان
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            over_txt = big_font.render("CRASHED!", True, (255, 60, 60))
            screen.blit(over_txt, (WIDTH // 2 - over_txt.get_width() // 2, HEIGHT // 2 - 50))

            restart_txt = font.render("Press SPACE to Play Again", True, WHITE)
            screen.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, HEIGHT // 2 + 15))

        pygame.display.flip()

main()
