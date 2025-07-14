import pygame, random

pygame.init()
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("1930")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Load Sounds
pygame.mixer.init()
background_music = pygame.mixer.Sound("background_music.ogg")
clap_sound = pygame.mixer.Sound("clap.ogg")
oh_no_sound = pygame.mixer.Sound("oh_no.ogg")
background_music.play(loops=-1)

# Colors
MODES = [
    {
        'bg': (30, 30, 30),
        'player': (200, 200, 50),
        'item': (50, 200, 200),
        'giant': (255, 0, 0),
        'obstacle': (200, 0, 200),
        'text': (255, 255, 255)
    },
    {
        'bg': (255, 255, 255),
        'player': (0, 100, 200),
        'item': (50, 200, 200),
        'giant': (255, 0, 0),
        'obstacle': (200, 0, 200),
        'text': (0, 0, 0)
    }
]
mode_index = 0
current_theme = MODES[mode_index]

player = pygame.Rect(WIDTH//2 - 25, HEIGHT - 60, 50, 50)
player_speed = 5

items = []
giants = []
obstacles = []
item_timer = 0
score = 0
high_score = 0
paused = False

last_clap_score = 0
last_mode_change_score = 0
game_over = False

# UI Buttons
buttons = {
    'play_pause': pygame.Rect(10, 10, 120, 30),
    'restart': pygame.Rect(WIDTH//2 - 60, HEIGHT//2 + 50, 120, 40)
}

def draw_glow_circle(surface, color, pos, radius):
    glow_color = (*color, 100)
    for i in range(5, 0, -1):
        pygame.draw.circle(surface, glow_color, pos, radius + i * 2)
    pygame.draw.circle(surface, color, pos, radius)

def draw_spiky_circle(surface, color, center, radius, spikes=8):
    pygame.draw.circle(surface, color, center, radius)
    for i in range(spikes):
        angle = i * (360 / spikes)
        x = int(center[0] + (radius + 8) * pygame.math.Vector2(1, 0).rotate(angle).x)
        y = int(center[1] + (radius + 8) * pygame.math.Vector2(1, 0).rotate(angle).y)
        pygame.draw.line(surface, color, center, (x, y), 2)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if buttons['play_pause'].collidepoint(event.pos):
                paused = not paused
            elif game_over and buttons['restart'].collidepoint(event.pos):
                game_over = False
                score = 0
                items.clear()
                giants.clear()
                obstacles.clear()
                player.x = WIDTH//2 - 25
                last_clap_score = 0
                last_mode_change_score = 0
                mode_index = 0
                current_theme = MODES[mode_index]

    if not paused and not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player.x -= player_speed
        if keys[pygame.K_RIGHT]: player.x += player_speed
        player.x = max(0, min(WIDTH - player.width, player.x))

        if score >= last_mode_change_score + 150:
            mode_index = (mode_index + 1) % len(MODES)
            current_theme = MODES[mode_index]
            last_mode_change_score = score

        if score >= last_clap_score + 100:
            clap_sound.play()
            last_clap_score = score

        item_timer += 1
        if item_timer > 30:
            item_timer = 0
            x = random.randint(20, WIDTH - 20)
            items.append({'pos': [x, 0], 'radius': 10})

            if score > 0 and score % 5 == 0:
                gx = random.randint(30, WIDTH - 30)
                giants.append({'pos': [gx, 0], 'radius': 15})

            if random.random() < 0.1:
                ox = random.randint(30, WIDTH - 30)
                obstacles.append({'pos': [ox, 0], 'radius': 20})

        for item in items[:]:
            item['pos'][1] += 4
            if pygame.Rect(player).collidepoint(item['pos'][0], item['pos'][1]):
                score += 1
                items.remove(item)
            elif item['pos'][1] > HEIGHT:
                items.remove(item)

        for giant in giants[:]:
            giant['pos'][1] += 3
            if pygame.Rect(player).collidepoint(giant['pos'][0], giant['pos'][1]):
                score += 10
                giants.remove(giant)
            elif giant['pos'][1] > HEIGHT:
                giants.remove(giant)

        for obs in obstacles[:]:
            obs['pos'][1] += 5
            if pygame.Rect(player).collidepoint(obs['pos'][0], obs['pos'][1]):
                oh_no_sound.play()
                game_over = True
            elif obs['pos'][1] > HEIGHT:
                obstacles.remove(obs)

        if score > high_score:
            high_score = score

    # Drawing
    screen.fill(current_theme['bg'])
    pygame.draw.rect(screen, current_theme['player'], player)

    for item in items:
        pygame.draw.circle(screen, current_theme['item'], item['pos'], item['radius'])

    for giant in giants:
        draw_glow_circle(screen, current_theme['giant'], giant['pos'], giant['radius'])

    for obs in obstacles:
        draw_spiky_circle(screen, current_theme['obstacle'], obs['pos'], obs['radius'])

    score_text = font.render(f"Score: {score}  High Score: {high_score}", True, current_theme['text'])
    screen.blit(score_text, (10, 100))

    pygame.draw.rect(screen, (100, 100, 100), buttons['play_pause'])
    screen.blit(font.render("Pause" if not paused else "Play", True, (255, 255, 255)), (buttons['play_pause'].x + 10, buttons['play_pause'].y + 5))

    if game_over:
        game_over_text = font.render("Game Over!", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 40))
        pygame.draw.rect(screen, (0, 200, 0), buttons['restart'])
        screen.blit(font.render("Replay", True, (255, 255, 255)), (buttons['restart'].x + 20, buttons['restart'].y + 5))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
