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
PLAYER_SPEED = 9
NITRO_MULTIPLIER = 1.8 

# --- NITRO SYSTEM ---
MAX_NITRO_FUEL = 100
NITRO_DRAIN_RATE = 1.0
NITRO_RECHARGE_RATE = 0.3 

# --- ROAD BOUNDARIES ---
ROAD_TOP = 420
ROAD_BOTTOM = 620 
ROAD_LEFT = 0
ROAD_RIGHT = 1280

# --- SETUP ---
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON RIDER: STREET EDITION")
clock = pygame.time.Clock()

# --- CUSTOM EVENTS ---
SPEED_UP_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPEED_UP_EVENT, SPEED_UP_TIME)

# --- FONTS ---
font_score = pygame.font.SysFont("Impact", 30) 
font_ui = pygame.font.SysFont("Arial", 20, bold=True)
font_gameover = pygame.font.SysFont("Impact", 80)
font_title = pygame.font.SysFont("Impact", 100) 

# --- ASSETS ---
try:
    bg_raw = pygame.image.load("assets/bg.jpg").convert()
    bg_image = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))
    
    bike_raw = pygame.image.load("assets/bike.jpg").convert()
    bike_raw.set_colorkey((255, 255, 255)) # Remove white from bike
    bike_flipped = pygame.transform.flip(bike_raw, True, False) 
    bike_image = pygame.transform.scale(bike_flipped, (100, 60))
    
    # --- UPDATED: LOAD MULTIPLE OBSTACLES WITH AUTO-TRANSPARENCY & FLIP ---
    obstacle_images = []
    # List the exact filenames you saved into your assets folder
    files_to_load = ["cone.png", "barrier.png", "fence.png"] 
    
    print("--- Loading Obstacles ---")
    for filename in files_to_load:
        path = os.path.join("assets", filename)
        if os.path.exists(path):
            # 1. Load the raw image
            img_raw = pygame.image.load(path).convert()
            
            # 2. THE MAGIC TRICK: Remove white background
            img_raw.set_colorkey((255, 255, 255))
            
            # 3. The Flip Logic: Check filename to see if it needs flipping
            if "fence" in filename.lower() or "barrier" in filename.lower():
                # Flip horizontally (True), not vertically (False)
                img_final = pygame.transform.flip(img_raw, True, False)
                # Scale barriers a bit bigger
                img_final = pygame.transform.scale(img_final, (80, 60))
            else:
                 # It's a cone or symmetrical object, don't flip
                img_final = img_raw
                # Scale cones a bit smaller
                img_final = pygame.transform.scale(img_final, (50, 50))

            obstacle_images.append(img_final)
            print(f"Loaded and processed: {filename}")
        else:
            print(f"Warning: Could not find {filename}, skipping.")

    # Fallback check
    if not obstacle_images:
        print("ERROR: No obstacle images found! Game cannot run.")
        sys.exit()

except FileNotFoundError:
    print("Error: Missing files in assets/ folder.")
    sys.exit()

# --- CLASSES ---
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(4, 10)
        self.life = 1.0 
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 0.02 
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
    nitro_fuel = MAX_NITRO_FUEL 
    return player_rect, obstacles, particles, score, bg_x, current_speed, nitro_fuel

# --- MAIN ---
def main():
    player_rect, obstacles, particles, score, bg_x, current_speed, nitro_fuel = reset_game()
    high_score = get_high_score()
    
    velocity_y = 0
    last_spawn_time = pygame.time.get_ticks()
    
    game_active = False 
    game_paused = False
    player_dead = False
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        
        is_nitro = False 

        # 1. EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p and game_active:
                game_paused = not game_paused

            if game_active and not game_paused and not player_dead:
                if event.type == SPEED_UP_EVENT:
                    if current_speed < MAX_SPEED:
                        current_speed += SPEED_INCREMENT

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w: velocity_y = -PLAYER_SPEED
                    if event.key == pygame.K_s: velocity_y = PLAYER_SPEED
                
                if event.type == pygame.KEYUP:
                    if event.key in [pygame.K_w, pygame.K_s]: velocity_y = 0
            
            if (not game_active or player_dead) and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player_rect, obstacles, particles, score, bg_x, current_speed, nitro_fuel = reset_game()
                high_score = get_high_score()
                game_active = True
                player_dead = False
                game_paused = False
                velocity_y = 0

        # --- LOGIC ---
        if game_active and not game_paused:
            
            wants_nitro = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            
            if wants_nitro and nitro_fuel > 0:
                is_nitro = True
                nitro_fuel -= NITRO_DRAIN_RATE
            else:
                if nitro_fuel < MAX_NITRO_FUEL:
                    nitro_fuel += NITRO_RECHARGE_RATE
            
            actual_speed = current_speed * (NITRO_MULTIPLIER if is_nitro else 1.0)
            
            if player_dead:
                for p in particles: p.update()
                if all(p.life <= 0 for p in particles): 
                    game_active = False 

            else:
                bg_x -= actual_speed
                if bg_x <= -WIDTH: bg_x = 0
                
                shake_y = random.randint(-2, 2) if is_nitro else 0
                player_rect.y += velocity_y + shake_y
                
                if player_rect.top < ROAD_TOP: player_rect.top = ROAD_TOP
                if player_rect.bottom > ROAD_BOTTOM: player_rect.bottom = ROAD_BOTTOM
                
                # --- SPAWN LOGIC ---
                spawn_speed_modifier = 20 if is_nitro else 20
                current_spawn_rate = 1500 - (current_speed * spawn_speed_modifier) 
                if current_spawn_rate < 300: current_spawn_rate = 300

                if current_time - last_spawn_time > current_spawn_rate:
                    spawn_y = random.randint(ROAD_TOP, ROAD_BOTTOM - 60)
                    
                    # 1. Pick a random image
                    chosen_img = random.choice(obstacle_images)
                    
                    # 2. Create rect based on that image's size
                    new_rect = chosen_img.get_rect(midleft=(WIDTH + 50, spawn_y))
                    
                    # 3. Store BOTH in a dictionary
                    obstacle_data = {'rect': new_rect, 'img': chosen_img}
                    obstacles.append(obstacle_data)
                    
                    last_spawn_time = current_time

                # --- MOVE OBSTACLES ---
                for item in obstacles[:]:
                    rect = item['rect']
                    rect.x -= actual_speed
                    
                    if player_rect.colliderect(rect):
                        save_high_score(score)
                        high_score = get_high_score()
                        player_dead = True
                        for _ in range(30):
                            p = Particle(player_rect.centerx, player_rect.centery, (200, 50, 50))
                            particles.append(p)
                            p2 = Particle(player_rect.centerx, player_rect.centery, (100, 100, 100))
                            particles.append(p2)
                    
                    if rect.right < 0:
                        obstacles.remove(item)
                        score += 2 if is_nitro else 1 

        else:
            actual_speed = 0

        # --- DRAWING ---
        screen.blit(bg_image, (bg_x, 0))
        screen.blit(bg_image, (bg_x + WIDTH, 0))
        
        if not player_dead:
            screen.blit(bike_image, player_rect)
            if is_nitro:
                pygame.draw.circle(screen, (0, 255, 255), (player_rect.left, player_rect.centery + 5), random.randint(5, 15))

        for p in particles:
            p.draw(screen)
            
        # --- DRAW OBSTACLES ---
        for item in obstacles:
            screen.blit(item['img'], item['rect'])

        if game_active and not player_dead:
            score_surf = font_score.render(f"SCORE: {score}", True, (255, 255, 255))
            screen.blit(score_surf, (20, 20))
            
            display_speed = int(actual_speed * 12) 
            if display_speed > 0: display_speed += 20 
                
            speed_color = (0, 255, 255) if not is_nitro else (255, 50, 50) 
            speed_surf = font_score.render(f"{display_speed} KM/H", True, speed_color)
            screen.blit(speed_surf, (20, 60))

            pygame.draw.rect(screen, (50, 50, 50), (20, 110, 200, 20))
            current_bar_width = int((nitro_fuel / MAX_NITRO_FUEL) * 200)
            bar_color = (0, 255, 0)
            if nitro_fuel < 30: bar_color = (255, 0, 0)
            pygame.draw.rect(screen, bar_color, (20, 110, current_bar_width, 20))
            pygame.draw.rect(screen, (255, 255, 255), (20, 110, 200, 20), 2)
            
            nitro_text = font_ui.render("NITRO", True, (255, 255, 255))
            screen.blit(nitro_text, (230, 110))

            if game_paused:
                 draw_text(screen, "PAUSED", font_gameover, (255, 255, 0), WIDTH//2, HEIGHT//2)

        if not game_active and not player_dead:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0,0,0))
            screen.blit(overlay, (0,0))
            
            draw_text(screen, "NEON RIDER", font_title, (0, 255, 255), WIDTH//2, HEIGHT//2 - 80)
            draw_text(screen, "Use W / S to Move", font_ui, (200, 200, 200), WIDTH//2, HEIGHT//2 + 20)
            draw_text(screen, "Hold SHIFT for Nitro", font_ui, (200, 200, 200), WIDTH//2, HEIGHT//2 + 50)
            draw_text(screen, "PRESS SPACE TO START", font_score, (255, 255, 255), WIDTH//2, HEIGHT//2 + 100)
            draw_text(screen, f"HIGH SCORE: {high_score}", font_score, (255, 215, 0), WIDTH//2, HEIGHT//2 + 150)

        if player_dead and all(p.life <= 0 for p in particles):
             overlay = pygame.Surface((WIDTH, HEIGHT))
             overlay.set_alpha(150)
             overlay.fill((50,0,0)) 
             screen.blit(overlay, (0,0))
             
             draw_text(screen, "CRASHED", font_gameover, (255, 0, 0), WIDTH//2, HEIGHT//2 - 60)
             draw_text(screen, f"Score: {score}", font_score, (255, 255, 255), WIDTH//2, HEIGHT//2 + 20)
             draw_text(screen, f"HIGH SCORE: {high_score}", font_score, (255, 215, 0), WIDTH//2, HEIGHT//2 + 60)
             draw_text(screen, "SPACE to Restart", font_score, (255, 255, 255), WIDTH//2, HEIGHT//2 + 120)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()