from dataclasses import dataclass, field
from typing import List

import pygame

from src.pygame.components.IComponent import IComponent


@dataclass
class GameWindow:
    width: int = 800
    height: int = 600
    title: str = "PyGame Window"
    background_color: tuple = field(default_factory=lambda: (0, 0, 0))
    fps: int = 60
    objects: List[IComponent] = field(default_factory=list)

    # Runtime attributes initialized later
    screen: pygame.Surface = field(init=False)
    clock: pygame.time.Clock = field(init=False)
    running: bool = field(init=False, default=False)

    def __post_init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        self.clock = pygame.time.Clock()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            for obj in self.objects:
                obj.handle_event(event)

    def update(self):
        pass

    def draw(self):
        self.screen.fill(self.background_color)
        for obj in self.objects:
            obj.draw(self.screen)

        pygame.display.flip()

    def run(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        pygame.quit()

    def running_step(self):
        self.handle_events()
        self.update()
        self.draw()
        self.clock.tick(self.fps)

    def add_object(self, obj: IComponent):
        self.objects.append(obj)


