from typing import Callable, Tuple
from unittest.main import MAIN_EXAMPLES
import pygame
from player import Player
from settings import *
from entity import Entity
from support import *


class Enemy(Entity):
    """Generic enemy class"""

    def __init__(self, monster_name: str, pos: Tuple[int, int], obstacle_sprites: pygame.sprite.Group, damage_player: Callable[[int, str], None], trigger_death_particles: Callable[[Tuple[int, int], str], None], add_exp: Callable[[int], None], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)
        self.sprite_type = 'enemy'

        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image: pygame.Surface = self.animations[self.status][self.frame_index]

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
        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.add_exp = add_exp

        self.vulnerable = True
        self.hit_time = None
        self.invencibility_duration = 300

        self.death_sound = pygame.mixer.Sound('audio/death.wav')
        self.hit_sound = pygame.mixer.Sound('audio/hit.wav')
        self.attack_sound = pygame.mixer.Sound(monster_info['attack_sound'])

        self.death_sound.set_volume(.2)
        self.hit_sound.set_volume(.2)
        self.attack_sound.set_volume(.3)

    def import_graphics(self, name: str):
        """Import enemy sprites + animations"""
        self.animations = {'idle': [], 'move': [], 'attack': []}
        main_path = f'graphics/monsters/{name}/'

        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)

    def get_player_distance_direction(self, player: Player):
        """Get the distance and direction between enemy and player"""
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)

        distance = (player_vec - enemy_vec).magnitude()

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return (distance, direction)

    def get_status(self, player: Player):
        """Control enemy status"""
        distance = self.get_player_distance_direction(player)[0]

        if distance <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0

            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'

    def get_damage(self, player: Player, attack_type: str):
        """Get the damage data"""
        if self.vulnerable:
            self.hit_sound.play()
            self.direction = self.get_player_distance_direction(player)[1]

            if attack_type == 'weapon':
                self.health -= player.get_full_weapon_damage()
            else:
                self.health -= player.get_full_magic_damage()

            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def check_damage(self):
        """Check if the enemy is dead"""
        if self.health < 0:
            self.kill()
            self.trigger_death_particles(self.rect.center, self.monster_name)
            self.add_exp(self.exp)
            self.death_sound.play()

    def hit_reaction(self):
        """Called on hit"""
        if not self.vulnerable:
            self.direction *= -self.resistance

    def actions(self, player: Player):
        """Control enemy based on status"""
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            self.attack_sound.play()
            self.damage_player(self.attack_damage, self.attack_type)
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

        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def cooldown(self):
        """Handle cooldowns"""
        current_time = pygame.time.get_ticks()

        if not self.can_attack and current_time - self.attack_time >= self.attack_cooldown:
            self.can_attack = True

        if not self.vulnerable and current_time - self.hit_time >= self.invencibility_duration:
            self.vulnerable = True

    def update(self):
        self.animate()
        self.cooldown()
        self.hit_reaction()
        self.move(self.speed)
        self.check_damage()

    def enemy_update(self, player: Player):
        self.get_status(player)
        self.actions(player)
