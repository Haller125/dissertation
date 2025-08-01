import logging
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Callable

import pygame

from src.pygame.components.IComponent import IComponent


@dataclass
class Dropdown(IComponent):
    x: int
    y: int
    width: int
    height: int
    options: List[str]
    font_size: int = 20
    color_inactive: Tuple[int, int, int] = (100, 100, 100)
    color_active: Tuple[int, int, int] = (150, 150, 150)
    highlight_color: Tuple[int, int, int] = (70, 70, 120)
    text_color: Tuple[int, int, int] = (255, 255, 255)
    max_visible: int = 5
    on_select: Optional[Callable[[str], None]] = field(default=None, repr=False)

    font: pygame.font.Font = field(init=False)
    active: bool = field(init=False, default=False)
    scroll_offset: int = field(init=False, default=0)
    selected_index: Optional[int] = field(init=False, default=None)

    label: str = ""
    label_color: Tuple[int, int, int] = (255, 255, 255)
    label_padding: int = 5

    def __post_init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont(None, self.font_size)
        self.item_height = self.font.get_height() + 4

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            main_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            list_rect = pygame.Rect(
                self.x,
                self.y + self.height,
                self.width,
                self.item_height * min(len(self.options), self.max_visible),
            )

            # handle scroll while the list is open
            if self.active and event.button in (4, 5) and list_rect.collidepoint(mx, my):
                max_scroll = max(
                    0,
                    self.item_height * len(self.options)
                    - self.item_height * self.max_visible,
                )
                step = self.item_height
                if event.button == 4:
                    self.scroll_offset = max(0, self.scroll_offset - step)
                else:
                    self.scroll_offset = min(max_scroll, self.scroll_offset + step)
                return

            if main_rect.collidepoint(mx, my):
                self.active = not self.active
                return

            if self.active and list_rect.collidepoint(mx, my):
                rel_y = my - list_rect.y + self.scroll_offset
                idx = rel_y // self.item_height
                if 0 <= idx < len(self.options):
                    self.selected_index = idx
                    if self.on_select:
                        try:
                            self.on_select(self.options[idx])
                        except Exception as exc:
                            logging.error(f"Dropdown on_select error: {exc}")
                self.active = False
            else:
                self.active = False

        elif event.type == pygame.MOUSEWHEEL and self.active:
            list_rect = pygame.Rect(
                self.x,
                self.y + self.height,
                self.width,
                self.item_height * min(len(self.options), self.max_visible),
            )
            mx, my = pygame.mouse.get_pos()
            if list_rect.collidepoint(mx, my):
                max_scroll = max(
                    0,
                    self.item_height * len(self.options)
                    - self.item_height * self.max_visible,
                )
                step = self.item_height * -event.y
                new_offset = self.scroll_offset + step
                new_offset = max(0, min(max_scroll, new_offset))
                self.scroll_offset = new_offset

    def menu_rect(self) -> pygame.Rect:
        height = self.item_height * min(len(self.options), self.max_visible)
        return pygame.Rect(self.x, self.y + self.height, self.width, height)

    def draw(self, surface: pygame.Surface):
        main_color = self.color_active if self.active else self.color_inactive
        main_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, main_color, main_rect, 2)

        text = self.options[self.selected_index] if self.selected_index is not None else ""
        txt_surf = self.font.render(text, True, self.text_color)
        surface.blit(txt_surf, (self.x + 5, self.y + (self.height - txt_surf.get_height()) // 2))

        if self.label:
            label_surf = self.font.render(self.label, True, self.label_color)
            label_pos = (self.x, self.y - label_surf.get_height() - self.label_padding)
            surface.blit(label_surf, label_pos)

        if self.active:
            list_height = self.item_height * min(len(self.options), self.max_visible)
            list_rect = pygame.Rect(self.x, self.y + self.height, self.width, list_height)
            pygame.draw.rect(surface, self.color_inactive, list_rect)
            surface.set_clip(list_rect)
            y = self.y + self.height - self.scroll_offset
            for idx, option in enumerate(self.options):
                item_rect = pygame.Rect(self.x, y, self.width, self.item_height)
                if item_rect.bottom > self.y + self.height and item_rect.top < list_rect.bottom:
                    bg = self.highlight_color if idx == self.selected_index else self.color_inactive
                    pygame.draw.rect(surface, bg, item_rect)
                    txt = self.font.render(option, True, self.text_color)
                    surface.blit(txt, (item_rect.x + 5, item_rect.y + 2))
                y += self.item_height
            surface.set_clip(None)
