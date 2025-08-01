import os
from tempfile import NamedTemporaryFile

from src.CiFBuilder.BCiFBuilder import CiFBuilder
from src.predicates.PredicateTemplate import PredicateTemplate
from src.social_exchange.BExchangeEffects import BExchangeEffects
from src.social_exchange.BSocialExchangeTemplate import BSocialExchangeTemplate
from src.rule.BRule import BRule
from src.irs.BIRS import BInfluenceRuleSet
from src.predicates.BCondition import BHasCondition
from src.save_system.save_system import save_model, load_model


class DummyCondition(BHasCondition):
    def __init__(self, value: float = 1.0):
        super().__init__(req_predicate=PredicateTemplate('trait', 'dummy', True))
        self.value = value

    def __call__(self, *args, **kwargs) -> float:
        return self.value


def make_template():
    tmpl = PredicateTemplate('relationship', 'ally', False)
    rule = BRule(name='r', condition=[DummyCondition(1.0)], weight=1.0)
    irs = BInfluenceRuleSet(name='irs', rules=[rule])
    effects = BExchangeEffects([], [])
    return BSocialExchangeTemplate(
        name='ally_request',
        preconditions=[lambda *a, **k: True],
        intent=tmpl,
        initiator_irs=irs,
        responder_irs=irs,
        effects=effects
    )


def build_cif():
    template = make_template()
    builder = CiFBuilder(
        traits=[('kind', 1.0)],
        relationships=[('friend', 1.0)],
        exchanges=[template],
        names=['A', 'B'],
        n=2,
    )
    return builder.build()


def test_save_and_load_model(monkeypatch):
    monkeypatch.setattr('src.CiFBuilder.BCiFBuilder.random', lambda: 0.0)
    cif = build_cif()
    cif.iteration()
    assert cif.actions_done
    first_len = len(cif.actions_done)

    with NamedTemporaryFile(delete=False) as tmp:
        save_model(cif, tmp.name)
        tmp_path = tmp.name

    cif.iteration()
    assert len(cif.actions_done) > first_len

    loaded = load_model(tmp_path)
    os.remove(tmp_path)

    assert len(loaded.actions_done) == first_len
    # ensure we can continue simulation
    loaded.iteration()
    assert len(loaded.actions_done) > first_len
