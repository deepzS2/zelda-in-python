from csv import reader
from os import walk
from typing import List

import pygame


def import_csv_layout(path: str) -> List[str]:
    """Import a CSV file"""
    terrain_map = []

    with open(path) as level_map:
        layout = reader(level_map, delimiter=',')

        for row in layout:
            terrain_map.append(list(row))

        return terrain_map


def import_folder(path: str) -> List[pygame.Surface]:
    """Take all images from a folder"""
    surface_list = []

    for _, __, image_files in walk(path):
        for img in image_files:
            full_path = path + '/' + img
            image_surface = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surface)

    return surface_list
