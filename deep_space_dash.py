"""
Deep Space Dash - An endless spaceship survival game
Navigate through space, avoid asteroids, and see how far you can travel!
"""

import pygame
import random
import sys
import math
import json
import os
from typing import List, Tuple
from datetime import datetime

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Leaderboard file
LEADERBOARD_FILE = "deep_space_dash_scores.json"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (100, 150, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 100)
GRAY = (100, 100, 100)
ORANGE = (255, 165, 0)
BROWN = (139, 90, 43)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)
EARTH_BLUE = (70, 130, 180)
EARTH_GREEN = (34, 139, 34)
PURPLE = (148, 0, 211)
CYAN = (0, 255, 255)

# Ship color options
SHIP_COLORS = {
    'red': (255, 50, 50),
    'green': (50, 255, 50),
    'blue': (100, 150, 255),
    'yellow': (255, 255, 50)
}

# Game scaling - increased for faster progression
KM_PER_PIXEL = 50_000  # Tripled from 16,093 to travel much faster
KM_PER_LIGHT_YEAR = 9_460_730_472_580.8

# Lives system
EXTRA_LIFE_DISTANCE = 1_000_000_000  # Get extra life every 1 billion km
MAX_EXTRA_LIVES = 3

# Speed mechanics
INITIAL_OBSTACLE_SPEED = 3
BASE_SPEED = 3
MAX_OBSTACLE_SPEED = 15  # Increased from 10
SPEED_INCREASE_RATE = 0.001  # Doubled speed increase rate
BOOST_SPEED = 20  # Increased from 8 - much faster boost!
MAX_BOOST_SPEED = 35  # Increased from 15 - super fast max speed!

# Difficulty progression
INITIAL_SPAWN_DELAY = 90
MIN_SPAWN_DELAY = 20
SPAWN_DECREASE_RATE = 0.01

# Special objects spawn rates
BLACK_HOLE_SPAWN_CHANCE = 0.003
PORTAL_SPAWN_CHANCE = 0.002

# Planet milestones
PLANET_MILESTONES = [
    ("Moon", 384_400, 30, [(LIGHT_GRAY, 1.0), (DARK_GRAY, 0.8)]),
    ("Mars", 225_300_000, 50, [(RED, 1.0), ((200, 100, 80), 0.9)]),
    ("Jupiter", 778_500_000, 100, [(BROWN, 1.0), ((210, 180, 140), 0.95), (WHITE, 0.9)]),
    ("Saturn", 1_433_000_000, 90, [(ORANGE, 1.0), ((230, 200, 150), 0.95)]),
    ("Uranus", 2_871_000_000, 70, [((150, 200, 230), 1.0), ((100, 150, 200), 0.95)]),
    ("Neptune", 4_495_000_000, 70, [(BLUE, 1.0), ((80, 120, 200), 0.95)]),
]

# Random name generators
PLANET_PREFIXES = ["Zeta", "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Sigma", 
                   "Omega", "Nova", "Stellar", "Cosmic", "Nebula", "Quantum", "Hyper"]
PLANET_SUFFIXES = ["Prime", "Major", "Minor", "Centauri", "Proxima", "Ultima", 
                   "Secundus", "Tertius", "Rex", "Magna", "Nova"]

GALAXY_PREFIXES = ["Andromeda", "Triangulum", "Whirlpool", "Sombrero", "Pinwheel",
                   "Cartwheel", "Sunflower", "Tadpole", "Sculptor", "Phoenix"]
GALAXY_SUFFIXES = ["Cluster", "Nebula", "Expanse", "Sector", "Quadrant", "Region",
                   "Domain", "Realm", "Territory", "Zone"]

# Game states
MENU = 0
COLOR_SELECT = 1
LAUNCH_ANIMATION = 2
RUNNING = 3
GAME_OVER = 4
PAUSED = 5
LEADERBOARD = 6


class Leaderboard:
    """Manages the leaderboard system"""
    
    def __init__(self):
        self.scores = []
        self.load_scores()
        
    def load_scores(self):
        """Load scores from file"""
        try:
            if os.path.exists(LEADERBOARD_FILE):
                with open(LEADERBOARD_FILE, 'r') as f:
                    self.scores = json.load(f)
        except:
            self.scores = []
            
    def save_scores(self):
        """Save scores to file"""
        try:
            with open(LEADERBOARD_FILE, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except:
            pass
            
    def add_score(self, score: int, distance_km: float, ship_color: str):
        """Add a new score to the leaderboard"""
        entry = {
            'score': score,
            'distance_km': distance_km,
            'distance_ly': distance_km / KM_PER_LIGHT_YEAR,
            'ship_color': ship_color,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.scores.append(entry)
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:10]
        self.save_scores()
        
    def get_rank(self, score: int) -> int:
        """Get the rank of a score"""
        for i, entry in enumerate(self.scores):
            if entry['score'] == score:
                return i + 1
        return 0
        
    def get_top_scores(self, n: int = 10) -> List[dict]:
        """Get top n scores"""
        return self.scores[:n]


class Spaceship:
    """Player's spaceship"""
    
    def __init__(self, x: int, y: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.speed = 5
        self.color = color
        self.invulnerable = False
        self.invulnerable_timer = 0
        
    def set_invulnerable(self, frames: int = 120):
        """Make ship invulnerable"""
        self.invulnerable = True
        self.invulnerable_timer = frames
        
    def update(self):
        """Update invulnerability"""
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
        
    def move(self, dy: int):
        """Move ship up or down"""
        self.y += dy * self.speed
        self.y = max(10, min(SCREEN_HEIGHT - self.height - 10, self.y))
        
    def draw(self, screen: pygame.Surface):
        """Draw the spaceship"""
        if self.invulnerable and self.invulnerable_timer % 10 < 5:
            return
            
        points = [
            (self.x + self.width, self.y + self.height // 2),
            (self.x, self.y),
            (self.x, self.y + self.height)
        ]
        pygame.draw.polygon(screen, self.color, points)
        
        pygame.draw.circle(screen, ORANGE, (self.x + 5, self.y + self.height // 2), 8)
        pygame.draw.circle(screen, YELLOW, (self.x + 5, self.y + self.height // 2), 5)
        
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Obstacle:
    """Asteroid obstacle"""
    
    def __init__(self, x: int, y: int, speed: float):
        self.x = x
        self.y = y
        self.radius = random.randint(15, 35)
        self.speed = speed
        self.color = GRAY
        self.color_variation = random.randint(-20, 20)
        
    def update(self, speed_multiplier: float = 1.0):
        """Move obstacle left"""
        self.x -= self.speed * speed_multiplier
        
    def draw(self, screen: pygame.Surface):
        """Draw the obstacle"""
        color = tuple(max(0, min(255, c + self.color_variation)) for c in self.color)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (80, 80, 80), 
                         (int(self.x - self.radius//3), int(self.y - self.radius//4)), 
                         self.radius//4)
        
    def is_off_screen(self) -> bool:
        """Check if off screen"""
        return self.x + self.radius < 0
        
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle"""
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)


class BlackHole:
    """Black hole obstacle"""
    
    def __init__(self, x: int, y: int, speed: float):
        self.x = x
        self.y = y
        self.radius = 40
        self.speed = speed
        self.rotation = 0
        
    def update(self, speed_multiplier: float = 1.0):
        """Move and rotate"""
        self.x -= self.speed * speed_multiplier
        self.rotation += 5
        
    def draw(self, screen: pygame.Surface):
        """Draw the black hole"""
        pygame.draw.circle(screen, (50, 0, 50), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, PURPLE, (int(self.x), int(self.y)), self.radius, 3)
        
        for i in range(3):
            angle = self.rotation + i * 120
            rad_angle = math.radians(angle)
            end_x = int(self.x + math.cos(rad_angle) * self.radius * 0.8)
            end_y = int(self.y + math.sin(rad_angle) * self.radius * 0.8)
            pygame.draw.line(screen, ORANGE, (int(self.x), int(self.y)), 
                           (end_x, end_y), 2)
        
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), int(self.radius * 0.6))
        pygame.draw.circle(screen, (100, 0, 100), (int(self.x), int(self.y)), 
                         int(self.radius * 0.6), 2)
        
    def is_off_screen(self) -> bool:
        return self.x + self.radius < 0
        
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)


class Portal:
    """Teleportation portal"""
    
    def __init__(self, x: int, y: int, speed: float):
        self.x = x
        self.y = y
        self.radius = 35
        self.speed = speed
        self.pulse = 0
        
    def update(self, speed_multiplier: float = 1.0):
        """Move and pulse"""
        self.x -= self.speed * speed_multiplier
        self.pulse = (self.pulse + 2) % 360
        
    def draw(self, screen: pygame.Surface):
        """Draw the portal"""
        pulse_radius = self.radius + int(math.sin(math.radians(self.pulse)) * 5)
        
        pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), pulse_radius, 3)
        pygame.draw.circle(screen, (0, 200, 200), (int(self.x), int(self.y)), pulse_radius - 5, 2)
        
        for i in range(4):
            angle = self.pulse + i * 90
            rad_angle = math.radians(angle)
            start_x = int(self.x + math.cos(rad_angle) * pulse_radius * 0.3)
            start_y = int(self.y + math.sin(rad_angle) * pulse_radius * 0.3)
            end_x = int(self.x + math.cos(rad_angle) * pulse_radius * 0.7)
            end_y = int(self.y + math.sin(rad_angle) * pulse_radius * 0.7)
            pygame.draw.line(screen, WHITE, (start_x, start_y), (end_x, end_y), 2)
        
        pygame.draw.circle(screen, (100, 255, 255), (int(self.x), int(self.y)), 10)
        
    def is_off_screen(self) -> bool:
        return self.x + self.radius < 0
        
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)


class Planet:
    """Visual planet representation"""
    
    def __init__(self, name: str, x: int, y: int, radius: int, colors: List):
        self.name = name
        self.x = x
        self.y = y
        self.radius = radius
        self.colors = colors
        
    def update(self, speed_multiplier: float = 1.0, base_speed: float = 3):
        self.x -= base_speed * speed_multiplier
        
    def is_off_screen(self) -> bool:
        return self.x + self.radius < -100
        
    def draw(self, screen: pygame.Surface):
        """Draw planet"""
        if self.name == "Moon":
            pygame.draw.circle(screen, LIGHT_GRAY, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, DARK_GRAY, (int(self.x - 8), int(self.y - 5)), 6)
            pygame.draw.circle(screen, DARK_GRAY, (int(self.x + 10), int(self.y + 8)), 8)
            
        elif self.name == "Mars":
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, (180, 80, 60), (int(self.x - 10), int(self.y - 10)), 12)
            
        elif self.name == "Jupiter":
            pygame.draw.circle(screen, (210, 180, 140), (int(self.x), int(self.y)), self.radius)
            for i in range(-3, 4):
                stripe_y = int(self.y + i * self.radius // 4)
                stripe_width = int(math.sqrt(max(0, self.radius**2 - (i * self.radius // 4)**2)) * 2)
                if i % 2 == 0:
                    pygame.draw.ellipse(screen, BROWN, 
                                      (int(self.x - stripe_width//2), stripe_y - 3, 
                                       stripe_width, 6))
                else:
                    pygame.draw.ellipse(screen, WHITE, 
                                      (int(self.x - stripe_width//2), stripe_y - 2, 
                                       stripe_width, 4))
            
        elif self.name == "Saturn":
            ring_color = (200, 180, 150)
            pygame.draw.ellipse(screen, ring_color,
                              (int(self.x - self.radius * 1.8), int(self.y - self.radius * 0.3),
                               int(self.radius * 3.6), int(self.radius * 0.6)), 8)
            pygame.draw.circle(screen, (230, 200, 150), (int(self.x), int(self.y)), self.radius)
            pygame.draw.ellipse(screen, ring_color,
                              (int(self.x - self.radius * 1.8), int(self.y),
                               int(self.radius * 3.6), int(self.radius * 0.3)), 8)
            
        elif self.name == "Uranus":
            pygame.draw.circle(screen, (150, 200, 230), (int(self.x), int(self.y)), self.radius)
            
        elif self.name == "Neptune":
            pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.radius)


class HUD:
    """Heads-up display"""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.milestone_timer = 0
        self.milestone_text = ""
        
    def draw_text_with_shadow(self, screen, text, x, y, font, color):
        shadow = font.render(text, True, BLACK)
        screen.blit(shadow, (x + 2, y + 2))
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))
        
    def draw_game_hud(self, screen, distance, speed, score, next_planet, 
                     distance_to_planet, extra_lives):
        # Distance with light years
        distance_ly = distance / KM_PER_LIGHT_YEAR
        if distance_ly < 0.001:
            distance_text = f"Distance: {distance:,} km"
        else:
            distance_text = f"Distance: {distance:,} km ({distance_ly:.6f} LY)"
        self.draw_text_with_shadow(screen, distance_text, 20, 20, self.font, WHITE)
        
        # Speed
        speed_text = f"Speed: {speed:.1f} km/s"
        self.draw_text_with_shadow(screen, speed_text, 20, 55, self.small_font, GREEN)
        
        # Lives
        lives_text = f"Lives: {extra_lives}/{MAX_EXTRA_LIVES}"
        self.draw_text_with_shadow(screen, lives_text, 20, 80, self.small_font, RED)
        
        # Next planet
        planet_info = f"Next: {next_planet}"
        self.draw_text_with_shadow(screen, planet_info, 20, 105, self.small_font, YELLOW)
        
        if distance_to_planet > 0:
            distance_info = f"{distance_to_planet:,} km away"
            self.draw_text_with_shadow(screen, distance_info, 20, 130, self.small_font, WHITE)
        
        # Score
        score_text = f"Score: {score}"
        score_surface = self.font.render(score_text, True, WHITE)
        score_x = SCREEN_WIDTH - score_surface.get_width() - 20
        self.draw_text_with_shadow(screen, score_text, score_x, 20, self.font, WHITE)
        
    def show_milestone(self, name: str, distance: int, is_galaxy: bool = False):
        if is_galaxy:
            self.milestone_text = f"Entering {name}!"
        else:
            self.milestone_text = f"You passed {name}! ({distance:,} km)"
        self.milestone_timer = 180
        
    def draw_milestone_toast(self, screen):
        if self.milestone_timer > 0:
            toast_surface = self.font.render(self.milestone_text, True, YELLOW)
            toast_rect = toast_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
            
            padding = 20
            box_rect = toast_rect.inflate(padding * 2, padding * 2)
            pygame.draw.rect(screen, (0, 0, 50), box_rect)
            pygame.draw.rect(screen, YELLOW, box_rect, 3)
            
            screen.blit(toast_surface, toast_rect)
            self.milestone_timer -= 1


class Game:
    """Main game manager"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Deep Space Dash")
        self.clock = pygame.time.Clock()
        self.state = MENU
        
        self.leaderboard = Leaderboard()
        self.selected_color = 'blue'
        
        self.ship = None
        self.obstacles = []
        self.black_holes = []
        self.portals = []
        self.planets = []
        self.hud = HUD()
        
        self.launch_timer = 0
        self.launch_duration = 180
        self.earth_y = SCREEN_HEIGHT // 2
        self.earth_size = 150
        
        self.distance = 0
        self.pixels_traveled = 0
        self.current_speed = BASE_SPEED
        self.score = 0
        self.obstacle_speed = INITIAL_OBSTACLE_SPEED
        self.spawn_delay = INITIAL_SPAWN_DELAY
        self.spawn_timer = 0
        self.frame_count = 0
        self.is_boosting = False
        
        self.extra_lives = 0
        self.last_life_distance = 0
        
        self.milestone_index = 0
        self.last_planet_passed = "Earth"
        self.passed_neptune = False
        self.procedural_milestones = []
        self.next_procedural_distance = 5_000_000_000
        self.planet_shown = [False] * len(PLANET_MILESTONES)
        
        self.stars = [(random.randint(0, SCREEN_WIDTH), 
                      random.randint(0, SCREEN_HEIGHT),
                      random.randint(1, 3)) for _ in range(100)]
        
    def generate_procedural_milestone(self):
        if random.random() < 0.7:
            name = f"{random.choice(PLANET_PREFIXES)}-{random.choice(PLANET_SUFFIXES)}"
            is_galaxy = False
        else:
            name = f"{random.choice(GALAXY_PREFIXES)} {random.choice(GALAXY_SUFFIXES)}"
            is_galaxy = True
        
        milestone = (name, self.next_procedural_distance, is_galaxy)
        self.procedural_milestones.append(milestone)
        self.next_procedural_distance += random.randint(300_000_000, 800_000_000)
        
    def calculate_difficulty_multiplier(self):
        distance_segments = self.distance // 500_000_000
        multiplier = 1.0 + (distance_segments * 0.15)
        return min(multiplier, 3.0)
        
    def reset_game(self):
        self.ship = Spaceship(100, SCREEN_HEIGHT // 2, SHIP_COLORS[self.selected_color])
        self.obstacles = []
        self.black_holes = []
        self.portals = []
        self.planets = []
        self.distance = 0
        self.pixels_traveled = 0
        self.current_speed = BASE_SPEED
        self.score = 0
        self.obstacle_speed = INITIAL_OBSTACLE_SPEED
        self.spawn_delay = INITIAL_SPAWN_DELAY
        self.spawn_timer = 0
        self.frame_count = 0
        self.milestone_index = 0
        self.last_planet_passed = "Earth"
        self.passed_neptune = False
        self.procedural_milestones = []
        self.next_procedural_distance = 5_000_000_000
        self.hud.milestone_timer = 0
        self.is_boosting = False
        self.planet_shown = [False] * len(PLANET_MILESTONES)
        self.launch_timer = 0
        self.earth_y = SCREEN_HEIGHT // 2
        self.extra_lives = 0
        self.last_life_distance = 0
        
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if self.state == MENU:
            if keys[pygame.K_SPACE]:
                self.state = COLOR_SELECT
            elif keys[pygame.K_l]:
                self.state = LEADERBOARD
                
        elif self.state == LEADERBOARD:
            if keys[pygame.K_ESCAPE] or keys[pygame.K_SPACE]:
                self.state = MENU
                
        elif self.state == COLOR_SELECT:
            if keys[pygame.K_1]:
                self.selected_color = 'red'
                self.reset_game()
                self.state = LAUNCH_ANIMATION
            elif keys[pygame.K_2]:
                self.selected_color = 'green'
                self.reset_game()
                self.state = LAUNCH_ANIMATION
            elif keys[pygame.K_3]:
                self.selected_color = 'blue'
                self.reset_game()
                self.state = LAUNCH_ANIMATION
            elif keys[pygame.K_4]:
                self.selected_color = 'yellow'
                self.reset_game()
                self.state = LAUNCH_ANIMATION
                
        elif self.state == RUNNING:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.ship.move(-1)
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.ship.move(1)
                
            self.is_boosting = keys[pygame.K_RIGHT]
                
            if keys[pygame.K_p]:
                self.state = PAUSED
                
        elif self.state == PAUSED:
            if keys[pygame.K_p]:
                self.state = RUNNING
                
        elif self.state == GAME_OVER:
            if keys[pygame.K_r]:
                self.state = COLOR_SELECT
            elif keys[pygame.K_l]:
                self.state = LEADERBOARD
                
    def update_launch_animation(self):
        if self.state != LAUNCH_ANIMATION:
            return
            
        self.launch_timer += 1
        
        progress = self.launch_timer / self.launch_duration
        self.earth_y = SCREEN_HEIGHT // 2 + (progress * SCREEN_HEIGHT * 0.8)
        self.earth_size = int(150 * (1 - progress * 0.7))
        
        if self.launch_timer >= self.launch_duration:
            self.state = RUNNING
            
    def teleport_player(self):
        teleport_options = [
            100, 1_000, 10_000, 100_000, 1_000_000,
            10_000_000, 100_000_000, 1_000_000_000
        ]
        teleport_km = random.choice(teleport_options)
        
        teleport_pixels = teleport_km / KM_PER_PIXEL
        self.pixels_traveled += teleport_pixels
        self.distance = int(self.pixels_traveled * KM_PER_PIXEL)
        
        if teleport_km >= 1_000_000:
            distance_ly = teleport_km / KM_PER_LIGHT_YEAR
            self.hud.milestone_text = f"Portal Jump! +{teleport_km:,} km ({distance_ly:.6f} LY)"
        else:
            self.hud.milestone_text = f"Portal Jump! +{teleport_km:,} km"
        self.hud.milestone_timer = 120
            
    def update_game(self):
        if self.state != RUNNING:
            return
            
        self.frame_count += 1
        self.ship.update()
        
        if self.is_boosting:
            self.current_speed = min(MAX_BOOST_SPEED, self.obstacle_speed + BOOST_SPEED)
        else:
            self.current_speed = self.obstacle_speed
        
        self.pixels_traveled += self.current_speed
        self.distance = int(self.pixels_traveled * KM_PER_PIXEL)
        
        # Extra life system
        if self.distance >= self.last_life_distance + EXTRA_LIFE_DISTANCE:
            if self.extra_lives < MAX_EXTRA_LIVES:
                self.extra_lives += 1
                self.last_life_distance = self.distance
                self.hud.milestone_text = f"Extra Life! ({self.extra_lives}/{MAX_EXTRA_LIVES})"
                self.hud.milestone_timer = 120
        
        if self.frame_count % 60 == 0:
            self.score += 1
        
        self.obstacle_speed = min(MAX_OBSTACLE_SPEED, 
                                 self.obstacle_speed + SPEED_INCREASE_RATE)
        
        difficulty_multiplier = self.calculate_difficulty_multiplier()
        adjusted_spawn_delay = INITIAL_SPAWN_DELAY / difficulty_multiplier
        self.spawn_delay = max(MIN_SPAWN_DELAY, adjusted_spawn_delay - (self.frame_count * SPAWN_DECREASE_RATE))
        
        # Spawn objects
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            y = random.randint(50, SCREEN_HEIGHT - 50)
            self.obstacles.append(Obstacle(SCREEN_WIDTH, y, self.obstacle_speed))
            self.spawn_timer = 0
        
        if random.random() < BLACK_HOLE_SPAWN_CHANCE:
            y = random.randint(80, SCREEN_HEIGHT - 80)
            self.black_holes.append(BlackHole(SCREEN_WIDTH, y, self.obstacle_speed))
        
        if random.random() < PORTAL_SPAWN_CHANCE:
            y = random.randint(70, SCREEN_HEIGHT - 70)
            self.portals.append(Portal(SCREEN_WIDTH, y, self.obstacle_speed))
        
        speed_multiplier = self.current_speed / self.obstacle_speed
        
        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update(speed_multiplier)
            
            if obstacle.is_off_screen():
                self.obstacles.remove(obstacle)
                self.score += 1
                
            if not self.ship.invulnerable and self.ship.get_rect().colliderect(obstacle.get_rect()):
                self.handle_collision()
        
        # Update black holes
        for black_hole in self.black_holes[:]:
            black_hole.update(speed_multiplier)
            
            if black_hole.is_off_screen():
                self.black_holes.remove(black_hole)
                self.score += 5
                
            if not self.ship.invulnerable and self.ship.get_rect().colliderect(black_hole.get_rect()):
                self.handle_collision()
        
        # Update portals
        for portal in self.portals[:]:
            portal.update(speed_multiplier)
            
            if portal.is_off_screen():
                self.portals.remove(portal)
                
            if self.ship.get_rect().colliderect(portal.get_rect()):
                self.teleport_player()
                self.portals.remove(portal)
                self.score += 10
                
        # Update planets
        for planet in self.planets[:]:
            planet.update(speed_multiplier, self.current_speed)
            if planet.is_off_screen():
                self.planets.remove(planet)
                
        # Milestones
        if self.milestone_index < len(PLANET_MILESTONES):
            planet_name, planet_distance, planet_radius, planet_colors = PLANET_MILESTONES[self.milestone_index]
            
            approach_distance = int(planet_distance * 0.9)
            if self.distance >= approach_distance and not self.planet_shown[self.milestone_index]:
                planet_y = random.randint(planet_radius + 50, SCREEN_HEIGHT - planet_radius - 50)
                self.planets.append(Planet(planet_name, SCREEN_WIDTH + planet_radius, planet_y, 
                                          planet_radius, planet_colors))
                self.planet_shown[self.milestone_index] = True
            
            if self.distance >= planet_distance:
                self.hud.show_milestone(planet_name, planet_distance)
                self.last_planet_passed = planet_name
                self.milestone_index += 1
                
                if planet_name == "Neptune":
                    self.passed_neptune = True
                    self.hud.milestone_text = "Leaving our solar system!"
                    self.hud.milestone_timer = 240
                    self.generate_procedural_milestone()
        
        elif self.passed_neptune:
            if not self.procedural_milestones or self.distance >= self.procedural_milestones[-1][1]:
                self.generate_procedural_milestone()
            
            for i, (name, distance, is_galaxy) in enumerate(self.procedural_milestones):
                if self.distance >= distance and distance > 0:
                    self.hud.show_milestone(name, distance, is_galaxy)
                    self.last_planet_passed = name
                    self.procedural_milestones[i] = (name, -1, is_galaxy)
    
    def handle_collision(self):
        if self.extra_lives > 0:
            self.extra_lives -= 1
            self.ship.set_invulnerable(120)
            self.hud.milestone_text = f"Life Lost! {self.extra_lives} left"
            self.hud.milestone_timer = 120
        else:
            self.state = GAME_OVER
            self.leaderboard.add_score(self.score, self.distance, self.selected_color)
                    
    def get_next_planet_info(self):
        if self.milestone_index < len(PLANET_MILESTONES):
            planet_name = PLANET_MILESTONES[self.milestone_index][0]
            planet_distance = PLANET_MILESTONES[self.milestone_index][1]
            distance_to_planet = planet_distance - self.distance
            return planet_name, distance_to_planet
        
        elif self.procedural_milestones:
            for name, distance, is_galaxy in self.procedural_milestones:
                if distance > 0 and self.distance < distance:
                    distance_to_planet = distance - self.distance
                    return name, distance_to_planet
        
        return "Deep Space", 0
            
    def draw_stars(self):
        for i, (x, y, size) in enumerate(self.stars):
            if self.state == RUNNING:
                move_speed = self.current_speed * 0.3
            elif self.state == LAUNCH_ANIMATION:
                move_speed = 2.0
            else:
                move_speed = BASE_SPEED * 0.3
                
            new_x = x - move_speed
            if new_x < 0:
                new_x = SCREEN_WIDTH
                y = random.randint(0, SCREEN_HEIGHT)
            self.stars[i] = (new_x, y, size)
            pygame.draw.circle(self.screen, WHITE, (int(new_x), int(y)), size)
            
    def draw_earth(self, x, y, size):
        pygame.draw.circle(self.screen, EARTH_BLUE, (int(x), int(y)), size)
        pygame.draw.circle(self.screen, EARTH_GREEN, (int(x - size * 0.3), int(y - size * 0.2)), int(size * 0.3))
        pygame.draw.circle(self.screen, EARTH_GREEN, (int(x + size * 0.2), int(y - size * 0.1)), int(size * 0.25))
        pygame.draw.circle(self.screen, WHITE, (int(x + size * 0.4), int(y + size * 0.3)), int(size * 0.15))
        
    def draw_menu(self):
        self.screen.fill(BLACK)
        self.draw_stars()
        
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("DEEP SPACE DASH", True, BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        font = pygame.font.Font(None, 32)
        instructions = [
            "Controls: W/S or UP/DOWN to move",
            "RIGHT ARROW to boost",
            "Avoid asteroids and black holes!",
            "Collect portals to teleport forward!",
            "Get extra lives every 1 billion km",
            "",
            "Press SPACE to Start",
            "Press L for Leaderboard"
        ]
        
        y = 250
        for line in instructions:
            text = font.render(line, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 38
    
    def draw_leaderboard(self):
        self.screen.fill(BLACK)
        self.draw_stars()
        
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("LEADERBOARD", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)
        
        font = pygame.font.Font(None, 28)
        y = 130
        
        scores = self.leaderboard.get_top_scores()
        if not scores:
            no_scores = font.render("No scores yet!", True, WHITE)
            no_scores_rect = no_scores.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(no_scores, no_scores_rect)
        else:
            for i, entry in enumerate(scores):
                rank_color = YELLOW if i < 3 else WHITE
                
                rank_text = f"#{i+1}"
                rank_surface = font.render(rank_text, True, rank_color)
                self.screen.blit(rank_surface, (50, y))
                
                score_text = f"{entry['score']:,}"
                score_surface = font.render(score_text, True, WHITE)
                self.screen.blit(score_surface, (120, y))
                
                distance_ly = entry['distance_ly']
                if distance_ly < 0.001:
                    distance_text = f"{int(entry['distance_km']):,} km"
                else:
                    distance_text = f"{distance_ly:.4f} LY"
                distance_surface = font.render(distance_text, True, CYAN)
                self.screen.blit(distance_surface, (280, y))
                
                ship_color = SHIP_COLORS.get(entry['ship_color'], WHITE)
                pygame.draw.circle(self.screen, ship_color, (550, y + 10), 8)
                
                date_surface = font.render(entry['date'], True, GRAY)
                self.screen.blit(date_surface, (580, y))
                
                y += 40
        
        back_font = pygame.font.Font(None, 32)
        back_text = back_font.render("Press SPACE or ESC to return", True, WHITE)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        self.screen.blit(back_text, back_rect)
            
    def draw_color_select(self):
        self.screen.fill(BLACK)
        self.draw_stars()
        
        title_font = pygame.font.Font(None, 56)
        title = title_font.render("Choose Your Spaceship Color", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        font = pygame.font.Font(None, 40)
        y = 250
        spacing = 80
        
        colors = [
            ('1', 'RED', SHIP_COLORS['red']),
            ('2', 'GREEN', SHIP_COLORS['green']),
            ('3', 'BLUE', SHIP_COLORS['blue']),
            ('4', 'YELLOW', SHIP_COLORS['yellow'])
        ]
        
        for key, name, color in colors:
            text = font.render(f"Press {key} - {name}", True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            
            preview_x = SCREEN_WIDTH // 2 - 150
            preview_y = y
            points = [
                (preview_x + 30, preview_y),
                (preview_x, preview_y - 10),
                (preview_x, preview_y + 10)
            ]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.circle(self.screen, ORANGE, (preview_x + 5, preview_y), 6)
            
            y += spacing
            
    def draw_launch_animation(self):
        self.screen.fill(BLACK)
        self.draw_stars()
        
        self.draw_earth(SCREEN_WIDTH // 2, int(self.earth_y), self.earth_size)
        
        ship_y = SCREEN_HEIGHT // 2 - (self.launch_timer * 1.5)
        self.ship.y = int(ship_y)
        self.ship.draw(self.screen)
        
        font = pygame.font.Font(None, 48)
        progress = self.launch_timer / self.launch_duration
        if progress < 0.3:
            text = font.render("Launching...", True, WHITE)
        elif progress < 0.6:
            text = font.render("Leaving Earth Orbit", True, YELLOW)
        else:
            text = font.render("Entering Deep Space!", True, GREEN)
        
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(text, text_rect)
        
    def draw_game(self):
        self.screen.fill(BLACK)
        self.draw_stars()
        
        for planet in self.planets:
            planet.draw(self.screen)
        
        for portal in self.portals:
            portal.draw(self.screen)
        
        self.ship.draw(self.screen)
        
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        for black_hole in self.black_holes:
            black_hole.draw(self.screen)
            
        if self.is_boosting:
            boost_font = pygame.font.Font(None, 48)
            boost_text = boost_font.render("BOOST!", True, ORANGE)
            boost_rect = boost_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
            self.screen.blit(boost_text, boost_rect)
            
        next_planet, distance_to_planet = self.get_next_planet_info()
        self.hud.draw_game_hud(self.screen, self.distance, self.current_speed,
                              self.score, next_planet, distance_to_planet, self.extra_lives)
        
        self.hud.draw_milestone_toast(self.screen)
        
    def draw_paused(self):
        self.draw_game()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        text = font.render("PAUSED", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)
        
        small_font = pygame.font.Font(None, 36)
        resume = small_font.render("Press P to Resume", True, WHITE)
        resume_rect = resume.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(resume, resume_rect)
        
    def draw_game_over(self):
        self.screen.fill(BLACK)
        self.draw_stars()
        
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("GAME OVER", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        rank = self.leaderboard.get_rank(self.score)
        if rank > 0:
            rank_font = pygame.font.Font(None, 48)
            rank_text = rank_font.render(f"Rank #{rank}!", True, YELLOW)
            rank_rect = rank_text.get_rect(center=(SCREEN_WIDTH // 2, 160))
            self.screen.blit(rank_text, rank_rect)
        
        font = pygame.font.Font(None, 36)
        distance_ly = self.distance / KM_PER_LIGHT_YEAR
        
        stats = [
            f"Score: {self.score}",
            f"Distance: {self.distance:,} km",
            f"Light Years: {distance_ly:.6f} LY",
            f"Max Speed: {self.current_speed:.1f} km/s",
            f"Last Location: {self.last_planet_passed}",
            "",
            "Press R to Play Again",
            "Press L for Leaderboard",
            "Press ESC to Quit"
        ]
        
        y = 220
        for line in stats:
            text = font.render(line, True, WHITE if line else BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 45
            
    def draw(self):
        if self.state == MENU:
            self.draw_menu()
        elif self.state == LEADERBOARD:
            self.draw_leaderboard()
        elif self.state == COLOR_SELECT:
            self.draw_color_select()
        elif self.state == LAUNCH_ANIMATION:
            self.draw_launch_animation()
        elif self.state == RUNNING:
            self.draw_game()
        elif self.state == PAUSED:
            self.draw_paused()
        elif self.state == GAME_OVER:
            self.draw_game_over()
            
        pygame.display.flip()
        
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == GAME_OVER or self.state == MENU:
                            running = False
                            
            self.handle_input()
            
            if self.state == LAUNCH_ANIMATION:
                self.update_launch_animation()
            else:
                self.update_game()
            
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()