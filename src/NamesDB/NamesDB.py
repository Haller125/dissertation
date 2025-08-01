from dataclasses import dataclass, field
import random
import names


@dataclass
class Names:
    _pool: list[str] = field(default_factory=lambda: [
        names.get_first_name() for _ in range(5_000)   # adjust pool size as you like
    ])

    def get_name(self) -> str:
        return random.choice(self._pool)

    def get_n_name(self, n: int) -> list[str]:
        return random.sample(self._pool, n)
