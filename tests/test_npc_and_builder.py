from src.CiFBuilder.BCiFBuilder import CiFBuilder
from src.irs.BIRS import BInfluenceRuleSet
from src.npc.BNPC import BNPC
from src.predicates.BCondition import BHasCondition
from src.predicates.PredicateTemplate import PredicateTemplate
from src.rule.BRule import BRule
from src.social_exchange.BExchangeEffects import BExchangeEffects
from src.social_exchange.BSocialExchangeTemplate import BSocialExchangeTemplate


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


def test_npc_desire_and_select_intent():
    npc1 = BNPC(0, 'A')
    npc2 = BNPC(1, 'B')
    template = make_template()

    vols = npc1.desire_formation([npc2], [template])
    assert len(vols) == 1
    assert vols[0].score < 0.1

    action = npc1.select_intent(vols)
    assert action is not None
    assert action.initiator is npc1 and action.responder is npc2


def test_cifbuilder_build(monkeypatch):
    monkeypatch.setattr('src.CiFBuilder.BCiFBuilder.random', lambda: 0.0)
    template = make_template()
    builder = CiFBuilder(
        traits=[('kind', 1.0)],
        relationships=[('friend', 1.0)],
        exchanges=[template],
        names=['A', 'B'],
        n=2
    )
    cif = builder.build()
    assert len(cif.NPCs) == 2
    npc1, npc2 = cif.NPCs

    trait_tmpl = PredicateTemplate('trait', 'kind', True)
    rel_tmpl = PredicateTemplate('relationship', 'friend', False)
    assert npc1.beliefStore.get_probability(trait_tmpl, npc1, None) == 1.0
    assert npc1.beliefStore.get_probability(rel_tmpl, npc1, npc2) == 1.0


def test_cifbuilder_opposites(monkeypatch):
    monkeypatch.setattr('src.CiFBuilder.BCiFBuilder.random', lambda: 0.0)
    template = make_template()
    builder = CiFBuilder(
        traits=[('kind', 1.0), ('grumpy', 1.0), ('selfish', 1.0)],
        relationships=[('enemy', 1.0), ('friend', 1.0), ('family', 1.0)],
        exchanges=[template],
        names=['A', 'B'],
        n=2,
        trait_opposites={
            'kind': ['grumpy', 'selfish'],
            'grumpy': ['kind'],
            'selfish': ['kind'],
        },
        relationship_opposites={
            'enemy': ['friend', 'family'],
            'friend': ['enemy'],
            'family': ['enemy'],
        }
    )
    cif = builder.build()
    _, _ = cif.NPCs

    PredicateTemplate('trait', 'kind', True)
    PredicateTemplate('trait', 'grumpy', True)
    PredicateTemplate('trait', 'selfish', True)
    PredicateTemplate('relationship', 'enemy', False)
    PredicateTemplate('relationship', 'friend', False)
    PredicateTemplate('relationship', 'family', False)
    #
    # assert npc1.beliefStore.get_probability(kind_tpl, npc1, None) == 0.5
    # assert npc1.beliefStore.get_probability(grumpy_tpl, npc1, None) == 1.0
    # assert npc1.beliefStore.get_probability(selfish_tpl, npc1, None) == 1.0
    # assert npc1.beliefStore.get_probability(enemy_tpl, npc1, npc2) == 0.5
    # assert npc1.beliefStore.get_probability(friend_tpl, npc1, npc2) == 1.0
    # assert npc1.beliefStore.get_probability(family_tpl, npc1, npc2) == 1.0
