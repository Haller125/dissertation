import itertools
from dataclasses import dataclass, field
from random import random, shuffle
from typing import Dict, List, Sequence

from src.CiF.BCiF import BCiF
from src.NamesDB.NamesDB import Names
from src.npc.BNPC import BNPC
from src.predicates.PredicateTemplate import PredicateTemplate
from src.social_exchange.BSocialExchangeTemplate import BSocialExchangeTemplate
from src.types.NPCTypes import BNPCType


@dataclass
class CiFBuilder:
    traits: List[tuple[str, float]]
    relationships: List[tuple[str, float]]
    exchanges: List[BSocialExchangeTemplate]
    names: List[str] = field(default_factory=lambda: Names().get_n_name(10))
    n: int = 10
    trait_opposites: Dict[str, Sequence[str]] = field(default_factory=dict)
    relationship_opposites: Dict[str, Sequence[str]] = field(default_factory=dict)
    NPCs: List[BNPCType] = field(default_factory=list)

    def build(self):
        if len(self.names) < self.n:
            raise ValueError("Not enough NamesDB provided for the number of NPCs.")
        if len(self.traits) == 0:
            raise ValueError("At least one trait must be provided.")
        if len(self.relationships) == 0:
            raise ValueError("At least one relationship must be provided.")
        if len(self.exchanges) == 0:
            raise ValueError("At least one social exchange template must be provided.")
        if self.n < 1:
            raise ValueError("At least one NPC must be created.")

        if self.NPCs:
            npcs = self.NPCs
        else:
            npcs = [BNPC(i, self.names[i]) for i in range(self.n)]
            npcs = self.initialize_beliefs(npcs)

        return BCiF(
            NPCs=npcs,
            actions=self.exchanges,
            traits=[trait for trait, _ in self.traits],
            relationships=[relationship for relationship, _ in self.relationships],
            trait_opposites=self.trait_opposites.copy(),
            relationship_opposites=self.relationship_opposites.copy(),
        )

    def initialize_beliefs(self, npcs: List[BNPCType]):
        for npc in npcs:
            self.initialize_traits(npc)

        for npc1, npc2 in itertools.permutations(npcs, 2):
            self.initialize_relationship(npc1, npc2)

        return npcs

    def get_trait_templates(self):
        templates: List[tuple[PredicateTemplate, float]] = []

        for trait, probability in self.traits:
            template = PredicateTemplate(pred_type="trait", subtype=trait, is_single=True)
            templates.append((template, probability))

        return templates

    def get_relationship_templates(self):
        templates: List[tuple[PredicateTemplate, float]] = []

        for relationship, probability in self.relationships:
            template = PredicateTemplate(pred_type="relationship", subtype=relationship, is_single=False)
            templates.append((template, probability))

        return templates

    def initialize_traits(self, npc: BNPCType):
        arr = self.get_trait_templates()
        shuffle(arr)  # Shuffle to ensure randomness in selection
        for trait, probability in arr:
            opp_names = self.trait_opposites.get(trait.subtype, [])
            if isinstance(opp_names, str):
                opp_names = [opp_names]

            skip = False
            for opp in opp_names:
                opp_template = PredicateTemplate(
                    pred_type="trait", subtype=opp, is_single=True
                )
                if npc.beliefStore.get_probability(opp_template, npc, None) > 0.5:
                    skip = True
                    break
            if skip:
                continue

            if random() <= probability:
                npc.beliefStore.add_belief(trait.instantiate(subject=npc))

        return npc

    def initialize_relationship(self, npc1: BNPCType, npc2: BNPCType):
        arr = self.get_relationship_templates()
        shuffle(arr)
        for relationship, probability in arr:
            opp_names = self.relationship_opposites.get(relationship.subtype, [])
            if isinstance(opp_names, str):
                opp_names = [opp_names]

            skip = False
            for opp in opp_names:
                opp_template = PredicateTemplate(
                    pred_type="relationship", subtype=opp, is_single=False
                )
                if npc1.beliefStore.get_probability(opp_template, npc1, npc2) > 0.5:
                    skip = True
                    break
            if skip:
                continue

            if random() <= probability:
                npc1.beliefStore.add_belief(
                    relationship.instantiate(subject=npc1, target=npc2)
                )

