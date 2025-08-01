from src.predicates.BCondition import BHasCondition, BHasNotCondition
from src.predicates.PredicateTemplate import PredicateTemplate
from src.social_exchange.BSocialExchangeTemplate import BSocialExchangeTemplate
from src.social_exchange.exchange_loader import (
    load_exchange_templates,
    BConstantCondition,
)


def test_load_exchange_templates():
    templates = load_exchange_templates('../configs/exchanges_example.yaml')
    assert isinstance(templates, list)
    assert templates

    tmpl = templates[0]
    assert isinstance(tmpl, BSocialExchangeTemplate)
    assert tmpl.name == 'ally_request'
    assert tmpl.intent.pred_type == 'relationship'
    assert tmpl.intent.subtype == 'ally'

    assert len(tmpl.preconditions) == 3
    assert isinstance(tmpl.preconditions[0], BConstantCondition)
    assert isinstance(tmpl.preconditions[1], BHasCondition)
    assert isinstance(tmpl.preconditions[2], BHasNotCondition)
    assert tmpl.initiator_irs.rules[0].weight == 1.0
    assert tmpl.initiator_irs.rules[1].weight == 0.5
    assert tmpl.responder_irs.rules[0].weight == 1.0
    assert tmpl.responder_irs.rules[1].weight == 0.2

    accept_effects = tmpl.effects.accept_effects
    reject_effects = tmpl.effects.reject_effects
    assert len(accept_effects) == 2
    assert len(reject_effects) == 2
    assert accept_effects[0].probability == 1.0
    pred_add = accept_effects[0].predicate
    assert isinstance(pred_add, PredicateTemplate)
    assert pred_add.subtype == 'ally'
    pred_remove = accept_effects[1].predicate
    assert pred_remove.subtype == 'enemy'
    assert reject_effects[0].label == 'remove'
    pred_rj_add = reject_effects[1].predicate
    assert pred_rj_add.subtype == 'rival'
