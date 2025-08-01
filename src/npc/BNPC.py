import logging
from dataclasses import dataclass, field
import random
from typing import Sequence, List, Optional, Dict

from src.belief.BeliefStore import BeliefStore
from src.desire_formation.BVolition import BVolition
from src.signal_interpolation.SignalInterpolation import update_beliefs_from_observation
from src.social_exchange.BSocialExchange import BSocialExchange
from src.social_exchange.BSocialExchangeTemplate import BSocialExchangeTemplate
from src.types.NPCTypes import BNPCType


@dataclass
class RelationPreference:
    relation_type: str
    weight: float


@dataclass
class Goal:
    target_name: str
    relation_type: str
    value: float


@dataclass
class BNPC(BNPCType):
    id: int
    name: str
    beliefStore: BeliefStore = field(default_factory=BeliefStore)
    relation_preferences: Dict[str, float] = field(default_factory=dict)
    goals: List[Goal] = field(default_factory=list)

    def __str__(self):
        return f"{self.name} (ID: {self.id})"

    def perform_action(self, action: BSocialExchange):
        action.perform(self.beliefStore)

    def desire_formation(self, targets: Sequence[BNPCType], actions_templates: Sequence[BSocialExchangeTemplate]) -> \
            List[BVolition]:
        volitions: List[BVolition] = []

        for r in targets:
            if r is self:
                continue
            for tpl in actions_templates:

                exch = tpl.instantiate(self, r)

                if not exch.is_playable(self.beliefStore):
                    continue

                score = exch.initiator_probability(self.beliefStore) * exch.responder_probability(self.estimate_belief_about(r))

                pref_weight = self.relation_preferences.get(exch.intent.subtype, 0.0)
                goal_bonus = sum(g.value for g in self.goals
                                 if g.relation_type == exch.intent.subtype
                                 and g.target_name == r.name)
                score *= max(pref_weight + goal_bonus, 1e-3)
                volitions.append(BVolition(exch, score))

        volitions.sort(key=lambda t: t.score, reverse=True)
        return volitions

    def select_intent(self, volitions: Sequence[BVolition], threshold: float = 0.0) -> Optional[BSocialExchange]:
        if not volitions:
            return None

        best = max(volitions, key=lambda v: v.score)

        choices: Sequence[BVolition] = [v for v in volitions if v.score == best.score]

        return random.choice(choices).social_exchange

    def update_beliefs_from_observation(self, actions_done: Sequence[BSocialExchange]) -> None:
        for action in actions_done:
            if action.is_accepted is None:
                logging.warning(f"Action {action.name} has no acceptance status, skipping belief update.")
                continue
            if action.initiator is self or action.responder is self:
                continue
            update_beliefs_from_observation(self, action, action.is_accepted)

    def iteration(self, targets: Sequence[BNPCType], actions_templates: Sequence[BSocialExchangeTemplate]):
        volitions = self.desire_formation(targets, actions_templates)
        action = self.select_intent(volitions)

        if action is None:
            return

        self.perform_action(action)

        return action

    def estimate_belief_about(self, other: BNPCType) -> BeliefStore:
        beliefs_from_other_perspective_list = [belief.clone() for belief in self.beliefStore
                                               if belief.predicate.subject == other]

        beliefs_from_other_perspective = BeliefStore(beliefs=beliefs_from_other_perspective_list)

        return beliefs_from_other_perspective

    def get_traits(self, npc=None):
        subject = npc if npc is not None else self

        res = []
        for belief in self.beliefStore:
            if belief.predicate.subject is subject and belief.predicate.is_single:
                res.append(belief)

        return res

    def get_relationships(self, subject, target):
        res = []
        for belief in self.beliefStore:
            if not belief.predicate.is_single and belief.predicate.subject is subject and belief.predicate.target is target:
                res.append(belief)
        return res

    @staticmethod
    def generate_random_goal(others: Sequence[BNPCType], relationships: List[str]) -> Goal:
        from random import choice, uniform

        target = choice(others)
        relation_type = choice(relationships)
        value = uniform(0.1, 1.0)

        goal = Goal(target_name=target.name, relation_type=relation_type, value=value)

        return goal

    def add_goal(self, goal: Goal):
        self.goals.append(goal)

    def remove_goal(self, goal: Goal):
        if goal in self.goals:
            self.goals.remove(goal)
        else:
            logging.warning(f"Goal {goal} not found in {self.name}'s goals.")

    def clear_goals(self):
        self.goals.clear()
        logging.info(f"All goals cleared for {self.name}.")

    def add_random_goals(self, others: Sequence[BNPCType], relationships: List[str], num_goals: int = 1):
        for _ in range(num_goals):
            goal = self.generate_random_goal(others, relationships)
            self.add_goal(goal)
            logging.info(f"Added goal: {goal} to {self.name}.")

    def set_relation_preference(self, relation_type: str, weight: float):
        if weight < 0 or weight > 1:
            raise ValueError("Weight must be between 0 and 1.")
        self.relation_preferences[relation_type] = weight
        logging.info(f"Set relation preference for {relation_type} to {weight} for {self.name}.")

    def set_relation_preferences(self, preferences: Dict[str, float]):
        for relation_type, weight in preferences.items():
            self.set_relation_preference(relation_type, weight)
        logging.info(f"Set multiple relation preferences for {self.name}.")



