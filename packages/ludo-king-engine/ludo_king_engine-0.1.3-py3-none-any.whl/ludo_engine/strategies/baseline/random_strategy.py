"""
Random Strategy - Makes completely random valid moves.
"""

import random

from ludo_engine.models.model import AIDecisionContext
from ludo_engine.strategies.base import Strategy


class RandomStrategy(Strategy):
    """
    Random strategy for baseline comparison.
    Makes completely random valid moves.
    """

    def __init__(self):
        super().__init__("Random", "Baseline strategy that makes random valid moves")

    def decide(self, game_context: AIDecisionContext) -> int:
        valid_moves = self._get_valid_moves(game_context)

        if not valid_moves:
            return 0

        # Completely random choice
        random_move = random.choice(valid_moves)
        return random_move.token_id
