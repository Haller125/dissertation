from dataclasses import dataclass


@dataclass
class IComponent:

    def handle_event(self, event):
        raise NotImplementedError("handle_event must be implemented by subclasses")

    def draw(self, surface):
        raise NotImplementedError("draw must be implemented by subclasses")
