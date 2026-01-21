import pygame
import sys
import random
import os

# --- CONFIGURATION ---
WIDTH, HEIGHT = 1280, 720
FPS = 60

# --- DIFFICULTY SETTINGS ---
INITIAL_SCROLL_SPEED = 5   
MAX_SPEED = 25             
SPEED_INCREMENT = 0.5      
SPEED_UP_TIME = 5000       

# Player settings
PLAYER_SPEED = 7 
NITRO_MULTIPLIER = 1.5     # Speed multiplier when holding Shift

# --- ROAD BOUNDARIES ---
ROAD_TOP = 420
ROAD_BOTTOM = 620 
ROAD_LEFT = 0
ROAD_RIGHT = 1280

# --- SETUP ---
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TRON RIDER: ULTIMATE EDITION")
clock = pygame.time.Clock()

# --- CUSTOM EVENTS ---
SPEED_UP_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPEED_UP_EVENT, SPEED_UP_TIME)

# --- FONTS ---
font_score = pygame.font.SysFont("Arial", 30, bold=True)
font_ui = pygame.font.SysFont("Arial", 20)
font_gameover = pygame.font.SysFont("Arial", 60, bold=True)

# --- ASSETS ---
try:
    bg_raw = pygame.image.load("assets/bg.jpg").convert()
    bg_image = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))
    
    bike_raw = pygame.image.load("assets/bike.jpg").convert()
    bike_raw.set_colorkey((255, 255, 255)) 
    bike_flipped = pygame.transform.flip(bike_raw, True, False) 
    bike_image = pygame.transform.scale(bike_flipped, (100, 60))
    
    wall_raw = pygame.image.load("assets/wall.png").convert()
    wall_image = pygame.transform.scale(wall_raw, (50, 50)) 

except FileNotFoundError:
    print("Error: Missing files in assets/ folder.")
    sys.exit()

# --- CLASSES ---

class Particle:
    """ A simple square particle that flies in a random direction """
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(4, 10)
        self.life = 1.0 # 100% opacity
        # Random velocity
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 0.02 # Fade out speed
        if self.life < 0: self.life = 0

    def draw(self, surf):
        if self.life > 0:
            s = pygame.Surface((self.size, self.size))
            s.set_alpha(int(self.life * 255))
            s.fill(self.color)
            surf.blit(s, (self.x, self.y))

# --- FUNCTIONS ---
def get_high_score():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            try: return int(f.read())
            except: return 0
    return 0

def save_high_score(new_score):
    current_high = get_high_score()
    if new_score > current_high:
        with open("highscore.txt", "w") as f:
            f.write(str(new_score))

def draw_text(surf, text, font, color, x, y):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    surf.blit(img, rect)

def reset_game():
    player_rect = bike_image.get_rect()
    player_rect.x = 100
    player_rect.y = 500
    obstacles = []
    particles = []
    score = 0
    bg_x = 0
    current_speed = INITIAL_SCROLL_SPEED
    return player_rect, obstacles, particles, score, bg_x, current_speed

# --- MAIN ---
def main():
    player_rect, obstacles, particles, score, bg_x, current_speed = reset_game()
    high_score = get_high_score()
    
    velocity_x = 0
    velocity_y = 0
    last_spawn_time = pygame.time.get_ticks()
    
    # Game States
    game_active = False # Start at menu
    game_paused = False
    player_dead = False
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        # 1. EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # PAUSE TOGGLE
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p and game_active:
                game_paused = not game_paused

            if game_active and not game_paused and not player_dead:
                # Speed Up Event
                if event.type == SPEED_UP_EVENT:
                    if current_speed < MAX_SPEED:
                        current_speed += SPEED_INCREMENT

                # MOVEMENT
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w: velocity_y = -PLAYER_SPEED
                    if event.key == pygame.K_s: velocity_y = PLAYER_SPEED
                    if event.key == pygame.K_a: velocity_x = -PLAYER_SPEED
                    if event.key == pygame.K_d: velocity_x = PLAYER_SPEED
                
                if event.type == pygame.KEYUP:
                    if event.key in [pygame.K_w, pygame.K_s]: velocity_y = 0
                    if event.key in [pygame.K_a, pygame.K_d]: velocity_x = 0
            
            # RESTART / START
            if (not game_active or player_dead) and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player_rect, obstacles, particles, score, bg_x, current_speed = reset_game()
                high_score = get_high_score()
                game_active = True
                player_dead = False
                game_paused = False
                velocity_x = 0 
                velocity_y = 0

        # --- LOGIC ---
        if game_active and not game_paused:
            
            # NITRO LOGIC
            is_nitro = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            actual_speed = current_speed * (1.5 if is_nitro else 1.0)
            
            # Handle Death Animation
            if player_dead:
                for p in particles: p.update()
                if all(p.life <= 0 for p in particles): # Wait for particles to fade
                    game_active = False # Show Game Over screen

            else:
                # Scroll BG
                bg_x -= actual_speed
                if bg_x <= -WIDTH: bg_x = 0
                
                # Move Player (with Nitro Shake effect)
                shake_y = random.randint(-2, 2) if is_nitro else 0
                player_rect.x += velocity_x
                player_rect.y += velocity_y + shake_y
                
                # Boundaries
                if player_rect.top < ROAD_TOP: player_rect.top = ROAD_TOP
                if player_rect.bottom > ROAD_BOTTOM: player_rect.bottom = ROAD_BOTTOM
                if player_rect.left < 0: player_rect.left = 0
                if player_rect.right > WIDTH: player_rect.right = WIDTH

                # Spawn Obstacles
                # Nitro makes obstacles spawn faster too!
                spawn_speed_modifier = 20 if is_nitro else 20
                current_spawn_rate = 1500 - (current_speed * spawn_speed_modifier) 
                if current_spawn_rate < 300: current_spawn_rate = 300

                if current_time - last_spawn_time > current_spawn_rate:
                    spawn_y = random.randint(ROAD_TOP, ROAD_BOTTOM - 40)
                    new_wall = wall_image.get_rect(midleft=(WIDTH + 50, spawn_y))
                    obstacles.append(new_wall)
                    last_spawn_time = current_time

                # Move Obstacles
                for wall in obstacles[:]:
                    wall.x -= actual_speed
                    
                    if player_rect.colliderect(wall):
                        # --- CRASH LOGIC ---
                        save_high_score(score)
                        player_dead = True
                        # Spawn particles
                        for _ in range(30):
                            p = Particle(player_rect.centerx, player_rect.centery, (200, 50, 50)) # Red
                            particles.append(p)
                            p2 = Particle(player_rect.centerx, player_rect.centery, (200, 200, 200)) # Grey
                            particles.append(p2)
                    
                    if wall.right < 0:
                        obstacles.remove(wall)
                        # Nitro gives double points!
                        score += 2 if is_nitro else 1 

        # --- DRAWING ---
        screen.blit(bg_image, (bg_x, 0))
        screen.blit(bg_image, (bg_x + WIDTH, 0))
        
        if not player_dead:
            screen.blit(bike_image, player_rect)
            # Draw Nitro flames if active
            if game_active and not game_paused and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
                pygame.draw.circle(screen, (0, 255, 255), player_rect.midleft, random.randint(5, 15))

        # Draw Particles (Explosion)
        for p in particles:
            p.draw(screen)
            
        for wall in obstacles:
            screen.blit(wall_image, wall)

        # Draw UI
        if game_active and not player_dead:
            score_surf = font_score.render(f"Score: {score}", True, (255, 255, 255))
            speed_surf = font_ui.render(f"Speed: {int(current_speed)} MPH", True, (0, 255, 255))
            controls_surf = font_ui.render("HOLD SHIFT FOR NITRO!", True, (255, 100, 100))
            
            screen.blit(score_surf, (20, 20))
            screen.blit(speed_surf, (20, 60))
            screen.blit(controls_surf, (20, 90))
            
            if game_paused:
                 draw_text(screen, "PAUSED", font_gameover, (255, 255, 0), WIDTH//2, HEIGHT//2)

        # Start Screen
        if not game_active and not player_dead:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0,0,0))
            screen.blit(overlay, (0,0))
            
            draw_text(screen, "TRON RIDER", font_gameover, (0, 255, 255), WIDTH//2, HEIGHT//2 - 50)
            draw_text(screen, "Avoid Walls. Hold SHIFT for Nitro.", font_ui, (200, 200, 200), WIDTH//2, HEIGHT//2 + 20)
            draw_text(screen, "Press SPACE to Start", font_score, (255, 255, 255), WIDTH//2, HEIGHT//2 + 80)
            draw_text(screen, f"High Score: {high_score}", font_score, (255, 215, 0), WIDTH//2, HEIGHT//2 + 130)

        # Game Over Screen
        if player_dead and all(p.life <= 0 for p in particles):
             overlay = pygame.Surface((WIDTH, HEIGHT))
             overlay.set_alpha(150)
             overlay.fill((50,0,0)) # Red tint
             screen.blit(overlay, (0,0))
             
             draw_text(screen, "WASTED", font_gameover, (255, 0, 0), WIDTH//2, HEIGHT//2 - 50)
             draw_text(screen, f"Score: {score}", font_score, (255, 255, 255), WIDTH//2, HEIGHT//2 + 20)
             draw_text(screen, "Press SPACE to Retry", font_score, (255, 255, 255), WIDTH//2, HEIGHT//2 + 80)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()