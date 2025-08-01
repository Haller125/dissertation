from typing import List

from src.irs.BIRS import BInfluenceRuleSet
from src.predicates.BCondition import BHasCondition, BHasNotCondition
from src.predicates.PredicateTemplate import PredicateTemplate
from src.utils.sigmoid import sigmoid


def estimate_likelihood(irs: BInfluenceRuleSet, predicate: PredicateTemplate, pred_true: bool, accepted: bool) -> float:
    relevant_rules: List[float] = []
    # weight in [-inf, +inf]
    for rule in irs.rules:
        for condition in rule.condition:
            if predicate.matches(condition.req_predicate):
                if isinstance(condition, BHasCondition):
                    relevant_rules.append(rule.weight)
                elif isinstance(condition, BHasNotCondition):
                    relevant_rules.append(-rule.weight)

    if not relevant_rules:
        return 0.5

    prob = sigmoid(sum(weight for weight in relevant_rules))

    if pred_true:
        if accepted:
            return prob
        else:
            return 1 - prob
    else:
        if accepted:
            return 1 - prob
        else:
            return prob

