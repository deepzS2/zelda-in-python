from os import walk
from typing import *
import pygame

from settings import *
from support import import_folder
from tile import Tile


class Player(pygame.sprite.Sprite):
    """Handle player movement, inputs, collisions, hitboxes, etc."""

    def __init__(self, pos: Tuple[int, int], obstacle_sprites: pygame.sprite.Group, create_attack: Callable[[], None], create_magic: Callable[[], None], destroy_attack: Callable[[], None], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)

        # Graphics setup
        self.import_player_assets()
        self.status = 'down'
        self.image = pygame.image.load(
            'graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)

        # Animation
        self.frame_index = 0
        self.animation_speed = .15

        # Hitbox and obstacles
        self.obstacle_sprites = obstacle_sprites
        self.hitbox = self.rect.inflate(0, -25)

        # Movement
        self.direction = pygame.math.Vector2()

        # Weapon
        self.can_switch_weapon = True
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.switch_weapon_time = None
        self.switch_duration_cooldown = 200
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]

        # Magic
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.weapon_index]
        self.can_switch_magic = True
        self.magic_switch_time = None

        # Attack
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

        # Stats
        self.stats = {'health': 100, 'energy': 60,
                      'attack': 10, 'magic': 4, 'speed': 6}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.exp = 123
        self.speed = self.stats['speed']

    def import_player_assets(self):
        character_path = "graphics/player/"
        self.animations: Dict[str, List[pygame.Surface]] = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
            'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def movementInput(self, keys: Sequence[bool]):
        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.status = 'down'
        else:
            self.direction.y = 0

        if keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.status = 'left'
        elif keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.status = 'right'
        else:
            self.direction.x = 0

    def input(self):
        """Handle player inputs"""
        keys = pygame.key.get_pressed()

        self.movementInput(keys)

        # Attack
        if keys[pygame.K_SPACE] and not self.attacking:
            self.attacking = True
            self.attack_time = pygame.time.get_ticks()
            self.create_attack()

        # Magic
        if keys[pygame.K_LCTRL] and not self.attacking:
            self.attacking = True
            self.attack_time = pygame.time.get_ticks()

            style = list(magic_data.keys())[self.magic_index]
            strength = list(magic_data.values())[
                self.magic_index]['strength'] + self.stats['magic']
            cost = list(magic_data.values())[self.magic_index]['cost']

            self.create_magic(style, strength, cost)

        # Switch weapon
        if keys[pygame.K_q] and self.can_switch_weapon:
            self.can_switch_weapon = False
            self.switch_weapon_time = pygame.time.get_ticks()

            if self.weapon_index < len(list(weapon_data.keys())) - 1:
                self.weapon_index += 1
            else:
                self.weapon_index = 0
            self.weapon = list(weapon_data.keys())[self.weapon_index]

        # Switch magic
        if keys[pygame.K_e] and self.can_switch_magic:
            self.can_switch_magic = False
            self.magic_switch_time = pygame.time.get_ticks()

            if self.magic_index < len(list(magic_data.keys())) - 1:
                self.magic_index += 1
            else:
                self.magic_index = 0

            self.magic = list(magic_data.keys())[self.magic_index]

    def get_status(self):
        """Set the players status based on inputs"""
        # Idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status = self.status + '_idle'

        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0

            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle', '_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')

    def move(self, speed: int):
        """Handle movement"""
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')

        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')

        self.rect.center = self.hitbox.center

    def collision(self, direction: Literal['horizontal', 'vertical']):
        """Check for collisions in X and Y direction"""
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom

    def cooldowns(self):
        """Handle cooldowns"""
        current_time = pygame.time.get_ticks()

        if self.attacking and current_time - self.attack_time >= self.attack_cooldown:
            self.attacking = False
            self.destroy_attack()

        if not self.can_switch_weapon and current_time - self.switch_weapon_time >= self.switch_duration_cooldown:
            self.can_switch_weapon = True

        if not self.can_switch_magic and current_time - self.magic_switch_time >= self.switch_duration_cooldown:
            self.can_switch_magic = True

    def animate(self):
        """Handles animation"""
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)
