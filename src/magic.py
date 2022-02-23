from random import randint
import pygame
from particles import AnimationPlayer
from player import Player
from settings import *


class MagicPlayer:
    def __init__(self, animation_player: AnimationPlayer) -> None:
        self.animation_player = animation_player

    def heal(self, player: Player, strength: int, cost: int, *groups: pygame.sprite.AbstractGroup):
        if player.energy >= cost:
            player.health += strength
            player.energy -= cost

            if player.health >= player.stats['health']:
                player.health = player.stats['health']

            pos = player.rect.center

            self.animation_player.create_particles('aura', pos, *groups)
            self.animation_player.create_particles('heal', pos, *groups)

    def flame(self, player: Player, cost: int, *groups: pygame.sprite.AbstractGroup):
        if player.energy >= cost:
            player.energy -= cost

            if player.status.split("_")[0] == 'right':
                direction = pygame.math.Vector2(1, 0)
            elif player.status.split("_")[0] == 'left':
                direction = pygame.math.Vector2(-1, 0)
            elif player.status.split("_")[0] == 'up':
                direction = pygame.math.Vector2(0, -1)
            else:
                direction = pygame.math.Vector2(0, 1)

            for i in range(1, 6):
                if direction.x:
                    offset_x = (direction.x * i) * TILESIZE

                    x = player.rect.centerx + offset_x + \
                        randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + \
                        randint(-TILESIZE // 3, TILESIZE // 3)

                    self.animation_player.create_particles(
                        'flame', (x, y), *groups)
                else:
                    offset_y = (direction.y * i) * TILESIZE

                    x = player.rect.centerx + \
                        randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + offset_y + \
                        randint(-TILESIZE // 3, TILESIZE // 3)

                    self.animation_player.create_particles(
                        'flame', (x, y), *groups)