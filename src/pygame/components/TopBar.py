from dataclasses import dataclass, field
from typing import Tuple, List

import pygame

from src.pygame.components.Button import Button
from src.pygame.components.IComponent import IComponent


@dataclass
class TopBar(IComponent):
    width: int
    height: int = 40
    color: Tuple[int, int, int] = (50, 50, 50)
    text_color: Tuple[int, int, int] = (255, 255, 255)

    font: pygame.font.Font = field(init=False)
    buttons: List[Button] = field(default_factory=list)
    disabled: bool = field(init=False, default=False)

    def __post_init__(self):
        pygame.font.init()
        font_size = max(12, self.height - 10)
        self.font = pygame.font.SysFont(None, font_size)
        btn_w, btn_h = 80, self.height - 10
        spacing = 10
        x_start = self.width - (btn_w * 2 + spacing * 3)
        self.buttons = [
            Button(x=x_start + spacing, y=5, width=btn_w, height=btn_h, text="Home"),
            Button(x=x_start + 2 * spacing + btn_w, y=5, width=btn_w, height=btn_h, text="Next iteration"),
            # Button(x=spacing, y=5, width=btn_w, height=btn_h, text="Braincheck")
        ]

    def draw(self, surface: pygame.Surface):
        rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(surface, self.color, rect)
        for btn in self.buttons:
            btn.draw(surface)

    def handle_event(self, event: pygame.event.Event):
        if self.disabled:
            return
        for btn in self.buttons:
            btn.handle_event(event)
