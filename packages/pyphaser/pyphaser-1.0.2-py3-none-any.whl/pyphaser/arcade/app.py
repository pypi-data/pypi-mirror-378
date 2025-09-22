from pathlib import Path
import random
import arcade

# -------------------- Settings --------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "PyPhaser"
ASSETS = Path("src/pyphaser/resources")
GRAVITY = 1.2
PLAYER_MOVE_SPEED = 5.0
PLAYER_JUMP_SPEED = 26.0
STAR_COUNT = 12
STAR_STEP_X = 70
STAR_START_X = 12
STAR_GRAVITY = 0.6
STAR_BOUNCE_MIN = 0.40
STAR_BOUNCE_MAX = 0.80
BOMB_MIN_SPEED_X = 3.0
BOMB_MAX_SPEED_X = 4.5
BOMB_GRAVITY = 0.9
BOMB_BOUNCE = 0.95


def slice_sheet_safe(sheet_path: Path, fw: int, fh: int, count: int):
    try:
        sheet = arcade.load_spritesheet(str(sheet_path))
        frames = sheet.get_texture_grid(size=(fw, fh), columns=count, count=count)
        if frames and len(frames) >= count:
            return frames
    except Exception:
        pass

    # 2) load_textures with rectangles
    try:
        rects = [(i * fw, 0, fw, fh) for i in range(count)]
        frames = arcade.load_textures(str(sheet_path), rects)
        if frames and len(frames) >= count:
            return frames
    except Exception:
        pass

    # 3) Last resort
    base = arcade.load_texture(str(sheet_path))
    return [base for _ in range(count)]


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate=1/60)
        arcade.set_background_color(arcade.color.WHITE)

        # SpriteLists
        self.bg_list: arcade.SpriteList | None = None
        self.platforms: arcade.SpriteList | None = None
        self.stars: arcade.SpriteList | None = None
        self.bombs: arcade.SpriteList | None = None
        self.player_list: arcade.SpriteList | None = None

        # Player + physics
        self.player: arcade.Sprite | None = None
        self.physics: arcade.PhysicsEnginePlatformer | None = None

        # Anim
        self.walk_left_frames = []
        self.walk_right_frames = []
        self.turn_frame = None
        self.anim_timer = 0.0
        self.anim_rate = 0.1
        self.walk_idx = 0

        # Input
        self.left = False
        self.right = False
        self.up = False

        # Game state
        self.score = 0
        self.game_over = False

    # -------------------- Setup --------------------
    def setup(self):
        self.bg_list = arcade.SpriteList()
        self.platforms = arcade.SpriteList(use_spatial_hash=True)
        self.stars = arcade.SpriteList()
        self.bombs = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.score = 0
        self.game_over = False

        # Background
        sky = arcade.Sprite(str(ASSETS / "sky.png"))
        sky.center_x = SCREEN_WIDTH // 2
        sky.center_y = SCREEN_HEIGHT // 2
        self.bg_list.append(sky)

        # Platforms (ground + ledges)
        ground = arcade.Sprite(str(ASSETS / "platform.png"), scale=2.0)
        # ground.center_x = 400
        ground.center_x = SCREEN_WIDTH // 2
        # ground.center_y = 568
        ground.center_y = 16
        self.platforms.append(ground)

        ledge1 = arcade.Sprite(str(ASSETS / "platform.png"))
        ledge1.center_x = 600
        ledge1.center_y = 400
        self.platforms.append(ledge1)

        ledge2 = arcade.Sprite(str(ASSETS / "platform.png"))
        ledge2.center_x = 50
        ledge2.center_y = 250
        self.platforms.append(ledge2)

        ledge3 = arcade.Sprite(str(ASSETS / "platform.png"))
        ledge3.center_x = 750
        ledge3.center_y = 220
        self.platforms.append(ledge3)

        # Player + animations (Phaser: 0..3 left, 4 idle, 5..8 right)
        frames = slice_sheet_safe(ASSETS / "dude.png", 32, 48, 9)
        self.walk_left_frames = frames[0:4]
        self.turn_frame = frames[4]
        self.walk_right_frames = frames[5:9]

        # IMPORTANT for 3.3.2: construct Sprite empty, then set texture (avoid texture kwarg bug)
        self.player = arcade.Sprite()
        self.player.texture = self.turn_frame
        self.player.scale = 1.5
        self.player.center_x = 100
        self.player.center_y = 450
        self.player_list.append(self.player)

        # Platformer physics
        self.physics = arcade.PhysicsEnginePlatformer(
            self.player,
            walls=self.platforms,
            gravity_constant=GRAVITY
        )

        # Stars
        self.spawn_star_batch()

    def spawn_star_batch(self):
        for i in range(STAR_COUNT):
            x = STAR_START_X + i * STAR_STEP_X
            star = arcade.Sprite(str(ASSETS / "star.png"))
            star.center_x = x
            star.center_y = random.randint(380, 560)  # drop zone
            star.change_y = 0.0
            star.bounce = random.uniform(STAR_BOUNCE_MIN, STAR_BOUNCE_MAX)
            self.stars.append(star)

    def spawn_bomb(self):
        bomb = arcade.Sprite(str(ASSETS / "bomb.png"))
        # Opposite side of player
        x = random.randint(400, 780) if self.player.center_x < 400 else random.randint(20, 400)
        bomb.center_x = x
        bomb.center_y = 560
        bomb.change_x = random.uniform(BOMB_MIN_SPEED_X, BOMB_MAX_SPEED_X) * (1 if random.random() < 0.5 else -1)
        bomb.change_y = -2.0
        self.bombs.append(bomb)

    # -------------------- Events --------------------
    def on_draw(self):
        self.clear()
        self.bg_list.draw()
        self.platforms.draw()
        self.stars.draw()
        self.bombs.draw()
        self.player_list.draw()  # draw Sprite via SpriteList

        # UI
        arcade.draw_text(f"Score: {self.score}", 16, SCREEN_HEIGHT - 48, arcade.color.BLACK, 28)
        if self.game_over:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                             arcade.color.RED, 48, anchor_x="center", anchor_y="center")

    def on_update(self, dt: float):
        if self.game_over:
            return

        # Input → velocity
        self.player.change_x = 0.0
        if self.left and not self.right:
            self.player.change_x = -PLAYER_MOVE_SPEED
        elif self.right and not self.left:
            self.player.change_x = PLAYER_MOVE_SPEED

        if self.up and self.physics.can_jump():
            self.player.change_y = PLAYER_JUMP_SPEED

        # Physics
        self.physics.update()

        # Animate player
        moving = abs(self.player.change_x) > 0.1
        if moving:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_rate:
                self.anim_timer = 0.0
                self.walk_idx = (self.walk_idx + 1) % 4
            self.player.texture = (
                self.walk_right_frames[self.walk_idx]
                if self.player.change_x > 0
                else self.walk_left_frames[self.walk_idx]
            )
        else:
            self.player.texture = self.turn_frame
            self.walk_idx = 0
            self.anim_timer = 0.0

        # Stars: simple gravity + bounce on platforms + floor
        for star in self.stars:
            star.change_y -= STAR_GRAVITY
            star.center_y += star.change_y

            if star.bottom <= 0 and star.change_y < 0:
                star.bottom = 0
                star.change_y = -star.change_y * star.bounce

            hit_list = arcade.check_for_collision_with_list(star, self.platforms)
            for platform in hit_list:
                if star.change_y < 0 and star.center_y >= platform.top:
                    star.bottom = platform.top
                    star.change_y = -star.change_y * star.bounce

        # Collect stars
        for s in arcade.check_for_collision_with_list(self.player, self.stars):
            s.remove_from_sprite_lists()
            self.score += 10

        # Respawn + bomb when all collected
        if len(self.stars) == 0:
            self.spawn_star_batch()
            self.spawn_bomb()

        # Bomb physics + bounces
        for bomb in self.bombs:
            bomb.change_y -= BOMB_GRAVITY
            bomb.center_x += bomb.change_x
            bomb.center_y += bomb.change_y

            if bomb.right >= SCREEN_WIDTH and bomb.change_x > 0:
                bomb.right = SCREEN_WIDTH
                bomb.change_x *= -1
            if bomb.left <= 0 and bomb.change_x < 0:
                bomb.left = 0
                bomb.change_x *= -1

            if bomb.bottom <= 0 and bomb.change_y < 0:
                bomb.bottom = 0
                bomb.change_y = -bomb.change_y * BOMB_BOUNCE
            if bomb.top >= SCREEN_HEIGHT and bomb.change_y > 0:
                bomb.top = SCREEN_HEIGHT
                bomb.change_y = -bomb.change_y * BOMB_BOUNCE

            plats = arcade.check_for_collision_with_list(bomb, self.platforms)
            for plat in plats:
                if bomb.change_y < 0 and bomb.center_y >= plat.top:
                    bomb.bottom = plat.top
                    bomb.change_y = -bomb.change_y * BOMB_BOUNCE
                elif bomb.change_y > 0 and bomb.bottom <= plat.bottom:
                    # Rising, hit underside of platform
                    bomb.top = plat.bottom
                    bomb.change_y = -bomb.change_y * BOMB_BOUNCE

        # Bomb hit → game over
        if arcade.check_for_collision_with_list(self.player, self.bombs):
            self.game_over = True
            self.player.texture = self.turn_frame
            self.player.change_x = 0
            self.player.change_y = 0

        if self.player.left < 0:
            self.player.left = 0
        if self.player.right > SCREEN_WIDTH:
            self.player.right = SCREEN_WIDTH
        if self.player.bottom < 0:
            self.player.bottom = 0
            self.player.change_y = 0
        if self.player.top > SCREEN_HEIGHT:
            self.player.top = SCREEN_HEIGHT
            self.player.change_y = 0

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = True
        elif key in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            self.up = True
        elif key == arcade.key.ENTER and self.game_over:
            self.setup()

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = False
        elif key in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            self.up = False


def main():
    game = Game()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
