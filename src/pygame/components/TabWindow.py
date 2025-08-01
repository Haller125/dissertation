import logging

from src.pygame.components.IComponent import IComponent

from dataclasses import dataclass, field
from typing import List, Tuple, Set, Callable, Optional
import pygame


@dataclass
class TabWindow(IComponent):
    x: int
    y: int
    width: int
    height: int
    tabs: List[str]
    header_height: int = 30

    bg_color: Tuple[int, int, int] = (40, 40, 40)
    tab_color: Tuple[int, int, int] = (60, 60, 60)
    selected_tab_color: Tuple[int, int, int] = (80, 80, 120)
    text_color: Tuple[int, int, int] = (255, 255, 255)

    disabled: bool = False
    disabled_bg_color: Tuple[int, int, int] = (80, 80, 80)
    disabled_tab_color: Tuple[int, int, int] = (100, 100, 100)
    disabled_selected_tab_color: Tuple[int, int, int] = (120, 120, 140)
    disabled_text_color: Tuple[int, int, int] = (180, 180, 180)

    disabled_tabs: Set[int] = field(default_factory=set)
    tab_disabled_color: Tuple[int, int, int] = (90, 90, 90)
    tab_disabled_text_color: Tuple[int, int, int] = (160, 160, 160)

    # get_data_for_tab now returns a list of (message, probability) tuples
    # probability can be None
    get_data_for_tab: Callable[[int], List[Tuple[str, Optional[float]]]] = field(
        default_factory=lambda: (lambda idx: []))

    scroll_speed: int = 3

    font: pygame.font.Font = field(init=False)
    selected_index: int = field(init=False, default=0)
    scroll_offset: int = field(init=False, default=0)

    def __post_init__(self):
        pygame.font.init()
        font_size = max(14, self.header_height - 10)
        self.font = pygame.font.SysFont(None, font_size)
        self._coerce_selected_index()

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False

    def disable_tab(self, idx: int):
        if 0 <= idx < len(self.tabs):
            self.disabled_tabs.add(idx)
            self._coerce_selected_index()

    def enable_tab(self, idx: int):
        if 0 <= idx < len(self.tabs):
            self.disabled_tabs.discard(idx)
            if self.selected_index not in range(len(self.tabs)) or self.selected_index in self.disabled_tabs:
                self.selected_index = idx
                self.scroll_offset = 0

    def enable_all_tabs(self):
        self.disabled_tabs.clear()
        self._coerce_selected_index()

    def toggle_tab_disabled(self, idx: int):
        if 0 <= idx < len(self.tabs):
            if idx in self.disabled_tabs:
                self.enable_tab(idx)
            else:
                self.disable_tab(idx)

    def is_tab_disabled(self, idx: int) -> bool:
        return idx in self.disabled_tabs

    def _coerce_selected_index(self):
        if self.selected_index in self.disabled_tabs or not (0 <= self.selected_index < len(self.tabs)):
            for i in range(len(self.tabs)):
                if i not in self.disabled_tabs:
                    self.selected_index = i
                    self.scroll_offset = 0
                    return
            self.selected_index = -1
            self.scroll_offset = 0

    def handle_event(self, event):
        if self.disabled:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            if self.y <= my <= self.y + self.header_height and self.x <= mx <= self.x + self.width:
                tab_w = self.width / len(self.tabs)
                idx = int((mx - self.x) // tab_w)
                if 0 <= idx < len(self.tabs) and idx not in self.disabled_tabs:
                    if idx != self.selected_index:
                        self.selected_index = idx
                        self.scroll_offset = 0

        elif event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if (self.x <= mx <= self.x + self.width and
                    self.y + self.header_height <= my <= self.y + self.height):
                self.scroll_offset -= event.y * self.scroll_speed
                if self.scroll_offset < 0:
                    self.scroll_offset = 0

    def draw(self, surface):
        bg = self.disabled_bg_color if self.disabled else self.bg_color
        tab_c_default = self.disabled_tab_color if self.disabled else self.tab_color
        tab_c_selected = self.disabled_selected_tab_color if self.disabled else self.selected_tab_color
        txt_default = self.disabled_text_color if self.disabled else self.text_color

        pygame.draw.rect(surface, bg, pygame.Rect(self.x, self.y, self.width, self.height))
        tab_w = self.width / len(self.tabs)
        for i, tab in enumerate(self.tabs):
            hdr_rect = pygame.Rect(self.x + i * tab_w, self.y, tab_w, self.header_height)
            if i in self.disabled_tabs or self.disabled:
                base_c = self.tab_disabled_color
                txt_c = self.tab_disabled_text_color
            else:
                base_c = tab_c_selected if i == self.selected_index else tab_c_default
                txt_c = txt_default
            pygame.draw.rect(surface, base_c, hdr_rect)
            txt_surf = self.font.render(tab, True, txt_c)
            txt_rect = txt_surf.get_rect(center=hdr_rect.center)
            surface.blit(txt_surf, txt_rect)

        content_rect = pygame.Rect(
            self.x, self.y + self.header_height, self.width, self.height - self.header_height)
        pygame.draw.rect(surface, bg, content_rect)

        data: List[Tuple[str, Optional[float]]] = []
        if callable(self.get_data_for_tab) and self.selected_index >= 0:
            try:
                data = self.get_data_for_tab(self.selected_index)
            except Exception:
                logging.error(f'Error during the getting data for middle window: {Exception}')
                data = []

        line_height = self.font.get_linesize()
        max_lines = content_rect.height // line_height

        max_offset = max(0, len(data) - max_lines)
        if self.scroll_offset > max_offset:
            self.scroll_offset = max_offset

        start = self.scroll_offset
        end = start + max_lines
        visible_data = data[start:end]

        y_offset = content_rect.y + 5
        for i, item in enumerate(visible_data):
            if isinstance(item, tuple):
                msg, prob = item
            else:
                msg, prob = str(item), None

            msg_text = str(msg)
            prob_text = "" if prob is None else f"{prob:.2f}"

            msg_surf = self.font.render(msg_text, True, txt_default)
            surface.blit(msg_surf, (content_rect.x + 5, y_offset + i * line_height))

            if prob_text:
                prob_surf = self.font.render(prob_text, True, txt_default)
                prob_rect = prob_surf.get_rect()
                prob_x = content_rect.x + self.width - prob_rect.width - 5
                surface.blit(prob_surf, (prob_x, y_offset + i * line_height))
