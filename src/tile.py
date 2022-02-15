from typing import *
import pygame

from settings import *


class Tile(pygame.sprite.Sprite):
    """Represents a tile in the game"""

    def __init__(self, pos: Tuple[int, int], sprite_type: Literal['grass', 'invisible', 'object'], *groups: pygame.sprite.AbstractGroup, surface=pygame.Surface((TILESIZE, TILESIZE))) -> None:
        super().__init__(*groups)

        self.sprite_type = sprite_type
        self.image = surface

        if sprite_type == 'object':
            self.rect = self.image.get_rect(
                topleft=(pos[0], pos[1] - TILESIZE))
        else:
            self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
