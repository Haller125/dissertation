import os
import yaml
from typing import List, Tuple, Dict, Sequence

from src.social_exchange.exchange_loader import load_exchange_templates


def load_configs(config_dir: str | None = None):
    if config_dir is None:
        root = os.path.dirname(os.path.dirname(__file__))
        config_dir = os.path.join(root, "configs")
    with open(os.path.join(config_dir, "traits.yaml"), "r", encoding="utf-8") as f:
        traits_data = yaml.safe_load(f) or {}
    with open(os.path.join(config_dir, "relationships.yaml"), "r", encoding="utf-8") as f:
        relationships_data = yaml.safe_load(f) or {}
    with open(os.path.join(config_dir, "config.yaml"), "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f) or {}

    exchanges_path = os.path.join(config_dir, "exchanges.yaml")
    if not os.path.exists(exchanges_path) or os.path.getsize(exchanges_path) == 0:
        exchanges_path = os.path.join(config_dir, "exchanges_example.yaml")
    exchanges = load_exchange_templates(exchanges_path)

    traits: List[Tuple[str, float]] = [
        (name, float(prob)) for name, prob in traits_data.get("probabilities", {}).items()
    ]
    relationships: List[Tuple[str, float]] = [
        (name, float(prob)) for name, prob in relationships_data.get("probabilities", {}).items()
    ]
    trait_opposites: Dict[str, Sequence[str]] = traits_data.get("opposites", {})
    relationship_opposites: Dict[str, Sequence[str]] = relationships_data.get("opposites", {})
    n = config_data.get("n", 5)
    return traits, relationships, trait_opposites, relationship_opposites, exchanges, n


def build_from_yaml(config_dir: str | None = None):
    from src.CiFBuilder.BCiFBuilder import CiFBuilder
    from src.NamesDB.NamesDB import Names

    traits, relationships, trait_opposites, relationship_opposites, exchanges, n = load_configs(config_dir)
    names = Names().get_n_name(n)
    builder = CiFBuilder(
        traits=traits,
        relationships=relationships,
        exchanges=exchanges,
        names=names,
        n=n,
        trait_opposites=trait_opposites,
        relationship_opposites=relationship_opposites,
    )
    return builder.build()
