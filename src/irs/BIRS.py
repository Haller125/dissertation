from dataclasses import dataclass, field
from typing import List

from src.belief.BeliefStore import BeliefStore
from src.rule.BRule import BRule
from src.types.NPCTypes import BNPCType
from src.utils.sigmoid import sigmoid


@dataclass(slots=True)
class BInfluenceRuleSet:
    name: str
    rules: List[BRule] = field(default_factory=list)

    def expected_value(self, beliefs: BeliefStore, i: BNPCType, r: BNPCType) -> float:
        # E w_i · P(condition_i)
        return sum(rule.weight * rule.probability(beliefs, i, r) for rule in self.rules)

    def acceptance_probability(self, beliefs: BeliefStore, i: BNPCType, r: BNPCType,
                               bias: float = 0.0) -> float:
        s = self.expected_value(beliefs, i, r)
        return sigmoid(x=s, bias=bias)

    def add(self, *new_rules: BRule) -> None:
        self.rules.extend(new_rules)
