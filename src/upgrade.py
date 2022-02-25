from typing import List
import pygame
from player import Player
from settings import *


class Upgrade:
    """Upgrade menu (used on pause)"""

    def __init__(self, player: Player) -> None:
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.attribute_nr = len(player.stats)
        self.attributes = list(player.stats.keys())
        self.max_values = list(player.maxstats.values())
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        self.width = self.display_surface.get_size()[0] // 6
        self.height = self.display_surface.get_size()[1] * .8

        self.selection_index = 0
        self.selection_time = None
        self.can_move = True

        self.create_items()

    def input(self):
        """Handle menu inputs"""
        keys = pygame.key.get_pressed()

        if self.can_move:
            if keys[pygame.K_RIGHT] and self.selection_index < self.attribute_nr - 1:
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
            elif keys[pygame.K_LEFT] and self.selection_index >= 1:
                self.selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

        if keys[pygame.K_SPACE]:
            self.can_move = False
            self.selection_time = pygame.time.get_ticks()
            self.items[self.selection_index].trigger(self.player)

    def create_items(self):
        """Create items UI"""
        self.items: List[Item] = []

        for item, index in enumerate(range(self.attribute_nr)):
            full_width = self.display_surface.get_size()[0]
            increment = full_width // self.attribute_nr
            left = (item * increment) + (increment - self.width) // 2

            top = self.display_surface.get_size()[1] * .1

            item = Item(left, top, self.width, self.height, index, self.font)

            self.items.append(item)

    def cooldowns(self):
        """Handle menu cooldowns"""
        if not self.can_move:
            current_time = pygame.time.get_ticks()

            if current_time - self.selection_time >= 300:
                self.can_move = True

    def display(self):
        self.input()
        self.cooldowns()

        for index, item in enumerate(self.items):
            name = self.attributes[index]
            value = self.player.get_value_by_index(index)
            max_value = self.max_values[index]
            cost = self.player.get_cost_by_index(index)

            item.display(self.display_surface, self.selection_index,
                         name, value, max_value, cost)


class Item:
    """Item UI for Upgrade menu"""

    def __init__(self, left: int, top: int, width: float, height: float, index: int, font: pygame.font.Font) -> None:
        self.rect = pygame.Rect(left, top, width, height)
        self.index = index
        self.font = font

    def display_names(self, surface: pygame.Surface, name: str, cost: int, selected: bool):
        color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR

        title_surf = self.font.render(name, False, color)
        title_rect = title_surf.get_rect(
            midtop=self.rect.midtop + pygame.math.Vector2(0, 20))

        cost_surf = self.font.render(f'{int(cost)}', False, color)
        cost_rect = cost_surf.get_rect(
            midbottom=self.rect.midbottom - pygame.math.Vector2(0, 20))

        surface.blit(title_surf, title_rect)
        surface.blit(cost_surf, cost_rect)

    def display_bar(self, surface: pygame.Surface, value: int, max_value: int, selected: bool):
        top = self.rect.midtop + pygame.math.Vector2(0, 60)
        bottom = self.rect.midbottom - pygame.math.Vector2(0, 60)
        color = BAR_COLOR_SELECTED if selected else BAR_COLOR

        full_height = bottom[1] - top[1]
        relative_number = (value / max_value) * full_height
        value_rect = pygame.Rect(
            top[0] - 15, bottom[1] - relative_number, 30, 10)

        pygame.draw.line(surface, color, top, bottom, 5)
        pygame.draw.rect(surface, color, value_rect)

    def trigger(self, player: Player):
        upgrade_attribute = list(player.stats.keys())[self.index]

        if player.exp >= player.upgrade_cost[upgrade_attribute] and player.stats[upgrade_attribute] < player.maxstats[upgrade_attribute]:
            player.exp -= player.upgrade_cost[upgrade_attribute]
            player.stats[upgrade_attribute] *= 1.2
            player.upgrade_cost[upgrade_attribute] *= 1.4

        if player.stats[upgrade_attribute] >= player.maxstats[upgrade_attribute]:
            player.stats[upgrade_attribute] = player.maxstats[upgrade_attribute]

    def display(self, surface: pygame.Surface, selection_num: int, name: str, value: int, max_value: int, cost: int):
        if self.index == selection_num:
            pygame.draw.rect(surface, UPGRADE_BG_COLOR_SELECTED, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)

        self.display_names(surface, name, cost, self.index == selection_num)
        self.display_bar(surface, value, max_value,
                         self.index == selection_num)
