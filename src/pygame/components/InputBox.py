import logging
from dataclasses import dataclass, field
from typing import Optional, Callable, Tuple

import pygame

from src.pygame.components.IComponent import IComponent


@dataclass
class InputBox(IComponent):
    x: int
    y: int
    width: int
    height: int
    text: str = ""
    font_size: int = 20
    color_inactive: Tuple[int, int, int] = (100, 100, 100)
    color_active: Tuple[int, int, int] = (150, 150, 150)
    text_color: Tuple[int, int, int] = (255, 255, 255)
    on_submit: Optional[Callable[[str], None]] = field(default=None, repr=False)

    label: str = ""
    label_color: Tuple[int, int, int] = (255, 255, 255)
    label_padding: int = 5

    font: pygame.font.Font = field(init=False)
    active: bool = field(init=False, default=False)

    def __post_init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont(None, self.font_size)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            within = self.x <= event.pos[0] <= self.x + self.width and self.y <= event.pos[1] <= self.y + self.height
            if within:
                self.active = not self.active
            else:
                self.active = False
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                if self.on_submit is not None:
                    try:
                        self.on_submit(self.text)
                    except Exception as exc:
                        logging.error(f"InputBox submit error: {exc}")
                self.text = ""
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

    def draw(self, surface):
        if self.label:
            label_surf = self.font.render(self.label, True, self.label_color)
            label_pos = (self.x, self.y - label_surf.get_height() - self.label_padding)
            surface.blit(label_surf, label_pos)

        color = self.color_active if self.active else self.color_inactive
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, color, rect, 2)

        txt_surf = self.font.render(self.text, True, self.text_color)
        text_x = self.x + 5
        text_y = self.y + (self.height - txt_surf.get_height()) // 2
        surface.blit(txt_surf, (text_x, text_y))
