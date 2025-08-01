import pytest

from src.belief.BeliefStore import BeliefStore
from src.predicates.PredicateTemplate import PredicateTemplate
from src.predicates.BCondition import BHasNotCondition
from src.rule.BRule import BRule
from src.npc.BNPC import BNPC


def make_npcs(n=1):
    return [BNPC(i, f"NPC{i}") for i in range(n)]


def test_condition_returns_inverted_probability():
    npc = make_npcs(1)[0]
    store = BeliefStore()
    tmpl = PredicateTemplate('trait', 'kind', True)
    pred = tmpl.instantiate(subject=npc)
    store.add_belief(pred, probability=0.7)

    cond = BHasNotCondition(req_predicate=tmpl)
    result = cond(store, npc)
    assert result == pytest.approx(0.3)


def test_rule_probability_with_has_not_condition():
    npc = make_npcs(1)[0]
    store = BeliefStore()
    tmpl = PredicateTemplate('trait', 'kind', True)
    pred = tmpl.instantiate(subject=npc)
    store.add_belief(pred, probability=0.7)

    cond = BHasNotCondition(req_predicate=tmpl)
    rule = BRule(name='r', condition=[cond], weight=1.0)
    prob = rule.probability(store, npc)
    assert prob == pytest.approx(0.3)
