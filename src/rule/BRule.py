import math
from dataclasses import dataclass, field
from typing import Sequence

from src.belief.BeliefStore import BeliefStore
from src.predicates.BCondition import IBCondition
from src.predicates.BEffect import IBEffect
from src.types.NPCTypes import BNPCType


@dataclass
class BRule:
    name: str
    condition: Sequence[IBCondition]
    weight: float
    effects: Sequence[IBEffect] = field(default_factory=list)

    def probability(self, beliefs: BeliefStore, i: BNPCType, r: BNPCType = None) -> float:
        if not self.condition:
            raise ValueError(f"Rule '{self.name}' has no conditions.")

        cond_probs = [float(cond(beliefs, i, r)) for cond in self.condition]
        if any(p < 0 or p > 1 for p in cond_probs):
            raise ValueError("Condition probabilities must be within [0,1].")

        prob = math.prod(cond_probs)
        return prob
