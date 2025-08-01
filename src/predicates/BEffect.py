from dataclasses import dataclass

from src.belief.BeliefStore import BeliefStore
from src.predicates.PredicateTemplate import PredicateTemplate
from src.types.NPCTypes import BNPCType


@dataclass
class IBEffect:
    label: str
    predicate: PredicateTemplate
    probability: float = 1.0

    def __call__(self, state: BeliefStore, i: BNPCType, r: BNPCType) -> None:
        raise NotImplementedError("Effect must implement __call__ method.")


@dataclass
class BAddPredicateEffect(IBEffect):
    label: str
    predicate: PredicateTemplate
    probability: float = 1.0

    def __call__(self, state: BeliefStore, i: BNPCType, r: BNPCType) -> None:
        predicate = self.predicate.instantiate(subject=i, target=r) if not self.predicate.is_single else self.predicate.instantiate(subject=i)
        state.update(predicate, self.probability)

@dataclass
class BRemovePredicateEffect(IBEffect):
    label: str
    predicate: PredicateTemplate
    probability: float = 0.0

    def __call__(self, state: BeliefStore, i: BNPCType, r: BNPCType) -> None:
        predicate = self.predicate.instantiate(subject=i, target=r) if not self.predicate.is_single else self.predicate.instantiate(subject=i)

        state.update(predicate, self.probability)
