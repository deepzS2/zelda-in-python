from typing import Tuple
from unittest.main import MAIN_EXAMPLES
import pygame
from player import Player
from settings import *
from entity import Entity
from support import *


class Enemy(Entity):
    """Generic enemy class"""

    def __init__(self, monster_name: str, pos: Tuple[int, int], obstacle_sprites: pygame.sprite.Group, *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)
        self.sprite_type = 'enemy'

        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]

        # Movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites

        # Stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']

        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 400

    def import_graphics(self, name: str):
        """Import enemy sprites + animations"""
        self.animations = {'idle': [], 'move': [], 'attack': []}
        main_path = f'graphics/monsters/{name}/'

        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)

    def get_player_distance_direction(self, player: Player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)

        distance = (player_vec - enemy_vec).magnitude()

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return (distance, direction)

    def get_status(self, player: Player):
        distance = self.get_player_distance_direction(player)[0]

        if distance <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0

            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'

    def actions(self, player: Player):
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
        elif self.status == 'move':
            self.direction = self.get_player_distance_direction(player)[1]
        else:
            self.direction = pygame.math.Vector2()

    def animate(self):
        """Handles animation"""
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def cooldown(self):
        """Handle cooldowns"""
        current_time = pygame.time.get_ticks()

        if not self.can_attack and current_time - self.attack_time >= self.attack_cooldown:
            self.can_attack = True

    def update(self):
        self.animate()
        self.cooldown()
        self.move(self.speed)

    def enemy_update(self, player: Player):
        self.get_status(player)
        self.actions(player)