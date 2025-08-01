from dataclasses import dataclass, field
from typing import List, Dict, Tuple

from src.belief.Belief import Belief
from src.predicates.Predicate import Predicate
from src.predicates.PredicateTemplate import PredicateTemplate
from src.types.NPCTypes import BNPCType


@dataclass
class BeliefStore:
    beliefs: List[Belief] = field(default_factory=list)

    def __post_init__(self):
        self._belief_index: Dict[Tuple[str, str, bool, int, int | None], Belief] = {}
        for belief in self.beliefs:
            key = self._key_from_predicate(belief.predicate)
            self._belief_index[key] = belief

    @staticmethod
    def _key_from_template(template: PredicateTemplate, subject: BNPCType, target: BNPCType | None) -> Tuple[str, str, bool, int, int | None]:
        return (
            template.pred_type,
            template.subtype,
            template.is_single,
            subject.id,
            target.id if target else None,
        )

    @staticmethod
    def _key_from_predicate(predicate: Predicate) -> Tuple[str, str, bool, int, int | None]:
        return (
            predicate.pred_type,
            predicate.subtype,
            predicate.is_single,
            predicate.subject.id,
            predicate.target.id if predicate.target else None,
        )

    def get_probability(self, predicate_temp: PredicateTemplate, i: BNPCType, r: BNPCType):
        key = self._key_from_template(predicate_temp, i, r)
        belief = self._belief_index.get(key)
        return belief.probability if belief else 0.5

    def __iter__(self):
        return iter(self.beliefs)

    def __contains__(self, item: Belief | Predicate):
        if isinstance(item, Belief):
            key = self._key_from_predicate(item.predicate)
            return key in self._belief_index
        elif isinstance(item, Predicate):
            key = self._key_from_predicate(item)
            return key in self._belief_index
        return False

    def update(self, predicate: Predicate, probability: float):
        key = self._key_from_predicate(predicate)
        belief = self._belief_index.get(key)
        if belief:
            belief.probability = probability
        else:
            new_belief = Belief(predicate=predicate, probability=probability, predicate_template=predicate.template)
            self.beliefs.append(new_belief)
            self._belief_index[key] = new_belief

    def add_belief(self, predicate: Predicate, probability: float = 1.0):
        if not isinstance(predicate, Predicate):
            raise TypeError("Only Predicate instances can be added as traits.")
        self.update(predicate, probability)

    def remove_predicate(self, pred_type: str, subtype: str) -> None:
        to_remove = []
        for belief in self.beliefs:
            pred = belief.predicate
            if pred.pred_type == pred_type and pred.subtype == subtype:
                to_remove.append(belief)

        for belief in to_remove:
            self.beliefs.remove(belief)
            key = self._key_from_predicate(belief.predicate)
            self._belief_index.pop(key, None)

    def get_traits_about(self, subject: BNPCType) -> List[Belief]:
        return [belief for belief in self.beliefs if belief.predicate.subject == subject and belief.predicate.is_single]

    def get_relationships_about(self, subject: BNPCType, target: BNPCType) -> List[Belief]:
        return [belief for belief in self.beliefs if not belief.predicate.is_single and belief.predicate.subject == subject and belief.predicate.target == target]
