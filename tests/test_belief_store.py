import pytest

from src.belief.Belief import Belief
from src.belief.BeliefStore import BeliefStore
from src.predicates.PredicateTemplate import PredicateTemplate
from src.npc.BNPC import BNPC


def make_npcs(n=2):
    return [BNPC(i, f"NPC{i}") for i in range(n)]


def test_add_and_get_probability():
    npc, _ = make_npcs()
    store = BeliefStore()
    tmpl = PredicateTemplate(pred_type="trait", subtype="kind", is_single=True)
    pred = tmpl.instantiate(subject=npc)

    store.add_belief(pred, probability=0.7)
    assert store.get_probability(tmpl, npc, None) == pytest.approx(0.7)

    other = PredicateTemplate(pred_type="trait", subtype="brave", is_single=True)
    assert store.get_probability(other, npc, None) == 0.5


def test_contains_and_update():
    npc, _ = make_npcs()
    store = BeliefStore()
    tmpl = PredicateTemplate(pred_type="trait", subtype="smart", is_single=True)
    pred = tmpl.instantiate(subject=npc)
    store.add_belief(pred)
    belief = next(iter(store))

    assert pred in store
    assert belief in store

    store.update(pred, 0.3)
    assert store.get_probability(tmpl, npc, None) == pytest.approx(0.3)

def test_remove_predicate():
    npc, _ = make_npcs()
    store = BeliefStore()
    tmpl = PredicateTemplate('trait', 'kind', True)
    pred = tmpl.instantiate(subject=npc)
    store.add_belief(pred, 1.0)

    store.remove_predicate('trait', 'kind')
    assert store.get_probability(tmpl, npc, None) == 0.5
    assert pred not in store


def test_initial_beliefs_indexing():
    npc, _ = make_npcs()
    tmpl = PredicateTemplate('trait', 'kind', True)
    pred = tmpl.instantiate(subject=npc)
    belief = Belief(predicate=pred, probability=0.8, predicate_template=tmpl)
    store = BeliefStore(beliefs=[belief])

    assert list(store)  # iterable
    assert store.get_probability(tmpl, npc, None) == pytest.approx(0.8)
