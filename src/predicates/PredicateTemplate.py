from __future__ import annotations

from dataclasses import dataclass

from src.types.NPCTypes import NPCType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.predicates.Predicate import Predicate  # Avoid circular import


@dataclass(frozen=True)
class PredicateTemplate:
    pred_type: str  # "trait", "relationship" etc.
    subtype: str  # "trust", "friendship", "kind", "evil" etc.
    is_single: bool  # whether the predicate is single (applies to one NPC) or relational (applies to two NPCs)

    def instantiate(self, subject: NPCType, target: NPCType = None) -> "Predicate":
        from src.predicates.Predicate import Predicate
        return Predicate(
            pred_type=self.pred_type,
            subtype=self.subtype,
            subject=subject,
            target=target,
            is_single=self.is_single,
            template=self,
        )

    def matches(self, other: PredicateTemplate) -> bool:
        return (self.pred_type == other.pred_type and
                self.subtype == other.subtype and
                self.is_single == other.is_single)
