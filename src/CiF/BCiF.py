from dataclasses import dataclass, field
from typing import List, Dict, Sequence

from src.social_exchange.BSocialExchange import BSocialExchange
from src.social_exchange.BSocialExchangeTemplate import BSocialExchangeTemplate
from src.types.NPCTypes import BNPCType


@dataclass
class BCiF:
    NPCs: List[BNPCType]
    actions: List[BSocialExchangeTemplate]
    traits: List[str]
    relationships: List[str]
    actions_done: List[BSocialExchange] = field(default_factory=list)
    trait_opposites: Dict[str, Sequence[str]] = field(default_factory=dict)
    relationship_opposites: Dict[str, Sequence[str]] = field(default_factory=dict)

    def iteration(self):
        actions_done: List[BSocialExchange] = []

        for npc in self.NPCs:
            action = npc.iteration(self.NPCs, self.actions)

            if action is not None:
                actions_done.append(action)

        for npc in self.NPCs:
            npc.update_beliefs_from_observation(actions_done)

        self.actions_done.extend(actions_done)

    def get_exchanges(self, i, r):
        res = []
        for exch in self.actions_done:
            if (exch.initiator is i and exch.responder is r) or (exch.initiator is r and exch.responder is i):
                res.append(exch)
        return res

    def add_trait(self, trait: str, opposites: Sequence[str] = ()) -> None:
        if trait not in self.traits:
            self.traits.append(trait)
        if opposites:
            self.trait_opposites[trait] = list(opposites)

    def remove_trait(self, trait: str) -> None:
        if trait in self.traits:
            self.traits.remove(trait)
        self.trait_opposites.pop(trait, None)
        for npc in self.NPCs:
            npc.beliefStore.remove_predicate('trait', trait)

    def add_relationship(self, relationship: str, opposites: Sequence[str] = ()) -> None:
        if relationship not in self.relationships:
            self.relationships.append(relationship)
        if opposites:
            self.relationship_opposites[relationship] = list(opposites)

    def remove_relationship(self, relationship: str) -> None:
        if relationship in self.relationships:
            self.relationships.remove(relationship)
        self.relationship_opposites.pop(relationship, None)
        for npc in self.NPCs:
            npc.beliefStore.remove_predicate('relationship', relationship)
