import math

import pytest

from src.npc.BNPC import BNPC
from src.belief.BeliefStore import BeliefStore
from src.predicates.PredicateTemplate import PredicateTemplate
from src.predicates.BCondition import BHasCondition, BHasNotCondition
from src.rule.BRule import BRule
from src.irs.BIRS import BInfluenceRuleSet
from src.social_exchange.BExchangeEffects import BExchangeEffects
from src.social_exchange.BSocialExchange import BSocialExchange
from src.signal_interpolation.SignalInterpolation import update_beliefs_from_observation


def make_exchange(i, r, weight=0.8):
    cond_pred = PredicateTemplate('relationship', 'ally', False)
    condition = BHasCondition(req_predicate=cond_pred)
    rule = BRule(name='rule', condition=[condition], weight=weight)
    irs = BInfluenceRuleSet(name='irs', rules=[rule])
    intent_tpl = PredicateTemplate('action', 'test', False)
    effects = BExchangeEffects([], [])
    exchange = BSocialExchange(
        name='ex',
        initiator=i,
        responder=r,
        intent=intent_tpl.instantiate(i, r),
        preconditions=[lambda *a, **k: True],
        initiator_irs=irs,
        responder_irs=irs,
        effects=effects,
        text='Test exchange',
    )
    return exchange, cond_pred


def test_update_beliefs_from_observation_accept():
    i = BNPC(0, 'I')
    r = BNPC(1, 'R')
    observer = BNPC(2, 'O')
    exchange, cond_pred = make_exchange(i, r, weight=0.8)

    update_beliefs_from_observation(observer, exchange, accepted=True)
    expected = 1.0 / (1.0 + math.exp(-0.8))
    assert observer.beliefStore.get_probability(cond_pred, i, r) == pytest.approx(expected)
    assert observer.beliefStore.get_probability(cond_pred, r, i) == pytest.approx(expected)


def test_update_beliefs_from_observation_reject():
    i = BNPC(0, 'I')
    r = BNPC(1, 'R')
    observer = BNPC(2, 'O')
    exchange, cond_pred = make_exchange(i, r, weight=0.8)

    update_beliefs_from_observation(observer, exchange, accepted=False)
    prob_true = 1.0 / (1.0 + math.exp(-0.8))
    expected_r = 1 - prob_true
    assert observer.beliefStore.get_probability(cond_pred, i, r) == pytest.approx(prob_true)
    assert observer.beliefStore.get_probability(cond_pred, r, i) == pytest.approx(expected_r)


def test_update_beliefs_complex_environment():
    i = BNPC(0, 'I')
    r = BNPC(1, 'R')
    observer = BNPC(2, 'O')
    cond_pred = PredicateTemplate('relationship', 'ally', False)

    rule_i1 = BRule(name='i1', condition=[BHasCondition(cond_pred)], weight=0.8)
    rule_i2 = BRule(name='i2', condition=[BHasNotCondition(cond_pred)], weight=0.2)
    irs_i = BInfluenceRuleSet(name='i_irs', rules=[rule_i1, rule_i2])

    rule_r1 = BRule(name='r1', condition=[BHasCondition(cond_pred)], weight=0.5)
    irs_r = BInfluenceRuleSet(name='r_irs', rules=[rule_r1])

    intent_tpl = PredicateTemplate('action', 'test', False)
    effects = BExchangeEffects([], [])
    exchange = BSocialExchange(
        name='ex',
        initiator=i,
        responder=r,
        intent=intent_tpl.instantiate(i, r),
        preconditions=[lambda *a, **k: True],
        initiator_irs=irs_i,
        responder_irs=irs_r,
        effects=effects,
        text='Test exchange',
    )

    pred_i = cond_pred.instantiate(i, r)
    pred_r = cond_pred.instantiate(r, i)
    observer.beliefStore = BeliefStore()
    observer.beliefStore.add_belief(pred_i, probability=0.3)
    observer.beliefStore.add_belief(pred_r, probability=0.7)

    update_beliefs_from_observation(observer, exchange, accepted=False)

    sigmoid = lambda x: 1 / (1 + math.exp(-x))
    logistic_i = sigmoid(0.8 - 0.2)
    logistic_r = sigmoid(0.5)
    expected_i = (logistic_i * 0.3) / (logistic_i * 0.3 + (1 - logistic_i) * (1 - 0.3))
    p_obs_true_r = 1 - logistic_r
    p_obs_false_r = logistic_r
    expected_r = (p_obs_true_r * 0.7) / (p_obs_true_r * 0.7 + p_obs_false_r * (1 - 0.7))

    assert observer.beliefStore.get_probability(cond_pred, i, r) == pytest.approx(expected_i)
    assert observer.beliefStore.get_probability(cond_pred, r, i) == pytest.approx(expected_r)
