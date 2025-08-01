import math
import pytest

from src.irs.BIRS import BInfluenceRuleSet
from src.rule.BRule import BRule
from src.predicates.PredicateTemplate import PredicateTemplate
from src.predicates.BCondition import BHasCondition, BHasNotCondition
from src.signal_interpolation.EstimateLikelihood import estimate_likelihood


def test_estimate_likelihood_with_mixed_rules():
    tmpl = PredicateTemplate('relationship', 'ally', False)
    rule1 = BRule(name='r1', condition=[BHasCondition(tmpl)], weight=1.0)
    rule2 = BRule(name='r2', condition=[BHasNotCondition(tmpl)], weight=0.5)
    irs = BInfluenceRuleSet(name='irs', rules=[rule1, rule2])

    logistic = 1.0 / (1.0 + math.exp(-(1.0 - 0.5)))

    assert estimate_likelihood(irs, tmpl, True, True) == pytest.approx(logistic)
    assert estimate_likelihood(irs, tmpl, True, False) == pytest.approx(1 - logistic)
    assert estimate_likelihood(irs, tmpl, False, True) == pytest.approx(1 - logistic)
    assert estimate_likelihood(irs, tmpl, False, False) == pytest.approx(logistic)


def test_estimate_likelihood_no_relevant_rules():
    tmpl = PredicateTemplate('trait', 'kind', True)
    irs = BInfluenceRuleSet(name='irs', rules=[])
    assert estimate_likelihood(irs, tmpl, True, True) == 0.5
