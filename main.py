import pygame
import sys
import random
import time
import math

# Initialize Pygame and set up the display
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound playback
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pokemon Battle")

# Colors and constants
WHITE, BLACK, RED, GREEN, BLUE, YELLOW, ORANGE, BROWN = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0), (165, 42, 42)
POKEMON_SIZE = (100, 100)
MOVE_SPEED = 5
ATTACK_COOLDOWN = 2  # Cooldown time between attacks in seconds
PLATFORM_HEIGHT = 100

# Load images
def load_image(path, size):
    return pygame.transform.scale(pygame.image.load(path), size)

background_img = load_image("background.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT))
pikachu_img = load_image("pikachu.png", POKEMON_SIZE)
charmander_img = load_image("charmander.png", POKEMON_SIZE)
alien_img = load_image("alien.png", (60, 60))  # Adjust size as needed

# Load sound effects
thunder_sound = pygame.mixer.Sound("thunder.mp3")
fireball_sound = pygame.mixer.Sound("fireball.mp3")
suspense_music = pygame.mixer.Sound("suspence.mp3")

class Pokemon:
    def __init__(self, name, image, health, position, attack_type, shield_key):
        self.name = name
        self.image = image
        self.health = self.max_health = health
        self.position = list(position)
        self.rect = self.image.get_rect(topleft=self.position)
        self.last_attack_time = 0
        self.is_fainted = False
        self.faint_animation = 0
        self.shake_amount = 0
        self.attack_type = attack_type
        self.shield_active = False
        self.shield_cooldown = 0
        self.shield_key = shield_key
        self.shield_timer = 0
        self.shield_duration = 0.2  # 0.2 seconds of active shield time
        self.aura_intensity = 1  # Start with full intensity
        self.aura_size = 20
        self.aura_color = (255, 255, 0) if attack_type == "lightning" else (255, 165, 0)  # Yellow for Pikachu, Orange for Charmander
        self.attack_count = 0
        self.max_aura_size = 50
        self.aura_time = 0

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        self.shake_amount = min(damage, 15)
        if self.health == 0:
            self.is_fainted = True

    def attack_opponent(self):
        if self.is_fainted:
            return 0

        current_time = time.time()
        if current_time - self.last_attack_time < ATTACK_COOLDOWN:
            return 0  # Can't attack yet

        self.last_attack_time = current_time
        self.attack_count += 1
        self.aura_size = min(self.max_aura_size, self.aura_size + 2)
        return random.randint(20, 40)

    def move(self, dx):
        if not self.is_fainted:
            self.position[0] = max(0, min(SCREEN_WIDTH - POKEMON_SIZE[0], self.position[0] + dx))
            self.rect.topleft = self.position

    def activate_shield(self):
        if self.shield_cooldown <= 0 and not self.shield_active:
            self.shield_active = True
            self.shield_timer = self.shield_duration
            self.shield_cooldown = 2  # 2 second cooldown

    def update(self, dt):
        if self.shield_cooldown > 0:
            self.shield_cooldown -= dt
        if self.shield_active:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active = False
        if not self.is_fainted:
            self.aura_time += dt

    def draw(self, surface):
        if not self.is_fainted:
            # Draw pulsating, moving aura
            aura_pulse = math.sin(self.aura_time * 5) * 0.2 + 0.8  # Pulsate between 0.6 and 1.0
            current_aura_size = int(self.aura_size * aura_pulse)
            
            aura_surf = pygame.Surface((self.rect.width + current_aura_size * 2, self.rect.height + current_aura_size * 2), pygame.SRCALPHA)
            aura_color = [min(255, c + 20 * self.attack_count) for c in self.aura_color]  # Brighten color
            
            # Create multiple ellipses for a more dynamic effect
            for i in range(3):
                offset = math.sin(self.aura_time * 3 + i * 2) * 5
                pygame.draw.ellipse(aura_surf, (*aura_color, 50), 
                                    (offset, offset, 
                                     self.rect.width + current_aura_size * 2 - offset * 2, 
                                     self.rect.height + current_aura_size * 2 - offset * 2))
            
            surface.blit(aura_surf, (self.rect.x - current_aura_size, self.rect.y - current_aura_size))

        # Draw Pokemon
        surface.blit(self.image, self.rect.topleft)

        if self.is_fainted:
            self.faint_animation = min(1, self.faint_animation + 0.05)
            rotated_image = pygame.transform.rotate(self.image, 90 * self.faint_animation)
            new_rect = rotated_image.get_rect(center=self.rect.center)
            new_rect.y += POKEMON_SIZE[1] * 0.5 * self.faint_animation
            surface.blit(rotated_image, new_rect.topleft)
        else:
            # Apply shake effect
            shake_offset = random.randint(-self.shake_amount, self.shake_amount)
            shaken_position = (self.position[0] + shake_offset, self.position[1])
            surface.blit(self.image, shaken_position)
            self.shake_amount = max(0, self.shake_amount - 1)  # Reduce shake over time

        if self.shield_active:
            pygame.draw.circle(surface, (0, 255, 255, 128), self.rect.center, self.rect.width // 2, 5)

    def is_alive(self):
        return self.health > 0

class Alien:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = alien_img
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = random.uniform(1, 3)
        self.health = 20
        self.wobble_speed = random.uniform(0.05, 0.1)
        self.wobble_dist = random.uniform(5, 15)
        self.t = random.uniform(0, math.pi * 2)

    def move(self):
        self.y += self.speed
        self.t += self.wobble_speed
        self.x += math.sin(self.t) * self.wobble_dist
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        # Apply a pulsating effect
        pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.1 + 0.9
        pulsed_image = pygame.transform.scale(self.image, 
                                              (int(self.rect.width * pulse), 
                                               int(self.rect.height * pulse)))
        pulsed_rect = pulsed_image.get_rect(center=self.rect.center)
        
        # Apply a simple rotation effect
        angle = math.sin(pygame.time.get_ticks() * 0.003) * 10
        rotated_image = pygame.transform.rotate(pulsed_image, angle)
        rotated_rect = rotated_image.get_rect(center=pulsed_rect.center)
        
        screen.blit(rotated_image, rotated_rect)

        # Draw a simple glow effect
        glow_radius = int(self.rect.width * 0.6)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (0, 255, 0, 64), (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surf, (self.rect.centerx - glow_radius, self.rect.centery - glow_radius), special_flags=pygame.BLEND_ADD)

class Battle:
    def __init__(self, pokemon1, pokemon2):
        self.pokemon1 = pokemon1
        self.pokemon2 = pokemon2
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        self.message = ""
        self.message_timer = 0
        self.animation = None
        self.animation_timer = 0
        self.fireball_particles = []
        self.last_time = time.time()
        self.animation_duration = 0.5  # 0.5 second animation duration
        self.aliens = []
        self.alien_spawn_timer = 0
        
        # Start playing the background music
        suspense_music.play(-1)  # -1 means loop indefinitely

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Movement
        if keys[pygame.K_a]:
            self.pokemon1.move(-MOVE_SPEED)
        if keys[pygame.K_d]:
            self.pokemon1.move(MOVE_SPEED)
        if keys[pygame.K_LEFT]:
            self.pokemon2.move(-MOVE_SPEED)
        if keys[pygame.K_RIGHT]:
            self.pokemon2.move(MOVE_SPEED)
        
        # Attacks
        if keys[pygame.K_SPACE]:
            self.perform_attack(self.pokemon1, self.pokemon2)
        if keys[pygame.K_RETURN]:
            self.perform_attack(self.pokemon2, self.pokemon1)
        
        # Shields
        if keys[self.pokemon1.shield_key]:
            self.pokemon1.activate_shield()
        if keys[self.pokemon2.shield_key]:
            self.pokemon2.activate_shield()

    def perform_attack(self, attacker, defender):
        if self.animation:
            return  # Don't allow new attacks while an animation is playing

        damage = attacker.attack_opponent()
        if damage > 0:
            self.start_animation(attacker, defender, damage)

    def set_message(self, msg):
        self.message = msg
        self.message_timer = time.time()

    def start_animation(self, attacker, defender, damage):
        self.animation = {
            "attacker": attacker,
            "defender": defender,
            "damage": damage,
            "progress": 0,
            "start_time": time.time()
        }
        
        # Play appropriate sound effect based on attack type
        if attacker.attack_type == "lightning":
            thunder_sound.play()
        elif attacker.attack_type == "fire":
            fireball_sound.play()

    def update_animation(self, dt):
        if not self.animation:
            return

        current_time = time.time()
        elapsed_time = current_time - self.animation["start_time"]
        self.animation["progress"] = min(elapsed_time / self.animation_duration, 1)

        if self.animation["progress"] >= 1:
            # Animation is complete, apply damage
            if self.animation["defender"].shield_active:
                self.set_message(f"{self.animation['defender'].name} blocked the attack!")
            else:
                self.animation["defender"].take_damage(self.animation["damage"])
                self.set_message(f"{self.animation['attacker'].name} dealt {self.animation['damage']} damage!")
            self.animation = None

    def draw_attack_animation(self, surface):
        if not self.animation:
            return

        attacker = self.animation["attacker"]
        defender = self.animation["defender"]
        progress = self.animation["progress"]

        start_pos = (attacker.rect.centerx, attacker.rect.centery)
        end_pos = (defender.rect.centerx, defender.rect.centery)

        current_pos = (
            start_pos[0] + (end_pos[0] - start_pos[0]) * progress,
            start_pos[1] + (end_pos[1] - start_pos[1]) * progress
        )

        if attacker.attack_type == "lightning":
            # Draw lightning bolt
            points = [start_pos]
            for _ in range(3):
                points.append((
                    points[-1][0] + (end_pos[0] - points[-1][0]) * 0.25,
                    points[-1][1] + (end_pos[1] - points[-1][1]) * 0.25 + random.randint(-20, 20)
                ))
            points.append(current_pos)
            pygame.draw.lines(surface, YELLOW, False, points, 3 + attacker.attack_count // 3)
        else:
            # Draw fireball
            pygame.draw.circle(surface, ORANGE, (int(current_pos[0]), int(current_pos[1])), 10 + attacker.attack_count // 3)
            
            # Add fire particles
            for _ in range(5 + attacker.attack_count):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 3)
                pygame.draw.circle(surface, (255, random.randint(100, 200), 0), 
                                   (int(current_pos[0] + math.cos(angle) * speed * 5),
                                    int(current_pos[1] + math.sin(angle) * speed * 5)), 
                                   2)

    def draw_frame(self):
        screen.blit(background_img, (0, 0))
        
        # Draw platform
        pygame.draw.rect(screen, BROWN, (0, SCREEN_HEIGHT - PLATFORM_HEIGHT, SCREEN_WIDTH, PLATFORM_HEIGHT))
        
        self.pokemon1.draw(screen)
        self.pokemon2.draw(screen)
        
        # Draw attack animation
        self.draw_attack_animation(screen)
        
        # Draw health bars
        self.draw_health_bar(self.pokemon1, 10, 10)  # Pikachu's health bar in top left corner
        self.draw_health_bar(self.pokemon2, SCREEN_WIDTH - 250, 10)  # Charmander's health bar
        
        # Draw message
        if time.time() - self.message_timer < 2:  # Display message for 2 seconds
            text = self.font.render(self.message, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - PLATFORM_HEIGHT - 50))
            screen.blit(text, text_rect)

        # Draw controls guide with smaller font
        controls_font = pygame.font.Font(None, 24)  # Smaller font size
        controls_text = [
            "Pikachu: A/D move, SPACE attack, W shield",
            "Charmander: Left/Right move, ENTER attack, L shield"
        ]
        for i, text in enumerate(controls_text):
            control_text = controls_font.render(text, True, BLACK)
            screen.blit(control_text, (10, SCREEN_HEIGHT - 50 + i * 25))  # Adjust vertical position

        # Draw shield cooldown indicators
        self.draw_cooldown_indicator(self.pokemon1, 10, 60)
        self.draw_cooldown_indicator(self.pokemon2, SCREEN_WIDTH - 250, 60)

        # Draw aliens
        for alien in self.aliens:
            alien.draw(screen)

    def draw_health_bar(self, pokemon, x, y):
        bar_width = 200
        bar_height = 20
        health_percentage = pokemon.health / pokemon.max_health
        health_bar_width = int(bar_width * health_percentage)
        
        pygame.draw.rect(screen, RED, (x, y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (x, y, health_bar_width, bar_height))
        pygame.draw.rect(screen, BLACK, (x, y, bar_width, bar_height), 2)
        
        health_text = self.font.render(f"{pokemon.name}: {pokemon.health}/{pokemon.max_health}", True, BLACK)
        text_x = x + (bar_width - health_text.get_width()) // 2  # Center the text
        screen.blit(health_text, (text_x, y + bar_height + 5))

    def draw_cooldown_indicator(self, pokemon, x, y):
        if pokemon.shield_active:
            status = "ACTIVE"
            color = (0, 255, 0)  # Green
        elif pokemon.shield_cooldown > 0:
            status = f"Cooldown: {pokemon.shield_cooldown:.1f}"
            color = (255, 0, 0)  # Red
        else:
            status = "Ready"
            color = (0, 255, 0)  # Green

        cooldown_text = self.font.render(f"Shield: {status}", True, color)
        screen.blit(cooldown_text, (x, y))

    def spawn_alien(self):
        x = random.randint(0, SCREEN_WIDTH - alien_img.get_width())
        self.aliens.append(Alien(x, -alien_img.get_height()))

    def update(self, dt):
        # Update and spawn aliens
        self.alien_spawn_timer += 1
        if self.alien_spawn_timer >= 120:  # Spawn alien every 2 seconds
            self.spawn_alien()
            self.alien_spawn_timer = 0

        for alien in self.aliens[:]:
            alien.move()
            if alien.y > SCREEN_HEIGHT:
                self.aliens.remove(alien)

        # Check for collisions with aliens
        for player in [self.pokemon1, self.pokemon2]:
            for alien in self.aliens[:]:
                if self.check_collision(player, alien):
                    player.health -= 10
                    self.aliens.remove(alien)

    def check_collision(self, obj1, obj2):
        return obj1.rect.colliderect(obj2.rect)

    def run(self):
        running = True
        last_time = time.time()
        while running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.handle_input()
            self.pokemon1.update(dt)
            self.pokemon2.update(dt)
            self.update_animation(dt)
            self.update(dt)
            self.draw_frame()
            pygame.display.flip()

            if not (self.pokemon1.is_alive() and self.pokemon2.is_alive()):
                winner = self.pokemon1 if self.pokemon1.is_alive() else self.pokemon2
                self.set_message(f"{winner.name} wins!")
                pygame.display.flip()
                pygame.time.delay(3000)
                suspense_music.stop()  # Stop the music when the game ends
                return

            self.clock.tick(60)

# Create Pokemon instances
pikachu = Pokemon("Pikachu", pikachu_img, 100, (50, SCREEN_HEIGHT - PLATFORM_HEIGHT - POKEMON_SIZE[1]), "lightning", pygame.K_w)
charmander = Pokemon("Charmander", charmander_img, 100, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - PLATFORM_HEIGHT - POKEMON_SIZE[1]), "fire", pygame.K_l)

battle = Battle(pikachu, charmander)
battle.run()

pygame.quit()
sys.exit()