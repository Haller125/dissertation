import logging
from dataclasses import dataclass, field
from typing import Optional, List

import pygame

from src.pygame.components.IComponent import IComponent
from src.pygame.components.Column import Column
from src.pygame.components.Button import Button
from src.pygame.components.InputBox import InputBox


@dataclass
class ListManagerWindow(IComponent):
    x: int
    y: int
    width: int
    height: int
    items: List[str]
    visible: bool = False

    font: pygame.font.Font = field(init=False)
    column: Column = field(init=False)
    add_button: Button = field(init=False)
    edit_button: Button = field(init=False)
    delete_button: Button = field(init=False)
    subtype_input: InputBox = field(init=False)
    confirm_button: Button = field(init=False)
    editing: bool = field(init=False, default=False)
    edit_index: Optional[int] = field(init=False, default=None)
    on_close: Optional[callable] = field(default=None, repr=False)
    input_label: str = field(default="Subtype", repr=False)

    def __post_init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 20)
        column_w = self.width // 3
        self.column = Column(self.x, self.y, column_w, self.height,
                             items=list(self.items))
        btn_w, btn_h = 80, 25
        btn_y = self.y
        top_padding = 10
        self.add_button = Button(self.x + column_w + 10, btn_y + top_padding,
                                 btn_w, btn_h,
                                 "Add", on_click=self.start_add)
        self.edit_button = Button(self.x + column_w + 10, btn_y + btn_h + 5 + top_padding,
                                  btn_w, btn_h,
                                  "Edit", on_click=self.start_edit)
        self.delete_button = Button(self.x + column_w + 10, btn_y + 2 * (btn_h + 5) + top_padding,
                                    btn_w, btn_h,
                                    "Delete", on_click=self.delete_selected)
        input_x = self.x + column_w + 10
        input_w = self.width - column_w - 20
        self.subtype_input = InputBox(input_x, self.y + self.height // 2 - 40, input_w, 25,
                                      label=self.input_label)
        self.confirm_button = Button(input_x, self.y + self.height // 2 + 35,
                                     btn_w, btn_h, "OK", on_click=self.confirm_edit)

        close_x = self.x + self.width - btn_w - 10
        self.close_button = Button(close_x, self.y + 5, btn_w, btn_h,
                                   "Close", on_click=self.close_window)

    def start_add(self):
        self.editing = True
        self.edit_index = None
        self.subtype_input.text = ""

    def close_window(self):
        self.editing = False
        self.edit_index = None
        self.column.selected_index = None
        if self.on_close:
            self.on_close()

    def start_edit(self):
        idx = self.column.get_selected_index()
        if idx is None:
            return
        self.editing = True
        self.edit_index = idx
        self.subtype_input.text = self.items[idx]

    def delete_selected(self):
        idx = self.column.get_selected_index()
        if idx is None:
            return
        try:
            del self.items[idx]
        except Exception as exc:
            logging.error(f"Delete item error: {exc}")
        self.column.items = list(self.items)
        self.column.recalculate_scroll()
        self.column.selected_index = None

    def confirm_edit(self):
        name = self.subtype_input.text.strip()
        if not name:
            self.editing = False
            return
        if self.edit_index is None:
            self.items.append(name)
        else:
            self.items[self.edit_index] = name
        self.column.items = list(self.items)
        self.editing = False
        self.column.selected_index = None
        self.column.recalculate_scroll()

    def handle_event(self, event):
        if not self.visible:
            return
        self.column.handle_event(event)
        self.add_button.handle_event(event)
        self.edit_button.handle_event(event)
        self.delete_button.handle_event(event)
        self.close_button.handle_event(event)
        if self.editing:
            self.subtype_input.handle_event(event)
            self.confirm_button.handle_event(event)

    def draw(self, surface):
        if not self.visible:
            return
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (40, 40, 40), rect)
        self.column.draw(surface)
        self.add_button.draw(surface)
        self.edit_button.draw(surface)
        self.delete_button.draw(surface)
        self.close_button.draw(surface)
        if self.editing:
            self.subtype_input.draw(surface)
            self.confirm_button.draw(surface)
