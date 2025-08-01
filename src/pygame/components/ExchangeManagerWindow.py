import logging
from dataclasses import field, dataclass
from typing import Optional

import pygame

from src.CiF.BCiF import BCiF
from src.pygame.components.Dropdown import Dropdown
from src.pygame.components.IComponent import IComponent
from src.pygame.components.Column import Column
from src.pygame.components.Button import Button
from src.pygame.components.InputBox import InputBox


@dataclass
class ExchangeManagerWindow(IComponent):
    x: int
    y: int
    width: int
    height: int
    model: BCiF
    visible: bool = False

    font: pygame.font.Font = field(init=False)
    column: Column = field(init=False)
    load_button: Button = field(init=False)
    name_input: InputBox = field(init=False)
    text_input: InputBox = field(init=False)
    close_button: Button = field(init=False)

    selected_index: Optional[int] = field(init=False, default=None)
    on_close: Optional[callable] = field(default=None, repr=False)

    def __post_init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 20)
        self._init_column()
        self._init_buttons()
        self._init_inputs()

        if self.model.actions:
            self.selected_index = 0
            tpl = self.model.actions[self.selected_index]
            self.name_input.text = tpl.name
            self.text_input.text = tpl.text
            try:
                self.intent_dropdown.selected_index = self.model.relationships.index(
                    tpl.intent.subtype
                )
            except ValueError:
                self.intent_dropdown.selected_index = None
        elif self.model.relationships:
            self.intent_dropdown.selected_index = 0

    def _init_column(self):
        self.column_w = self.width // 3
        self.column = Column(
            self.x,
            self.y,
            self.column_w,
            self.height,
            items=[ex.name for ex in self.model.actions],
        )

    def _init_buttons(self):
        btn_w, btn_h = 80, 25
        self.btn_h = btn_h
        column_w = self.column_w
        btn_y = self.y
        top_padding = 10
        self.load_button = Button(
            self.x + column_w + 10,
            btn_y + top_padding,
            btn_w,
            btn_h,
            "Load from YAML",
            on_click=self.load_exchanges,
        )
        close_x = self.x + self.width - btn_w - 10
        self.close_button = Button(
            close_x,
            self.y + 5,
            btn_w,
            btn_h,
            "Close",
            on_click=self.close_window,
        )

    def _init_inputs(self):
        column_w = self.column_w
        input_x = self.x + column_w + 10
        input_w = self.width - column_w - 20

        top_y = self.y + self.height // 2 - 80
        d_btwn = 60
        self.intent_dropdown = Dropdown(
            input_x,
            top_y,
            input_w,
            25,
            options=list(self.model.relationships),
            label="Intent Relationship of Exchange",
        )
        self.refresh_dropdown()
        self.name_input = InputBox(
            input_x,
            top_y + d_btwn,
            input_w,
            25,
            label="Name of Exchange",
        )
        self.text_input = InputBox(
            input_x,
            top_y + d_btwn * 2,
            input_w,
            25,
            label="Text of Exchange (for logging in history tab)",
        )
        self.precond_label_y = top_y + d_btwn * 3

    def load_exchanges(self):
        import os
        from src.social_exchange.exchange_loader import load_exchange_templates

        try:
            root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            path = os.path.join(root, "configs", "exchanges_example.yaml")
            templates = load_exchange_templates(path)
        except Exception as exc:
            logging.error(f"Failed to load exchanges: {exc}")
            return

        self.model.actions = templates
        self.column.items = [ex.name for ex in self.model.actions]
        self.column.recalculate_scroll()

        if self.model.actions:
            self.column.selected_index = 0
            self.selected_index = 0
            tpl = self.model.actions[0]
            self.name_input.text = tpl.name
            self.text_input.text = tpl.text
            try:
                self.intent_dropdown.selected_index = self.model.relationships.index(
                    tpl.intent.subtype
                )
            except ValueError:
                self.intent_dropdown.selected_index = None
        else:
            self.column.selected_index = None
            self.selected_index = None
            self.name_input.text = ""
            self.text_input.text = ""
            self.intent_dropdown.selected_index = None

    def refresh_dropdown(self):
        self.intent_dropdown.options = list(self.model.relationships)
        self.intent_dropdown.scroll_offset = 0
        self.intent_dropdown.selected_index = None if self.intent_dropdown.options is None else (
                self.intent_dropdown.selected_index or 0)

    def close_window(self):
        self.column.selected_index = None
        self.selected_index = None
        self.name_input.text = ""
        self.text_input.text = ""
        self.intent_dropdown.selected_index = None
        if self.on_close:
            self.on_close()

    def handle_event(self, event):
        if not self.visible:
            return
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION, pygame.MOUSEWHEEL):
            mx, my = event.pos if hasattr(event, "pos") else pygame.mouse.get_pos()
            open_dds = []
            if self.intent_dropdown.active:
                open_dds.append(self.intent_dropdown)
            for dd in open_dds:
                if dd.menu_rect().collidepoint(mx, my):
                    dd.handle_event(event)
                    return
        self.column.handle_event(event)
        self.load_button.handle_event(event)
        self.close_button.handle_event(event)

        self.selected_index = self.column.get_selected_index()
        if self.selected_index is not None:
            tpl = self.model.actions[self.selected_index]
            self.name_input.text = tpl.name
            self.text_input.text = tpl.text
            self.intent_dropdown.selected_index = self.model.relationships.index(tpl.intent.subtype) if tpl.intent.subtype in self.model.relationships else None

    def draw(self, surface):
        if not self.visible:
            return
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (40, 40, 40), rect)
        self.column.draw(surface)
        self.load_button.draw(surface)
        self.close_button.draw(surface)
        self.name_input.draw(surface)
        self.text_input.draw(surface)
        self.intent_dropdown.draw(surface)
        open_menus = []
        if self.intent_dropdown.active:
            open_menus.append(self.intent_dropdown)

        for dd in open_menus:
            dd.draw(surface)
