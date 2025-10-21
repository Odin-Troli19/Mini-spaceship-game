"""
Deep Space Dash - An endless spaceship survival game
Navigate through space, avoid asteroids, and see how far you can travel!
"""

import pygame
import random
import sys
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (100, 150, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 100)
GRAY = (100, 100, 100)
ORANGE = (255, 165, 0)

# Ship color options
SHIP_COLORS = {
    'red': (255, 50, 50),
    'green': (50, 255, 50),
    'blue': (100, 150, 255),
    'yellow': (255, 255, 50)
}

# Game scaling - determines how fast distance accumulates
KM_PER_PIXEL = 16_093  # Approximately 10,000 miles converted to km

# Speed mechanics
INITIAL_OBSTACLE_SPEED = 3
BASE_SPEED = 3  # Base scrolling speed
MAX_OBSTACLE_SPEED = 10
SPEED_INCREASE_RATE = 0.0005  # Speed increase per frame
BOOST_SPEED = 8  # Additional speed when holding right arrow
MAX_BOOST_SPEED = 15  # Maximum speed with boost

# Difficulty progression
INITIAL_SPAWN_DELAY = 90  # Frames between spawns
MIN_SPAWN_DELAY = 30
SPAWN_DECREASE_RATE = 0.01  # Decrease spawn delay over time

# Planet milestones (in km from Earth)
PLANET_MILESTONES = [
    ("Moon", 384_400),
    ("Mars", 225_300_000),
    ("Jupiter", 778_500_000),
    ("Saturn", 1_433_000_000),
    ("Uranus", 2_871_000_000),
    ("Neptune", 4_495_000_000),
]

# Random name generators for procedural content
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
RUNNING = 2
GAME_OVER = 3
PAUSED = 4


class Spaceship:
    """Player's spaceship"""
    
    def __init__(self, x: int, y: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.speed = 5
        self.color = color
        
    def move(self, dy: int):
        """Move ship up or down, clamped to screen bounds"""
        self.y += dy * self.speed
        self.y = max(10, min(SCREEN_HEIGHT - self.height - 10, self.y))
        
    def draw(self, screen: pygame.Surface):
        """Draw the spaceship as a triangle"""
        # Main body (triangle pointing right)
        points = [
            (self.x + self.width, self.y + self.height // 2),  # Nose
            (self.x, self.y),  # Top back
            (self.x, self.y + self.height)  # Bottom back
        ]
        pygame.draw.polygon(screen, self.color, points)
        
        # Engine glow
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
        # Random variation for visual interest
        self.color_variation = random.randint(-20, 20)
        
    def update(self, speed_multiplier: float = 1.0):
        """Move obstacle left with optional speed multiplier"""
        self.x -= self.speed * speed_multiplier
        
    def draw(self, screen: pygame.Surface):
        """Draw the obstacle as a circle with some texture"""
        # Adjust color slightly
        color = tuple(max(0, min(255, c + self.color_variation)) for c in self.color)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        # Add some crater details
        pygame.draw.circle(screen, (80, 80, 80), 
                         (int(self.x - self.radius//3), int(self.y - self.radius//4)), 
                         self.radius//4)
        
    def is_off_screen(self) -> bool:
        """Check if obstacle has moved off the left side"""
        return self.x + self.radius < 0
        
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle"""
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)


class HUD:
    """Handles all on-screen display elements"""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.milestone_timer = 0  # Timer for milestone toast display
        self.milestone_text = ""
        
    def draw_text_with_shadow(self, screen: pygame.Surface, text: str, 
                             x: int, y: int, font: pygame.font.Font, color: Tuple[int, int, int]):
        """Draw text with a shadow for better visibility"""
        # Shadow
        shadow = font.render(text, True, BLACK)
        screen.blit(shadow, (x + 2, y + 2))
        # Main text
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))
        
    def draw_game_hud(self, screen: pygame.Surface, distance: int, speed: float,
                     score: int, next_planet: str, distance_to_planet: int):
        """Draw HUD during gameplay"""
        # Left side - Distance and Speed
        distance_text = f"Distance: {distance:,} km"
        self.draw_text_with_shadow(screen, distance_text, 20, 20, self.font, WHITE)
        
        # Speed display
        speed_text = f"Speed: {speed:.1f} km/s"
        self.draw_text_with_shadow(screen, speed_text, 20, 55, self.small_font, GREEN)
        
        # Distance from Earth and next planet
        planet_info = f"From Earth | Next: {next_planet}"
        self.draw_text_with_shadow(screen, planet_info, 20, 85, self.small_font, YELLOW)
        
        if distance_to_planet > 0:
            distance_info = f"{distance_to_planet:,} km to {next_planet}"
            self.draw_text_with_shadow(screen, distance_info, 20, 110, self.small_font, WHITE)
        
        # Right side - Score
        score_text = f"Score: {score}"
        score_surface = self.font.render(score_text, True, WHITE)
        score_x = SCREEN_WIDTH - score_surface.get_width() - 20
        self.draw_text_with_shadow(screen, score_text, score_x, 20, self.font, WHITE)
        
    def show_milestone(self, name: str, distance: int, is_galaxy: bool = False):
        """Trigger a milestone toast notification"""
        if is_galaxy:
            self.milestone_text = f"Entering {name}!"
        else:
            self.milestone_text = f"You passed {name}! ({distance:,} km)"
        self.milestone_timer = 180  # Show for 3 seconds at 60 FPS
        
    def draw_milestone_toast(self, screen: pygame.Surface):
        """Draw milestone notification if active"""
        if self.milestone_timer > 0:
            # Fade in/out effect
            alpha = min(255, self.milestone_timer * 4) if self.milestone_timer < 60 else 255
            
            # Create surface with text
            toast_surface = self.font.render(self.milestone_text, True, YELLOW)
            toast_rect = toast_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
            
            # Draw background box
            padding = 20
            box_rect = toast_rect.inflate(padding * 2, padding * 2)
            pygame.draw.rect(screen, (0, 0, 50), box_rect)
            pygame.draw.rect(screen, YELLOW, box_rect, 3)
            
            # Draw text
            screen.blit(toast_surface, toast_rect)
            
            self.milestone_timer -= 1


class Game:
    """Main game manager"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Deep Space Dash")
        self.clock = pygame.time.Clock()
        self.state = MENU
        
        # Color selection
        self.selected_color = 'blue'
        
        # Game objects
        self.ship = None
        self.obstacles: List[Obstacle] = []
        self.hud = HUD()
        
        # Game variables
        self.distance = 0  # Total distance in km
        self.pixels_traveled = 0  # For distance calculation
        self.current_speed = BASE_SPEED  # Current scrolling speed
        self.score = 0
        self.obstacle_speed = INITIAL_OBSTACLE_SPEED
        self.spawn_delay = INITIAL_SPAWN_DELAY
        self.spawn_timer = 0
        self.frame_count = 0
        self.is_boosting = False
        
        # Milestone tracking
        self.milestone_index = 0  # Index of next milestone to reach
        self.last_planet_passed = "Earth"
        self.passed_neptune = False
        self.procedural_milestones = []  # Generated milestones after Neptune
        self.next_procedural_distance = 5_000_000_000  # Start 500M km after Neptune
        
        # Stars for background
        self.stars = [(random.randint(0, SCREEN_WIDTH), 
                      random.randint(0, SCREEN_HEIGHT),
                      random.randint(1, 3)) for _ in range(100)]
        
    def generate_procedural_milestone(self):
        """Generate a random planet or galaxy name"""
        if random.random() < 0.7:  # 70% chance for planet
            name = f"{random.choice(PLANET_PREFIXES)}-{random.choice(PLANET_SUFFIXES)}"
            is_galaxy = False
        else:  # 30% chance for galaxy
            name = f"{random.choice(GALAXY_PREFIXES)} {random.choice(GALAXY_SUFFIXES)}"
            is_galaxy = True
        
        milestone = (name, self.next_procedural_distance, is_galaxy)
        self.procedural_milestones.append(milestone)
        
        # Next milestone will be 300M-800M km further
        self.next_procedural_distance += random.randint(300_000_000, 800_000_000)
        
    def reset_game(self):
        """Reset game state for new run"""
        self.ship = Spaceship(100, SCREEN_HEIGHT // 2, SHIP_COLORS[self.selected_color])
        self.obstacles = []
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
        
    def handle_input(self):
        """Process keyboard input"""
        keys = pygame.key.get_pressed()
        
        if self.state == MENU:
            if keys[pygame.K_SPACE]:
                self.state = COLOR_SELECT
                
        elif self.state == COLOR_SELECT:
            if keys[pygame.K_1]:
                self.selected_color = 'red'
                self.reset_game()
                self.state = RUNNING
            elif keys[pygame.K_2]:
                self.selected_color = 'green'
                self.reset_game()
                self.state = RUNNING
            elif keys[pygame.K_3]:
                self.selected_color = 'blue'
                self.reset_game()
                self.state = RUNNING
            elif keys[pygame.K_4]:
                self.selected_color = 'yellow'
                self.reset_game()
                self.state = RUNNING
                
        elif self.state == RUNNING:
            # Movement
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.ship.move(-1)
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.ship.move(1)
                
            # Boost with right arrow
            self.is_boosting = keys[pygame.K_RIGHT]
                
            # Pause
            if keys[pygame.K_p]:
                self.state = PAUSED
                
        elif self.state == PAUSED:
            if keys[pygame.K_p]:
                self.state = RUNNING
                
        elif self.state == GAME_OVER:
            if keys[pygame.K_r]:
                self.state = COLOR_SELECT
                
    def update_game(self):
        """Update game state during gameplay"""
        if self.state != RUNNING:
            return
            
        self.frame_count += 1
        
        # Calculate current speed with boost
        if self.is_boosting:
            self.current_speed = min(MAX_BOOST_SPEED, self.obstacle_speed + BOOST_SPEED)
        else:
            self.current_speed = self.obstacle_speed
        
        # Update distance traveled based on current speed
        self.pixels_traveled += self.current_speed
        self.distance = int(self.pixels_traveled * KM_PER_PIXEL)
        
        # Increase score (1 point per second)
        if self.frame_count % 60 == 0:
            self.score += 1
        
        # Gradually increase base difficulty
        self.obstacle_speed = min(MAX_OBSTACLE_SPEED, 
                                 self.obstacle_speed + SPEED_INCREASE_RATE)
        self.spawn_delay = max(MIN_SPAWN_DELAY, 
                              self.spawn_delay - SPAWN_DECREASE_RATE)
        
        # Spawn obstacles
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            y = random.randint(50, SCREEN_HEIGHT - 50)
            self.obstacles.append(Obstacle(SCREEN_WIDTH, y, self.obstacle_speed))
            self.spawn_timer = 0
        
        # Calculate speed multiplier for obstacles when boosting
        speed_multiplier = self.current_speed / self.obstacle_speed
        
        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update(speed_multiplier)
            
            # Remove off-screen obstacles
            if obstacle.is_off_screen():
                self.obstacles.remove(obstacle)
                self.score += 1  # Bonus point for passing obstacle
                
            # Check collision
            if self.ship.get_rect().colliderect(obstacle.get_rect()):
                self.state = GAME_OVER
                
        # Check for milestone achievements (original planets)
        if self.milestone_index < len(PLANET_MILESTONES):
            planet_name, planet_distance = PLANET_MILESTONES[self.milestone_index]
            if self.distance >= planet_distance:
                self.hud.show_milestone(planet_name, planet_distance)
                self.last_planet_passed = planet_name
                self.milestone_index += 1
                
                # Check if we just passed Neptune
                if planet_name == "Neptune":
                    self.passed_neptune = True
                    # Show special message
                    self.hud.milestone_text = "You are leaving our solar system!"
                    self.hud.milestone_timer = 240  # Show for 4 seconds
                    # Generate first procedural milestone
                    self.generate_procedural_milestone()
        
        # Check procedural milestones (after Neptune)
        elif self.passed_neptune:
            # Make sure we have upcoming milestones
            if not self.procedural_milestones or self.distance >= self.procedural_milestones[-1][1]:
                self.generate_procedural_milestone()
            
            # Check if we've reached any procedural milestone
            for i, (name, distance, is_galaxy) in enumerate(self.procedural_milestones):
                if self.distance >= distance and distance > 0:
                    self.hud.show_milestone(name, distance, is_galaxy)
                    self.last_planet_passed = name
                    # Mark as passed by setting distance to -1
                    self.procedural_milestones[i] = (name, -1, is_galaxy)
                    
    def get_next_planet_info(self) -> Tuple[str, int]:
        """Get name and distance to next planet milestone"""
        # Check original milestones
        if self.milestone_index < len(PLANET_MILESTONES):
            planet_name, planet_distance = PLANET_MILESTONES[self.milestone_index]
            distance_to_planet = planet_distance - self.distance
            return planet_name, distance_to_planet
        
        # Check procedural milestones
        elif self.procedural_milestones:
            for name, distance, is_galaxy in self.procedural_milestones:
                if distance > 0 and self.distance < distance:
                    distance_to_planet = distance - self.distance
                    return name, distance_to_planet
        
        return "Deep Space", 0
            
    def draw_stars(self):
        """Draw animated star field background"""
        for i, (x, y, size) in enumerate(self.stars):
            # Move stars left to simulate motion (faster when boosting)
            move_speed = self.current_speed * 0.3 if self.state == RUNNING else BASE_SPEED * 0.3
            new_x = x - move_speed
            if new_x < 0:
                new_x = SCREEN_WIDTH
                y = random.randint(0, SCREEN_HEIGHT)
            self.stars[i] = (new_x, y, size)
            pygame.draw.circle(self.screen, WHITE, (int(new_x), int(y)), size)
            
    def draw_menu(self):
        """Draw main menu screen"""
        self.screen.fill(BLACK)
        self.draw_stars()
        
        # Title
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("DEEP SPACE DASH", True, BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Instructions
        font = pygame.font.Font(None, 32)
        instructions = [
            "Navigate your spaceship through the asteroid field!",
            "",
            "Controls:",
            "W / UP ARROW - Move Up",
            "S / DOWN ARROW - Move Down",
            "RIGHT ARROW - Boost Speed",
            "P - Pause Game",
            "",
            "Press SPACE to Start"
        ]
        
        y = 250
        for line in instructions:
            text = font.render(line, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 40
            
    def draw_color_select(self):
        """Draw color selection screen"""
        self.screen.fill(BLACK)
        self.draw_stars()
        
        # Title
        title_font = pygame.font.Font(None, 56)
        title = title_font.render("Choose Your Spaceship Color", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Color options
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
            
            # Draw small spaceship preview
            preview_x = SCREEN_WIDTH // 2 - 150
            preview_y = y
            points = [
                (preview_x + 30, preview_y),
                (preview_x, preview_y - 10),
                (preview_x, preview_y + 10)
            ]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.circle(self.screen, ORANGE, (preview_x + 5, preview_y), 6)
            pygame.draw.circle(self.screen, YELLOW, (preview_x + 5, preview_y), 4)
            
            y += spacing
            
    def draw_game(self):
        """Draw gameplay screen"""
        self.screen.fill(BLACK)
        self.draw_stars()
        
        # Draw game objects
        self.ship.draw(self.screen)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
            
        # Draw boost indicator
        if self.is_boosting:
            boost_font = pygame.font.Font(None, 48)
            boost_text = boost_font.render("BOOST!", True, ORANGE)
            boost_rect = boost_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
            self.screen.blit(boost_text, boost_rect)
            
        # Draw HUD
        next_planet, distance_to_planet = self.get_next_planet_info()
        self.hud.draw_game_hud(self.screen, self.distance, self.current_speed,
                              self.score, next_planet, distance_to_planet)
        
        # Draw milestone toast if active
        self.hud.draw_milestone_toast(self.screen)
        
    def draw_paused(self):
        """Draw pause overlay"""
        self.draw_game()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        font = pygame.font.Font(None, 72)
        text = font.render("PAUSED", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)
        
        small_font = pygame.font.Font(None, 36)
        resume = small_font.render("Press P to Resume", True, WHITE)
        resume_rect = resume.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(resume, resume_rect)
        
    def draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill(BLACK)
        self.draw_stars()
        
        # Title
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("GAME OVER", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)
        
        # Stats
        font = pygame.font.Font(None, 36)
        stats = [
            f"Final Score: {self.score}",
            f"Distance Traveled: {self.distance:,} km",
            f"Maximum Speed: {self.current_speed:.1f} km/s",
            f"Last Location: {self.last_planet_passed}",
            "",
            "Press R to Play Again",
            "Press ESC to Quit"
        ]
        
        y = 250
        for line in stats:
            text = font.render(line, True, WHITE if line else BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 50
            
    def draw(self):
        """Main draw function"""
        if self.state == MENU:
            self.draw_menu()
        elif self.state == COLOR_SELECT:
            self.draw_color_select()
        elif self.state == RUNNING:
            self.draw_game()
        elif self.state == PAUSED:
            self.draw_paused()
        elif self.state == GAME_OVER:
            self.draw_game_over()
            
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == GAME_OVER or self.state == MENU:
                            running = False
                            
            # Input handling
            self.handle_input()
            
            # Update
            self.update_game()
            
            # Draw
            self.draw()
            
            # Frame rate
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()


def main():
    """Entry point"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()