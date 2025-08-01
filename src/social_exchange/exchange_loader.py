import yaml
from typing import List, Sequence

from src.predicates.PredicateTemplate import PredicateTemplate
from src.predicates.BCondition import BHasCondition, BHasNotCondition
from src.rule.BRule import BRule
from src.irs.BIRS import BInfluenceRuleSet
from src.predicates.BEffect import BAddPredicateEffect, BRemovePredicateEffect
from src.social_exchange.BExchangeEffects import BExchangeEffects
from src.social_exchange.BSocialExchangeTemplate import BSocialExchangeTemplate


class BConstantCondition(BHasCondition):
    def __init__(self, value: float):
        super().__init__(req_predicate=PredicateTemplate("trait", "constant", True))
        self.value = value

    def __call__(self, *args, **kwargs) -> float:
        return self.value


def _predicate_template(data: dict) -> PredicateTemplate:
    return PredicateTemplate(
        pred_type=data["pred_type"],
        subtype=data["subtype"],
        is_single=bool(data["is_single"]),
    )


def _parse_condition(data: dict):
    if "constant" in data:
        return BConstantCondition(float(data["constant"]))
    if "has" in data:
        return BHasCondition(_predicate_template(data["has"]))
    if "has_not" in data:
        return BHasNotCondition(_predicate_template(data["has_not"]))
    raise ValueError(f"Unknown condition type: {data}")


def _parse_rule(data: dict) -> BRule:
    conds = [_parse_condition(c) for c in data.get("conditions", [])]
    return BRule(name=data.get("name", ""), condition=conds, weight=data.get("weight"))


def _parse_irs(data: dict) -> BInfluenceRuleSet:
    rules = [_parse_rule(r) for r in data.get("rules", [])]
    return BInfluenceRuleSet(name=data.get("name", ""), rules=rules)


def _parse_effect(data: dict):
    if "add" in data:
        pred = _predicate_template(data["add"])
        prob = data["add"].get("probability", 1.0)
        return BAddPredicateEffect(label="add", predicate=pred, probability=prob)
    if "remove" in data:
        pred = _predicate_template(data["remove"])
        return BRemovePredicateEffect(label="remove", predicate=pred)
    raise ValueError(f"Unknown effect type: {data}")


def _parse_effects(data: dict) -> BExchangeEffects:
    accept = [_parse_effect(e) for e in data.get("accept", [])]
    reject = [_parse_effect(e) for e in data.get("reject", [])]
    return BExchangeEffects(accept_effects=accept, reject_effects=reject)


def _parse_preconditions(seq: Sequence[dict]):
    return [_parse_condition(c) for c in seq]


def _parse_exchange(data: dict) -> BSocialExchangeTemplate:
    name = data["name"]
    text = data.get("text", "")
    intent = _predicate_template(data["intent"])
    preconds = _parse_preconditions(data.get("preconditions", []))
    init_irs = _parse_irs(data.get("initiator_irs", {}))
    resp_irs = _parse_irs(data.get("responder_irs", {}))
    effects = _parse_effects(data.get("effects", {}))
    return BSocialExchangeTemplate(
        name=name,
        preconditions=preconds,
        intent=intent,
        initiator_irs=init_irs,
        responder_irs=resp_irs,
        effects=effects,
        text=text,
    )


def load_exchange_templates(path: str) -> List[BSocialExchangeTemplate]:
    import os

    if not os.path.isabs(path) and not os.path.exists(path):
        base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        alt = os.path.normpath(os.path.join(base, "configs", os.path.basename(path)))
        if os.path.exists(alt):
            path = alt

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or []
    if not isinstance(data, list):
        raise ValueError("Exchanges YAML must be a list of exchanges")
    return [_parse_exchange(entry) for entry in data]
