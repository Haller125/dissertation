import pytest

from src.belief.BeliefStore import BeliefStore
from src.predicates.PredicateTemplate import PredicateTemplate
from src.predicates.BCondition import BHasCondition
from src.predicates.BEffect import BAddPredicateEffect, BRemovePredicateEffect
from src.social_exchange.BExchangeEffects import BExchangeEffects
from src.social_exchange.BSocialExchange import BSocialExchange
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


def make_irs(prob: float) -> BInfluenceRuleSet:
    rule = BRule(name='r', condition=[DummyCondition(prob)], weight=1.0)
    return BInfluenceRuleSet(name='irs', rules=[rule])


def test_social_exchange_perform_accept():
    initiator, responder = make_npcs()
    state = BeliefStore()

    tmpl = PredicateTemplate('relationship', 'ally', False)
    intent = tmpl.instantiate(initiator, responder)
    irs = make_irs(1.0)
    effects = BExchangeEffects(
        accept_effects=[BAddPredicateEffect(label='a', predicate=tmpl, probability=1.0)],
        reject_effects=[BRemovePredicateEffect(label='r', predicate=tmpl)]
    )

    exch = BSocialExchange(
        name='test',
        initiator=initiator,
        responder=responder,
        intent=intent,
        preconditions=[lambda *a, **k: True],
        initiator_irs=irs,
        responder_irs=irs,
        effects=effects,
        text='Test exchange',
    )

    assert exch.is_playable(state)
    exch.perform(state)
    assert exch.is_accepted is True
    assert state.get_probability(tmpl, initiator, responder) == pytest.approx(1.0)
