from pydoc import visiblename
from random import randint, choice
from typing import *
import pygame
from enemy import Enemy
from magic import MagicPlayer
from particles import AnimationPlayer

from settings import *
from player import Player
from support import *
from tile import Tile
from ui import UI
from weapon import Weapon
from upgrade import Upgrade


class Level:
    """Handle the scene aspects like camera, map, etc."""

    def __init__(self) -> None:
        # Get display surface
        self.display_surface = pygame.display.get_surface()

        self.game_paused = False

        # Sprites group
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # Attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        self.create_map()

        self.ui = UI()
        self.upgrade = Upgrade(self.player)

        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

    def create_map(self):
        """Create the map with the svgs on map/*.csv"""
        layouts = {
            'boundary': import_csv_layout('map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('map/map_Grass.csv'),
            'object': import_csv_layout('map/map_Objects.csv'),
            'entities': import_csv_layout('map/map_Entities.csv')
        }

        graphics = {
            'grass': import_folder('graphics/grass'),
            'objects': import_folder('graphics/objects')
        }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE

                        if style == 'boundary':
                            Tile((x, y), 'invisible', [self.obstacle_sprites])
                        if style == 'grass':
                            random_grass = choice(graphics['grass'])
                            Tile(
                                (x, y),
                                'grass',
                                [self.visible_sprites, self.obstacle_sprites,
                                    self.attackable_sprites],
                                surface=random_grass
                            )

                        if style == 'object':
                            surface = graphics['objects'][int(col)]
                            Tile((x, y), 'object', [
                                 self.visible_sprites, self.obstacle_sprites], surface=surface)

                        if style == 'entities':
                            if col == '394':
                                self.player = Player(
                                    (x, y), self.obstacle_sprites, self.create_attack, self.create_magic, self.destroy_attack, [self.visible_sprites])
                            else:
                                if col == '390':
                                    monster_name = 'bamboo'
                                elif col == '391':
                                    monster_name = 'spirit'
                                elif col == '392':
                                    monster_name = 'raccoon'
                                else:
                                    monster_name = 'squid'

                                Enemy(monster_name,
                                      (x, y),
                                      self.obstacle_sprites,
                                      self.damage_player,
                                      self.trigger_death_particles,
                                      [
                                          self.visible_sprites, self.attackable_sprites
                                      ])

    def create_attack(self):
        """Create the weapon sprite"""
        self.current_attack = Weapon(
            self.player,
            [self.visible_sprites, self.attack_sprites]
        )

    def create_magic(self, style: str, strength: int, cost: int):
        """Create the magic sprite"""
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [
                                   self.visible_sprites])
        elif style == 'flame':
            self.magic_player.flame(
                self.player, cost, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        """Destroy the weapon sprite"""
        if self.current_attack:
            self.current_attack.kill()

        self.current_attack = None

    def player_attack_logic(self):
        """Create the player damage interaction with the enemy"""
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(
                    attack_sprite, self.attackable_sprites, False)

                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'grass':
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0, 75)

                            for leaf in range(randint(3, 6)):
                                self.animation_player.create_grass_particles(
                                    pos - offset, [self.visible_sprites])

                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(
                                self.player, attack_sprite.sprite_type)

    def trigger_death_particles(self, pos: Tuple[int, int], particle_type: str):
        """Monsters death animation invocation"""
        self.animation_player.create_particles(
            particle_type, pos, [self.visible_sprites])

    def damage_player(self, amount: int, attack_type: str):
        """Create the enemy damage interaction with the player"""
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(
                attack_type, self.player.rect.center, [self.visible_sprites])

    def add_exp(self, amount: int):
        """Add exp to player"""
        self.player.exp += amount

    def toggle_menu(self):
        """Toggle upgrade menu"""
        self.game_paused = not self.game_paused

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)

        if self.game_paused:
            self.upgrade.display()
        else:
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()


class YSortCameraGroup(pygame.sprite.Group):
    """Custom sprite group to centering the player rendering the sprites based on the Y axis"""

    def __init__(self, *sprites: Union[pygame.sprite.Sprite, Sequence[pygame.sprite.Sprite]]) -> None:
        super().__init__(*sprites)

        self.display_surface = pygame.display.get_surface()

        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2

        self.offset = pygame.math.Vector2()

        self.floor_surface = pygame.image.load(
            'graphics/tilemap/ground.png').convert()
        self.floor_rect = self.floor_surface.get_rect(topleft=(0, 0))

    def custom_draw(self, player: Player):
        """Center player to camera"""
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surface, floor_offset_pos)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    def enemy_update(self, player: Player):
        """Update enemies"""
        enemy_sprites = [
            sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy'
        ]

        for enemy in enemy_sprites:
            enemy.enemy_update(player)
