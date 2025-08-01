import math
import pytest

from src.belief.BeliefStore import BeliefStore
from src.predicates.PredicateTemplate import PredicateTemplate
from src.predicates.BCondition import BHasCondition
from src.rule.BRule import BRule
from src.irs.BIRS import BInfluenceRuleSet
from src.npc.BNPC import BNPC


class DummyCondition(BHasCondition):
    def __init__(self, value: float):
        super().__init__(req_predicate=PredicateTemplate('trait', 'dummy', True))
        self.value = value

    def __call__(self, *args, **kwargs) -> float:
        return self.value


def make_npcs(n=2):
    return [BNPC(i, f"NPC{i}") for i in range(n)]


def test_rule_probability():
    rule = BRule(name='r', condition=[DummyCondition(0.2), DummyCondition(0.5)], weight=1.0)
    store = BeliefStore()
    i, r = make_npcs()
    assert rule.probability(store, i, r) == pytest.approx(0.1)


def test_influence_rule_set_calculations():
    rule1 = BRule(name='r1', condition=[DummyCondition(1.0)], weight=1.0)
    rule2 = BRule(name='r2', condition=[DummyCondition(0.5)], weight=2.0)
    irs = BInfluenceRuleSet(name='irs', rules=[rule1, rule2])
    store = BeliefStore()
    i, r = make_npcs()

    expected_value = (rule1.weight * rule1.probability(store, i, r) +
                      rule2.weight * rule2.probability(store, i, r))
    assert irs.expected_value(store, i, r) == pytest.approx(expected_value)

    expected_prob = 1.0 / (1.0 + math.exp(-expected_value))
    assert irs.acceptance_probability(store, i, r) == pytest.approx(expected_prob)


def test_rule_probability_no_conditions():
    rule = BRule(name='empty', condition=[], weight=1.0)
    with pytest.raises(ValueError):
        rule.probability(BeliefStore(), BNPC(0, 'A'), BNPC(1, 'B'))


class InvalidCondition(BHasCondition):
    def __init__(self, value: float):
        super().__init__(req_predicate=PredicateTemplate('trait', 'dummy', True))
        self.value = value

    def __call__(self, *args, **kwargs) -> float:
        return self.value


def test_rule_probability_invalid_value():
    rule = BRule(name='r', condition=[InvalidCondition(1.5)], weight=1.0)
    with pytest.raises(ValueError):
        rule.probability(BeliefStore(), BNPC(0, 'A'), BNPC(1, 'B'))


def test_birs_add():
    irs = BInfluenceRuleSet(name='irs')
    rule = BRule(name='r', condition=[DummyCondition(1.0)], weight=1.0)
    irs.add(rule)
    assert rule in irs.rules
