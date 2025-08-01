import cProfile
import io
import pstats
import time
import psutil
from src.CiFBuilder.BCiFBuilder import CiFBuilder
from src.predicates.PredicateTemplate import PredicateTemplate
from src.predicates.BCondition import BHasCondition
from src.rule.BRule import BRule
from src.irs.BIRS import BInfluenceRuleSet
from src.social_exchange.BExchangeEffects import BExchangeEffects
from src.social_exchange.BSocialExchangeTemplate import BSocialExchangeTemplate


def create_template(name: str) -> BSocialExchangeTemplate:
    cond = BHasCondition(PredicateTemplate('trait', 'dummy', True))
    rule = BRule(name='r', condition=[cond], weight=1.0)
    irs = BInfluenceRuleSet(name='irs', rules=[rule])
    effects = BExchangeEffects([], [])
    intent = PredicateTemplate('action', name, False)
    return BSocialExchangeTemplate(
        name=name,
        preconditions=[lambda *a, **k: True],
        intent=intent,
        initiator_irs=irs,
        responder_irs=irs,
        effects=effects,
    )


def run_builder(num_traits: int, num_rels: int, num_exch: int, n_npcs: int):
    traits = [(f'trait_{i}', 1.0) for i in range(num_traits)]
    rels = [(f'rel_{i}', 1.0) for i in range(num_rels)]
    exchs = [create_template(f'exch_{i}') for i in range(num_exch)]
    names = [f'NPC{i}' for i in range(n_npcs)]
    builder = CiFBuilder(traits=traits, relationships=rels, exchanges=exchs, names=names, n=n_npcs)

    proc = psutil.Process()
    start = time.time()
    mem_before = proc.memory_info().rss
    cif = builder.build()
    build_time = time.time() - start
    mem_after = proc.memory_info().rss

    start = time.time()
    cif.iteration()
    iter_time = time.time() - start

    mem_used = mem_after - mem_before
    return build_time, iter_time, mem_used


if __name__ == '__main__':
    # configs = [
    #     (1, 1, 1),
    #     (10, 10, 10),
    #     (20, 20, 20),
    #     (30, 30, 30),
    # ]
    # for t, r, e in configs:
    #     bt, it, mem = run_builder(t, r, e, n_npcs=20)
    #     print(f"traits={t}\t rels={r}\t exch={e}:\t build_time={bt:.3f}s, \titeration_time={it:.3f}s, \tmem_used={mem/1e6:.2f}MB")

    # 1. Create a profiler
    pr = cProfile.Profile()
    pr.enable()

    # 2. Run exactly the piece you want to measure
    #    e.g. build everything once (or loop a few times for stability)
    bt, it, mem = run_builder(50, 50, 50, n_npcs=50)

    pr.disable()

    # 3. Dump the stats to stdout (or to a file)
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s)
    # sort by cumulative time; you can also sort by 'cumtime'
    ps.strip_dirs().sort_stats('tottime').print_stats(20)
    print(s.getvalue())
