from dataclasses import dataclass
from typing import Sequence

from src.belief.BeliefStore import BeliefStore
from src.predicates.BEffect import IBEffect
from src.types.NPCTypes import BNPCType

@dataclass
class BExchangeEffects:
    accept_effects: Sequence[IBEffect]
    reject_effects: Sequence[IBEffect]

    def accept(self, state: BeliefStore, i: BNPCType, r: BNPCType) -> None:
        for effect in self.accept_effects:
            effect(state, i, r)

    def reject(self, state: BeliefStore, i: BNPCType, r: BNPCType) -> None:
        for effect in self.reject_effects:
            effect(state, i, r)
