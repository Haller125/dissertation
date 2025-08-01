import pygame
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from src.CiF.BCiF import BCiF
from src.predicates.PredicateTemplate import PredicateTemplate
from src.pygame.components.IComponent import IComponent
from src.pygame.components.Dropdown import Dropdown


@dataclass
class PreconditionEditor(IComponent):
    x: int
    y: int
    width: int
    model: BCiF
    get_selected_index: Callable[[], Optional[int]]
    set_confirm_y: Callable[[int], None]
    font: pygame.font.Font = field(init=False)
    dropdowns: List[Tuple[Dropdown, Dropdown]] = field(init=False, default_factory=list)
    base_y: int = field(init=False)
    scroll_offset: int = field(init=False, default=0)
    label: str = "Preconditions"

    PRECOND_TYPES = ["Has", "Has not", "Const"]

    def __post_init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 20)
        self.base_y = self.y

    def _predicate_options(self) -> List[str]:
        return [f"trait:{t}" for t in self.model.traits] + [f"relationship:{r}" for r in self.model.relationships]

    def refresh(self):
        self.dropdowns.clear()
        idx = self.get_selected_index()
        if idx is None:
            return
        tpl = self.model.actions[idx]
        start_y = self.y
        height = 25
        spacing = 5
        type_w = 100
        pred_w = self.width - type_w - 10
        x_type = self.x
        x_pred = x_type + type_w + 5

        options_pred = self._predicate_options()

        for i, cond in enumerate(tpl.preconditions):
            dd_type = Dropdown(
                x_type,
                start_y + i * (height + spacing),
                type_w,
                height,
                options=list(self.PRECOND_TYPES),
                on_select=self._make_type_handler(i),
            )
            cond_type = cond.get_type()
            if cond_type in self.PRECOND_TYPES:
                dd_type.selected_index = self.PRECOND_TYPES.index(cond_type)

            dd_pred = Dropdown(
                x_pred,
                start_y + i * (height + spacing),
                pred_w,
                height,
                options=list(options_pred),
                on_select=self._make_pred_handler(i),
            )
            pred_str = f"{cond.req_predicate.pred_type}:{cond.req_predicate.subtype}"
            if pred_str in options_pred:
                dd_pred.selected_index = options_pred.index(pred_str)

            self.dropdowns.append((dd_type, dd_pred))

        ok_y = start_y + len(tpl.preconditions) * (height + spacing) + 5
        self.set_confirm_y(ok_y)

    def set_scroll(self, offset: int):
        self.scroll_offset = offset
        self.y = self.base_y - offset
        self.refresh()

    def get_active_dropdowns(self) -> List[Dropdown]:
        active: List[Dropdown] = []
        for d_t, d_p in self.dropdowns:
            if d_t.active:
                active.append(d_t)
            if d_p.active:
                active.append(d_p)
        return active

    def handle_event(self, event):
        for d_t, d_p in self.dropdowns:
            d_t.handle_event(event)
            d_p.handle_event(event)

    def draw(self, surface, editing: bool = False):
        if not self.dropdowns or self.get_selected_index() is None:
            return []
        label_surf = self.font.render(self.label, True, (255, 255, 255))
        surface.blit(label_surf, (self.x, self.y - 20))
        active: List[Dropdown] = []
        for d_t, d_p in self.dropdowns:
            d_t.draw(surface)
            d_p.draw(surface)
            if editing:
                if d_t.active:
                    active.append(d_t)
                if d_p.active:
                    active.append(d_p)
        return active

    def _make_type_handler(self, idx: int):
        def handler(selection: str):
            sel = self.get_selected_index()
            if sel is None:
                return
            tpl = self.model.actions[sel]
            pred = tpl.preconditions[idx].req_predicate
            if selection == "Has":
                from src.predicates.BCondition import BHasCondition

                tpl.preconditions[idx] = BHasCondition(pred)
            elif selection == "Has not":
                from src.predicates.BCondition import BHasNotCondition

                tpl.preconditions[idx] = BHasNotCondition(pred)
            else:
                from src.predicates.BCondition import BConstantCondition

                val = 1.0
                if hasattr(tpl.preconditions[idx], "value"):
                    val = tpl.preconditions[idx].value
                tpl.preconditions[idx] = BConstantCondition(val)

        return handler

    def _make_pred_handler(self, idx: int):
        def handler(selection: str):
            sel = self.get_selected_index()
            if sel is None:
                return
            tpl = self.model.actions[sel]
            pred_type, subtype = selection.split(":", 1)
            tpl.preconditions[idx].req_predicate = PredicateTemplate(
                pred_type, subtype, False
            )

        return handler
