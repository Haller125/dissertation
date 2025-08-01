from src.CiFBuilder.BCiFBuilder import CiFBuilder
from src.pygame.Game import Game
from src.social_exchange.BSocialExchangeTemplate import make_template

if __name__ == "__main__":
    template = make_template()
    builder = CiFBuilder(
        traits=[
            ('kind', 0.9), ('brave', 0.8), ('curious', 0.7), ('loyal', 0.85),
            ('selfish', 0.3), ('intelligent', 0.95), ('funny', 0.6), ('serious', 0.4),
            ('honest', 0.88), ('greedy', 0.2), ('romantic', 0.5), ('shy', 0.6),
            ('confident', 0.7), ('generous', 0.9), ('ambitious', 0.8), ('lazy', 0.35),
            ('sarcastic', 0.45), ('empathetic', 0.9), ('moody', 0.3), ('optimistic', 0.75),
            ('pessimistic', 0.25), ('assertive', 0.7)
        ],
        relationships=[
            ('friend', 0.95), ('enemy', 0.3), ('rival', 0.4), ('mentor', 0.7),
            ('student', 0.6), ('lover', 0.5), ('sibling', 0.8), ('colleague', 0.75),
            ('neighbor', 0.5), ('parent', 0.6), ('child', 0.65), ('boss', 0.3),
            ('follower', 0.55), ('leader', 0.8), ('acquaintance', 0.6), ('teammate', 0.7),
            ('classmate', 0.65), ('partner', 0.75), ('spouse', 0.5), ('roommate', 0.4),
            ('adversary', 0.35), ('confidant', 0.6), ('ally', 0.85), ('opponent', 0.3)
        ],
        exchanges=[template],
        names=[
            'Alex', 'Jordan', 'Taylor', 'Morgan', 'Riley',
            'Casey', 'Drew', 'Jamie', 'Avery', 'Reese',
            'Cameron', 'Quinn', 'Skyler', 'Logan', 'Blake',
            'Harper', 'Emerson', 'Peyton', 'Rowan', 'Dakota'
        ],
        n=20
    )
    cif = builder.build()
    game = Game(cif)
    game.run()
