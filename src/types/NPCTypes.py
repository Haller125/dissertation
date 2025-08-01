from __future__ import annotations

from typing import Protocol, Sequence, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.belief.BeliefStore import BeliefStore
    from src.desire_formation.BVolition import BVolition
    from src.social_exchange.BSocialExchange import BSocialExchange
    from src.social_exchange.BSocialExchangeTemplate import BSocialExchangeTemplate


class NPCType(Protocol):
    id: int
    name: str


class BNPCType(Protocol):
    id: int
    name: str
    beliefStore: BeliefStore

    def perform_action(self, action: BSocialExchange):
        raise NotImplementedError

    def desire_formation(self, targets: Sequence[BNPCType], actions_templates: Sequence[BSocialExchangeTemplate]) -> \
            List[BVolition]:
        raise NotImplementedError

    def select_intent(self, volitions: Sequence[BVolition], threshold: float = 0.0) -> Optional[BSocialExchange]:
        raise NotImplementedError

    def update_beliefs_from_observation(self, actions_done: Sequence[BSocialExchange]) -> None:
        raise NotImplementedError

    def iteration(self, targets: Sequence[BNPCType], actions_templates: Sequence[BSocialExchangeTemplate]):
        raise NotImplementedError
