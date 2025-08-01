from dataclasses import dataclass

from src.social_exchange.BSocialExchange import BSocialExchange


@dataclass(slots=True, frozen=True)
class BVolition:
    social_exchange: BSocialExchange
    score: float
