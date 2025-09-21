"""Weighted Random Strategy.

Stochastic policy that samples moves proportionally to a transformed
strategic value with soft prioritization heuristics:
  - Finish: chosen immediately (uniform among finishing moves).
  - Home advancement & captures get value boosts.
  - Safe moves get a mild bonus; high-threat moves penalized.
  - Temperature anneals by game phase (early -> exploratory, late -> sharper).
  - Diversity: light penalty on repeatedly moving same token in consecutive turns
    via recent usage history embedded in game_context (optional; ignored if absent).
  - Epsilon: small probability of pure uniform random for exploration.

All numeric parameters sourced from StrategyConstants WEIGHTED_RANDOM_*.
"""

from __future__ import annotations

import math
import random
from typing import Dict, List

from ludo_engine.models.constants import (
    BoardConstants,
    GameConstants,
    StrategyConstants,
)
from ludo_engine.models.model import AIDecisionContext, MoveType, ValidMove
from ludo_engine.strategies.base import Strategy
from ludo_engine.strategies.utils import get_opponent_main_positions


class WeightedRandomStrategy(Strategy):
    def __init__(self):
        super().__init__(
            "WeightedRandom",
            "Stochastic softmax sampling over strategic values with heuristics",
        )
        self.recent_moves_memory = []

    def decide(self, game_context: AIDecisionContext) -> int:  # type: ignore[override]
        moves = self._get_valid_moves(game_context)
        if not moves:
            return 0

        # 1. Immediate finish shortcut
        finish_moves = [m for m in moves if m.move_type == MoveType.FINISH]
        if finish_moves:
            return random.choice(finish_moves).token_id

        # Game phase for temperature selection
        # turn_index = game_context.get("turn_index", 0)
        # Approximate phase by finished tokens ratio
        player_state = game_context.player_state
        finished = player_state.finished_tokens
        phase_ratio = finished / float(GameConstants.TOKENS_PER_PLAYER)
        if phase_ratio < StrategyConstants.WEIGHTED_RANDOM_PHASE_EARLY:
            temp = StrategyConstants.WEIGHTED_RANDOM_TEMP_EARLY
        elif phase_ratio > StrategyConstants.WEIGHTED_RANDOM_PHASE_LATE:
            temp = StrategyConstants.WEIGHTED_RANDOM_TEMP_LATE
        else:
            temp = StrategyConstants.WEIGHTED_RANDOM_TEMP_MID

        # Diversity penalty - expects optional context: recent_token_moves (list of token_ids)
        recent: List[int] = self.recent_moves_memory
        diversity_counts = {}
        if recent:
            for tid in recent:
                diversity_counts[tid] = diversity_counts.get(tid, 0) + 1

        weights: List[float] = []
        tokens: List[int] = []

        # Threat heuristic: approximate opponent threat count (reuse minimal backward distance logic)
        threat_map = self._approx_threats(moves, game_context)

        min_sv = min(m.strategic_value for m in moves)

        for mv in moves:
            sv = mv.strategic_value
            base = sv - min_sv  # shift to non-negative
            # Progress shaping: slight non-linear emphasis
            base = base**1.05 if base > 0 else 0.0

            # Heuristic boosts
            if mv.move_type == MoveType.ADVANCE_HOME_COLUMN:
                base += 1.0
            if mv.captures_opponent:
                captured = mv.captured_tokens
                base += StrategyConstants.WEIGHTED_RANDOM_CAPTURE_BONUS * max(
                    1, len(captured)
                )
            if mv.is_safe_move:
                base += StrategyConstants.WEIGHTED_RANDOM_SAFE_BONUS

            # Threat penalty
            threat_count = threat_map.get(mv.token_id, 0)
            if threat_count > StrategyConstants.WEIGHTED_RANDOM_RISK_THREAT_CAP:
                base *= 1.0 - StrategyConstants.WEIGHTED_RANDOM_RISK_PENALTY

            # Diversity penalty
            if diversity_counts:
                occurrences = diversity_counts.get(mv.token_id, 0)
                if occurrences > 0:
                    base /= (
                        1.0
                        + StrategyConstants.WEIGHTED_RANDOM_DIVERSITY_LAMBDA
                        * occurrences
                    )

            # Ensure minimum positive weight before softmax
            weights.append(max(base, StrategyConstants.WEIGHTED_RANDOM_MIN_WEIGHT))
            tokens.append(mv.token_id)

        # Epsilon uniform exploration
        if random.random() < StrategyConstants.WEIGHTED_RANDOM_EPSILON:
            return self.save_and_return(random.choice(tokens))

        # Softmax sampling
        max_w = max(weights)
        exp_weights = [math.exp((w - max_w) / max(1e-6, temp)) for w in weights]
        total = sum(exp_weights)
        if total <= 0:
            return self.save_and_return(random.choice(tokens))
        r = random.random() * total
        acc = 0.0
        for tid, ew in zip(tokens, exp_weights):
            acc += ew
            if acc >= r:
                return self.save_and_return(tid)
        return self.save_and_return(tokens[-1])

    def save_and_return(self, tid: int) -> int:
        self.recent_moves_memory.append(tid)
        if (
            len(self.recent_moves_memory)
            > StrategyConstants.WEIGHTED_RANDOM_DIVERSITY_MEMORY
        ):
            self.recent_moves_memory.pop(0)
        return tid

    # --- threat approximation ---
    def _approx_threats(
        self, moves: List[ValidMove], ctx: AIDecisionContext
    ) -> Dict[int, int]:
        opponent_positions = get_opponent_main_positions(ctx)
        threat_map: Dict[int, int] = {}
        for mv in moves:
            landing = mv.target_position
            if not isinstance(landing, int) or BoardConstants.is_home_column_position(
                landing
            ):
                threat_map[mv.token_id] = 0
                continue
            threats = 0
            for opp in opponent_positions:
                if landing <= opp:
                    dist = opp - landing
                else:
                    dist = (GameConstants.MAIN_BOARD_SIZE - landing) + opp
                if 1 <= dist <= 6:
                    threats += 1
            threat_map[mv.token_id] = threats
        return threat_map


__all__ = ["WeightedRandomStrategy"]
