#! /usr/bin/env python3

from settings import WIDTH, HEIGTH, FPS
from level import Level
import pygame
import sys


class Game:
    """Handles game loop"""

    def __init__(self):

        # general setup
        pygame.init()
        pygame.display.set_caption('Zelda')
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        self.clock = pygame.time.Clock()

        self.level = Level()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill('black')
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()
