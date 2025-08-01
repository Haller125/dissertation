from src.CiF.BCiF import BCiF
from src.pygame.components.ListManagerWindow import ListManagerWindow


class TraitsManagerWindow(ListManagerWindow):
    def __init__(self, x: int, y: int, width: int, height: int, model: BCiF, visible: bool = False, on_close=None, input_label: str = "Trait Type"):
        self.model = model
        super().__init__(x, y, width, height, model.traits, visible, on_close, input_label)
