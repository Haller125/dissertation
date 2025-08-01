import logging
from dataclasses import dataclass

from src.belief.BeliefStore import BeliefStore
from src.predicates.PredicateTemplate import PredicateTemplate


@dataclass
class IBCondition:
    req_predicate: PredicateTemplate

    def __call__(self, state: BeliefStore, i, r=None) -> bool:
        raise NotImplementedError("Subclasses should implement this method.")

    @staticmethod
    def get_type() -> str:
        raise NotImplementedError("Subclasses should implement this method.")


@dataclass
class BHasCondition(IBCondition):
    req_predicate: PredicateTemplate

    def __call__(self, state: BeliefStore, i, r=None) -> float:
        if not self.req_predicate:
            logging.error("Condition is empty.")
            return False
        return state.get_probability(self.req_predicate, i, r)

    @staticmethod
    def get_type():
        return f"Has"


@dataclass
class BHasNotCondition(IBCondition):
    req_predicate: PredicateTemplate

    def __call__(self, state: BeliefStore, i, r=None) -> float:
        if not self.req_predicate:
            logging.error("Condition is empty.")
            return False
        return 1.0 - state.get_probability(self.req_predicate, i, r)

    @staticmethod
    def get_type():
        return f"Has not"


# This class is used to represent a constant condition that always returns the same value. For tests
class BConstantCondition(IBCondition):
    def __init__(self, value: float):
        super().__init__(req_predicate=PredicateTemplate("trait", "constant", True))
        self.value = value

    def __call__(self, *args, **kwargs) -> float:
        return self.value

    def get_type(self) -> str:
        return f"Const"
