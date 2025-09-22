from pathlib import Path
import pygame
import random
import sys

# Initialize PyGame
pygame.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)

ASSETS = Path("/Users/ralph/dev/coding4kids/pyphaser/pyphaser/src/pyphaser/resources")

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyGame Platformer")

clock = pygame.time.Clock()

# Load images
background = pygame.image.load(str(ASSETS / "sky.png"))
ground_img = pygame.image.load(str(ASSETS / "platform.png"))
star_img = pygame.image.load(str(ASSETS / "star.png"))
bomb_img = pygame.image.load(str(ASSETS / "bomb.png"))
dude_img = pygame.image.load(str(ASSETS / "dude.png"))

dude_frames = [dude_img.subsurface((32*i, 0, 32, 48)) for i in range(9)]

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Take frame 4 (standing)
        self.frames_left = dude_frames[0:4]
        self.frame_idle = dude_frames[4]
        self.frames_right = dude_frames[5:9]
        self.image = self.frame_idle
        # self.image = dude_img.subsurface((32*4, 0, 32, 48))
        self.rect = self.image.get_rect()
        self.rect.center = (100, 450)
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False

        # Animation control
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.15  # lower = slower
        self.facing = "idle"

    def update(self, keys):
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -5
            self.facing = 'left'
        elif keys[pygame.K_RIGHT]:
            self.vel_x = 5
            self.facing = 'right'
        else:
            self.facing = 'idle'

        if (keys[pygame.K_UP] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel_y = -15

        # Apply gravity
        self.vel_y += 0.5
        if self.vel_y > 10:
            self.vel_y = 10

        # Move
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        self.animate()

    def animate(self):
        if self.facing == "left":
            self.anim_timer += self.anim_speed
            if self.anim_timer >= 1:
                self.anim_timer = 0
                self.anim_index = (self.anim_index + 1) % len(self.frames_left)
            self.image = self.frames_left[self.anim_index]

        elif self.facing == "right":
            self.anim_timer += self.anim_speed
            if self.anim_timer >= 1:
                self.anim_timer = 0
                self.anim_index = (self.anim_index + 1) % len(self.frames_right)
            self.image = self.frames_right[self.anim_index]

        else:  # idle
            self.image = self.frame_idle
            self.anim_index = 0
            self.anim_timer = 0

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w=0, h=0):
        super().__init__()
        self.image = ground_img
        if w and h:
            self.image = pygame.transform.scale(ground_img, (w, h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Star class
class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = star_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.bounce = random.uniform(0.4, 0.8)
        self.vel_y = 0

    def update(self, *args):
        self.vel_y += 0.3
        if self.vel_y > 6:
            self.vel_y = 6
        self.rect.y += self.vel_y

# Bomb class
class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bomb_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = random.choice([-2, 2])
        self.vel_y = 2

    def update(self, *args):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Bounce off screen walls
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.vel_x *= -1
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vel_y *= -1

# Groups
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
stars = pygame.sprite.Group()
bombs = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Create platforms
ground = Platform(0, 568, 800, 32)
platform_list = [
    ground,
    Platform(600, 400),
    Platform(50, 250),
    Platform(750, 220)
]
for p in platform_list:
    all_sprites.add(p)
    platforms.add(p)

# Create stars
for i in range(12):
    star = Star(12 + i*70, 0)
    all_sprites.add(star)
    stars.add(star)

# Score
score = 0
font = pygame.font.SysFont(None, 36)
game_over = False

# Main loop
running = True
while running:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        # Update
        all_sprites.update(keys)

        # Collision with platforms (player)
        player.on_ground = False
        hits = pygame.sprite.spritecollide(player, platforms, False)
        # for platform in hits:
        #     if player.vel_y > 0:
        #         player.rect.bottom = platform.rect.top
        #         player.vel_y = 0
        #         player.on_ground = True
        for platform in hits:
            if player.vel_y > 0:  # falling
                player.rect.bottom = platform.rect.top
                player.vel_y = 0
                player.on_ground = True
            elif player.vel_y < 0:  # jumping up into platform
                player.rect.top = platform.rect.bottom
                player.vel_y = 0

        # Collision with platforms (stars)
        for star in stars:
            if pygame.sprite.spritecollide(star, platforms, False):
                star.vel_y = -star.vel_y * star.bounce

        for bomb in bombs:
            hits = pygame.sprite.spritecollide(bomb, platforms, False)
            for platform in hits:
                if bomb.vel_y > 0:  # falling
                    bomb.rect.bottom = platform.rect.top
                    bomb.vel_y = -bomb.vel_y * 0.9
                elif bomb.vel_y < 0:  # hitting underside
                    bomb.rect.top = platform.rect.bottom
                    bomb.vel_y = -bomb.vel_y * 0.9

        # Collect stars
        star_hits = pygame.sprite.spritecollide(player, stars, True)
        for star in star_hits:
            score += 10

        if len(stars) == 0:
            # Respawn stars
            for i in range(12):
                star = Star(12 + i*70, 0)
                all_sprites.add(star)
                stars.add(star)

            # Add bomb
            x = random.randint(400, 800) if player.rect.x < 400 else random.randint(0, 400)
            bomb = Bomb(x, 16)
            all_sprites.add(bomb)
            bombs.add(bomb)

        # Hit bomb
        if pygame.sprite.spritecollide(player, bombs, False):
            game_over = True

    # Draw
    screen.blit(background, (0, 0))
    all_sprites.draw(screen)

    # Score text
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (16, 16))

    # Game over text
    if game_over:
        over_text = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(over_text, (WIDTH//2 - 80, HEIGHT//2))

    pygame.display.flip()

pygame.quit()
sys.exit()

def main():
    pass