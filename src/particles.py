from random import choice
from typing import List, Tuple
import pygame
from support import import_folder


class AnimationPlayer:
    """Hold the particles animations"""

    def __init__(self) -> None:
        self.frames = {
            # magic
            'flame': import_folder('graphics/particles/flame/frames'),
            'aura': import_folder('graphics/particles/aura'),
            'heal': import_folder('graphics/particles/heal/frames'),

            # attacks
            'claw': import_folder('graphics/particles/claw'),
            'slash': import_folder('graphics/particles/slash'),
            'sparkle': import_folder('graphics/particles/sparkle'),
            'leaf_attack': import_folder('graphics/particles/leaf_attack'),
            'thunder': import_folder('graphics/particles/thunder'),

            # monster deaths
            'squid': import_folder('graphics/particles/smoke_orange'),
            'raccoon': import_folder('graphics/particles/raccoon'),
            'spirit': import_folder('graphics/particles/nova'),
            'bamboo': import_folder('graphics/particles/bamboo'),

            # leafs
            'leaf': (
                import_folder('graphics/particles/leaf1'),
                import_folder('graphics/particles/leaf2'),
                import_folder('graphics/particles/leaf3'),
                import_folder('graphics/particles/leaf4'),
                import_folder('graphics/particles/leaf5'),
                import_folder('graphics/particles/leaf6'),
                self.reflect_images(import_folder('graphics/particles/leaf1')),
                self.reflect_images(import_folder('graphics/particles/leaf2')),
                self.reflect_images(import_folder('graphics/particles/leaf3')),
                self.reflect_images(import_folder('graphics/particles/leaf4')),
                self.reflect_images(import_folder('graphics/particles/leaf5')),
                self.reflect_images(import_folder('graphics/particles/leaf6'))
            )
        }

    def reflect_images(self, frames: List[pygame.Surface]):
        """Flip an list of images (X axis)"""
        new_frames = []

        for frame in frames:
            flipped_frame = pygame.transform.flip(frame, True, False)
            new_frames.append(flipped_frame)

        return new_frames

    def create_grass_particles(self, pos: Tuple[int, int], groups: pygame.sprite.AbstractGroup):
        animation_frames = choice(self.frames['leaf'])

        ParticleEffect(pos, animation_frames, groups)

    def create_particles(self, animation_type: str, pos: Tuple[int, int], groups: pygame.sprite.AbstractGroup):
        animation_frames = self.frames[animation_type]

        ParticleEffect(pos, animation_frames, groups)


class ParticleEffect(pygame.sprite.Sprite):
    """Particles!"""

    def __init__(self, pos: Tuple[int, int], animation_frames: List[pygame.Surface], *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)

        self.frame_index = 0
        self.animation_speed = 0.15
        self.frames = animation_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

    def animate(self):
        """Animate particle then kill"""
        self.frame_index += self.animation_speed

        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self) -> None:
        self.animate()
