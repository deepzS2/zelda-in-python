from os import walk
from typing import *
import pygame
from entity import Entity

from settings import *
from support import import_folder
from tile import Tile


class Player(Entity):
    """Handle player movement, inputs, collisions, hitboxes, etc."""

    def __init__(self, pos: Tuple[int, int], obstacle_sprites: pygame.sprite.Group, create_attack: Callable[[], None], create_magic: Callable[[], None], destroy_attack: Callable[[], None], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)

        # Graphics setup
        self.import_player_assets()
        self.status = 'down'
        self.image = pygame.image.load(
            'graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)

        # Hitbox and obstacles
        self.obstacle_sprites = obstacle_sprites
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET['player'])

        # Hitbox damage
        self.vulnerable = True
        self.hurt_time = None
        self.invunerability_duration = 500

        # Weapon
        self.can_switch_weapon = True
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.switch_weapon_time = None
        self.switch_duration_cooldown = 200
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]

        self.weapon_attack_sound = pygame.mixer.Sound('audio/sword.wav')
        self.weapon_attack_sound.set_volume(0.4)

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
        self.maxstats = {'health': 300, 'energy': 140,
                         'attack': 20, 'magic': 10, 'speed': 10}
        self.upgrade_cost = {'health': 100, 'energy': 100,
                             'attack': 100, 'magic': 100, 'speed': 100}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.exp = 500
        self.speed = self.stats['speed']

    def import_player_assets(self):
        """Import player sprites + animations"""
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
            self.weapon_attack_sound.play()

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

    def energy_recovery(self):
        """Recover player energy (for spells)"""
        if self.energy < self.stats['energy']:
            self.energy += 0.01 * self.stats['magic']
        else:
            self.energy = self.stats['energy']

    def cooldowns(self):
        """Handle cooldowns"""
        current_time = pygame.time.get_ticks()

        if self.attacking and current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
            self.attacking = False
            self.destroy_attack()

        if not self.can_switch_weapon and current_time - self.switch_weapon_time >= self.switch_duration_cooldown:
            self.can_switch_weapon = True

        if not self.can_switch_magic and current_time - self.magic_switch_time >= self.switch_duration_cooldown:
            self.can_switch_magic = True

        if not self.vulnerable and current_time - self.hurt_time >= self.invunerability_duration:
            self.vulnerable = True

    def animate(self):
        """Handles animation"""
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def get_full_weapon_damage(self) -> int:
        """Sum base damage and weapon damage"""
        base_damage = self.stats['attack']
        weapon_damage = weapon_data[self.weapon]['damage']
        return weapon_damage + base_damage

    def get_full_magic_damage(self) -> int:
        """Sum of base magic damage and spell damage"""
        base_damage = self.stats['magic']
        spell_damage = magic_data[self.magic]['strength']
        return base_damage + spell_damage

    def get_value_by_index(self, index: int):
        return list(self.stats.values())[index]

    def get_cost_by_index(self, index: int):
        return list(self.upgrade_cost.values())[index]

    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.stats['speed'])
        self.energy_recovery()
