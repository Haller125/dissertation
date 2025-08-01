from typing import Callable

from src.belief.BeliefStore import BeliefStore
from src.desire_formation.BVolition import BVolition
from src.social_exchange.BSocialExchangeTemplate import BSocialExchangeTemplate
from src.types.NPCTypes import BNPCType

BDesireFormationType = Callable[[BNPCType, list[BNPCType], BeliefStore, list[BSocialExchangeTemplate]], BVolition]
