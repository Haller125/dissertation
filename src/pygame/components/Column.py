from dataclasses import dataclass, field
from typing import List, Tuple, Optional

import pygame

from src.pygame.components.IComponent import IComponent


@dataclass
class Column(IComponent):
    x: int
    y: int
    width: int
    height: int
    items: List[str]
    exclude_items: List[str] = field(default_factory=list)
    bg_color: Tuple[int, int, int] = (30, 30, 30)
    text_color: Tuple[int, int, int] = (255, 255, 255)
    selected_color: Tuple[int, int, int] = (70, 70, 120)
    padding: int = 5
    line_height: int = 20
    font: pygame.font.Font = field(init=False)
    scroll_offset: int = field(init=False, default=0)
    max_scroll: int = field(init=False, default=0)
    selected_index: Optional[int] = field(init=False, default=None)
    disabled: bool = field(init=False, default=False)

    def __post_init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont(None, self.line_height)
        render_items = [item for item in self.items if item not in self.exclude_items]
        total = len(render_items) * (self.line_height + self.padding)
        self.max_scroll = max(0, total - self.height)

    def recalculate_scroll(self):
        render_items = [item for item in self.items if item not in self.exclude_items]
        total = len(render_items) * (self.line_height + self.padding)
        self.max_scroll = max(0, total - self.height)
        self.scroll_offset = min(self.scroll_offset, self.max_scroll)

    def handle_event(self, event):
        if self.disabled:
            return
        mx, my = pygame.mouse.get_pos()
        in_col = self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in (4, 5) and in_col:
                step = self.line_height + self.padding
                self.scroll_offset = max(0, min(self.max_scroll,
                                                self.scroll_offset + (step if event.button == 5 else -step)))
            elif event.button == 1 and in_col:
                # calculate index in filtered list
                rel_y = my - self.y + self.scroll_offset - self.padding
                idx = rel_y // (self.line_height + self.padding)
                # build filtered list
                render_items = [item for item in self.items if item not in self.exclude_items]
                if 0 <= idx < len(render_items):
                    # find original index
                    item = render_items[idx]
                    orig_idx = self.items.index(item)
                    self.selected_index = orig_idx if self.selected_index != orig_idx else None

    def draw(self, surface):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.bg_color, rect)
        surface.set_clip(rect)
        y_off = self.y - self.scroll_offset + self.padding
        render_items = [item for item in self.items if item not in self.exclude_items]

        for item in render_items:
            i = self.items.index(item)
            item_rect = pygame.Rect(self.x + self.padding, y_off,
                                    self.width - 2 * self.padding, self.line_height)
            col = self.selected_color if i == self.selected_index else self.bg_color
            pygame.draw.rect(surface, col, item_rect)
            txt = self.font.render(str(item), True, self.text_color)
            surface.blit(txt, (item_rect.x + 5, item_rect.y))
            y_off += self.line_height + self.padding
        surface.set_clip(None)

    def get_selected_index(self):
        if self.selected_index is None:
            return None
        return self.selected_index if self.items[self.selected_index] not in self.exclude_items else None
