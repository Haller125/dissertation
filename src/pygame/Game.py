from dataclasses import dataclass, field
from typing import List

import pygame

from src.CiF.BCiF import BCiF
from src.npc.BNPC import BNPC
from src.pygame import MainWindow
from src.pygame.components.Button import Button
from src.pygame.components.Column import Column
from src.pygame.components.ExchangeManagerWindow import ExchangeManagerWindow
from src.pygame.components.RelationshipsManagerWindow import RelationshipsManagerWindow

from src.pygame.components.TabWindow import TabWindow
from src.pygame.components.TopBar import TopBar
from src.pygame.components.TraitsManagerWindow import TraitsManagerWindow
from src.social_exchange.BSocialExchange import BSocialExchange
from src.social_exchange.BSocialExchangeTemplate import BSocialExchangeTemplate


@dataclass
class Game:
    model: BCiF
    npcs: List = None
    actions: List[BSocialExchangeTemplate] = None
    traits: List[str] = None
    relationships: List[str] = None

    left_column: Column = None
    left_column_exclude_items: List = field(default_factory=list)
    right_column: Column = None
    right_column_exclude_items: List = field(default_factory=list)

    mid_window: TabWindow = None
    traits_manager: TraitsManagerWindow = None
    relationships_manager: RelationshipsManagerWindow = None
    exchange_manager: ExchangeManagerWindow = None

    overlapping_windows: List = field(default_factory=list)
    main_window_components: List = field(default_factory=list)

    checking_beliefs: BNPC | None = None

    def __post_init__(self):
        self.npcs = self.model.NPCs
        self.actions = self.model.actions
        self.traits = self.model.traits
        self.relationships = self.model.relationships

        self.window = MainWindow.GameWindow()
        topbar = TopBar(width=self.window.width, height=self.window.height // 5)
        btn_w, btn_h = 80, topbar.height - 10
        spacing = 10
        num_buttons = 6
        x_start = topbar.width - (btn_w * num_buttons + spacing * (num_buttons + 3))
        buttons = [

            Button(x=x_start + spacing, y=5, width=btn_w, height=btn_h, text="Check Beliefs about others", on_click=self.toggle_checking_beliefs),
            Button(x=x_start + 2 * spacing + btn_w, y=5, width=btn_w, height=btn_h, text="Next iteration", on_click=self.next_iteration),
            Button(x=x_start + 3 * spacing + 2 * btn_w, y=5, width=btn_w, height=btn_h, text="Traits", on_click=self.toggle_traits_manager),
            Button(x=x_start + 4 * spacing + 3 * btn_w, y=5, width=btn_w, height=btn_h, text="Relationships", on_click=self.toggle_relationships_manager),
            Button(x=x_start + 5 * spacing + 4 * btn_w, y=5, width=btn_w, height=btn_h, text="Exchanges",
                   on_click=self.toggle_exchange_manager),
            Button(x=x_start + 6 * spacing + 5 * btn_w, y=5, width=btn_w, height=btn_h, text="Save",
                   on_click=self.save_prompt)
        ]
        topbar.buttons = buttons
        self.window.add_object(topbar)

        # Left column
        content_y = topbar.height
        content_h = self.window.height - topbar.height
        column_left = Column(
            x=0,
            y=content_y,
            width=self.window.width // 4,
            height=content_h,
            items=self.npcs,
            exclude_items= self.left_column_exclude_items,
        )
        self.left_column = column_left
        self.window.add_object(column_left)

        # Right column
        column_right = Column(
            x=self.window.width - self.window.width // 4,
            y=content_y,
            width=self.window.width // 4,
            height=content_h,
            items=self.npcs,
            exclude_items=self.npcs.copy(),
        )
        self.right_column = column_right
        self.window.add_object(column_right)

        mid = TabWindow(x=self.window.width // 4, y=content_y,
                        width=self.window.width // 2, height=content_h,
                        tabs=['History', 'Traits', 'Relationships'],
                        get_data_for_tab=self.get_data_for_mid_window)
        self.window.add_object(mid)
        self.mid_window = mid

        traits_manager = TraitsManagerWindow(
            x=self.window.width // 8,
            y=self.window.height // 8,
            width=self.window.width * 3 // 4,
            height=self.window.height * 3 // 4,
            model=self.model,
            on_close=lambda: self.toggle_traits_manager()
        )
        self.traits_manager = traits_manager
        self.window.add_object(traits_manager)

        relations_manager = RelationshipsManagerWindow(
            x=self.window.width // 8,
            y=self.window.height // 8,
            width=self.window.width * 3 // 4,
            height=self.window.height * 3 // 4,
            model=self.model,
            on_close=lambda: self.toggle_relationships_manager()
        )
        self.relationships_manager = relations_manager
        self.window.add_object(relations_manager)

        exchange_manager = ExchangeManagerWindow(
            x=self.window.width // 8,
            y=self.window.height // 8,
            width=self.window.width * 3 // 4,
            height=self.window.height * 3 // 4,
            model=self.model,
            on_close=lambda: self.toggle_exchange_manager(),
        )
        self.exchange_manager = exchange_manager
        self.window.add_object(exchange_manager)

        # Kind of different windows
        self.overlapping_windows.append(traits_manager)
        self.overlapping_windows.append(relations_manager)
        self.overlapping_windows.append(exchange_manager)

        # Main window components
        self.main_window_components.append(topbar)
        self.main_window_components.append(column_left)
        self.main_window_components.append(column_right)
        self.main_window_components.append(mid)

    def run(self):
        self.window.running = True
        while self.window.running:
            self.update_state()
            self.window.running_step()
        pygame.quit()

    def update_state(self):
        selected_left = self.get_left_column_selection()
        selected_right = self.get_right_column_selection()

        if selected_left is None:
            self.right_column.exclude_items = self.npcs if self.checking_beliefs is None else [self.npcs, self.checking_beliefs]
            self.mid_window.disable()
        else:
            self.right_column.exclude_items = [selected_left] if self.checking_beliefs is None else [selected_left, self.checking_beliefs]
            self.mid_window.enable()
            if selected_right is None:
                self.mid_window.disable_tab(0)
                self.mid_window.disable_tab(2)
            else:
                self.mid_window.enable_all_tabs()

    def next_iteration(self):
        self.model.iteration()

    def toggle_traits_manager(self):
        self.toggle_helper(self.traits_manager)

    def toggle_relationships_manager(self):
        self.toggle_helper(self.relationships_manager)

    def toggle_exchange_manager(self):
        self.exchange_manager.refresh_dropdown()
        self.toggle_helper(self.exchange_manager)

    def toggle_helper(self, window):
        window.visible = not window.visible
        for w in self.overlapping_windows:
            if w != window:
                w.visible = False
        if self.check_is_main_available():
            for w in self.main_window_components:
                w.disabled = False
        else:
            for w in self.main_window_components:
                w.disabled = True

    def save_prompt(self) -> None:
        import os
        import tkinter as tk
        from tkinter import filedialog, messagebox

        root = tk.Tk()
        root.withdraw()
        saves_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "saves")
        os.makedirs(saves_dir, exist_ok=True)
        path = filedialog.asksaveasfilename(
            initialdir=saves_dir,
            defaultextension=".sav",
            title="Save Game"
        )
        root.destroy()
        if not path:
            return
        try:
            self.save(path)
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to save game: {exc}")

    def check_is_main_available(self):
        res = [not window.visible for window in self.overlapping_windows]

        return all(res)

    def get_left_column_selection(self):
        selected_index = self.left_column.get_selected_index()
        if selected_index is None:
            return None
        return self.left_column.items[selected_index]

    def get_right_column_selection(self):
        selected_index = self.right_column.get_selected_index()
        if selected_index is None:
            return None
        return self.right_column.items[selected_index]

    def get_traits(self):
        npc: BNPC = self.get_left_column_selection()

        beliefs = npc.get_traits() if self.checking_beliefs is None else self.checking_beliefs.beliefStore.get_traits_about(npc)
        data = [(f"{belief.predicate.subtype}", belief.probability) for belief in beliefs]
        return data

    def get_relationships(self):
        subject: BNPC = self.get_left_column_selection()
        target: BNPC = self.get_right_column_selection()

        beliefs = subject.get_relationships(subject, target) if self.checking_beliefs is None else self.checking_beliefs.beliefStore.get_relationships_about(subject, target)
        data = [(f"{belief.predicate.subtype}", belief.probability) for belief in beliefs]
        return data

    def get_history(self):
        subject: BNPC = self.get_left_column_selection()
        target: BNPC = self.get_right_column_selection()

        exchanges: List[BSocialExchange] = self.model.get_exchanges(subject, target) if self.checking_beliefs is None else []

        exchanges.reverse()

        return [f"{exchange.initiator} {exchange.text} {exchange.responder}" for exchange in exchanges]

    def get_data_for_mid_window(self, i: int):
        match i:
            case 0:
                if self.get_left_column_selection() is None:
                    return []
                return self.get_history()
            case 1:
                if self.get_left_column_selection() is None:
                    return []
                return self.get_traits()
            case 2:
                if self.get_left_column_selection() is None or self.get_right_column_selection() is None:
                    return []
                return self.get_relationships()

    def save(self, path: str) -> None:
        from src.save_system.save_system import save_model
        save_model(self.model, path)

    @staticmethod
    def load(path: str) -> 'Game':
        from src.save_system.save_system import load_model
        model = load_model(path)
        return Game(model)

    def toggle_checking_beliefs(self):

        if self.checking_beliefs is not None:
            self.checking_beliefs = None
            self.npcs = self.model.NPCs
            self.left_column.exclude_items = []
            return

        npc = self.get_left_column_selection()

        if npc is not None:
            self.checking_beliefs = npc
            self.left_column.exclude_items = [npc]
            self.left_column_exclude_items.append(npc)
