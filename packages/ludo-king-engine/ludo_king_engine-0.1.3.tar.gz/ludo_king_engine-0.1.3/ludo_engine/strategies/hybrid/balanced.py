"""Balanced Strategy.

Adaptive hybrid that blends priorities from aggressive (capture/progression),
defensive (threat management, block maintenance), winner (finish/home depth),
and cautious (avoid needless risk when ahead). Dynamic weights shift based on
relative progress and late-game pressure.
"""

from typing import Dict, List, Optional, Set, Tuple

from ludo_engine.models.constants import (
    BoardConstants,
    GameConstants,
    StrategyConstants,
)
from ludo_engine.models.model import AIDecisionContext, MoveType, ValidMove
from ludo_engine.strategies.base import Strategy
from ludo_engine.strategies.utils import (
    LARGE_THREAT_COUNT,
    NO_THREAT_DISTANCE,
    compute_threats_for_moves,
    get_my_main_positions,
    get_opponent_main_positions,
)


class BalancedStrategy(Strategy):
    """Adaptive multi-factor decision policy."""

    def __init__(self):
        super().__init__(
            "Balanced",
            "Adaptive blend of offensive, defensive, and finishing heuristics",
        )

    # --- Public API ---
    def decide(self, game_context: AIDecisionContext) -> int:
        moves = self._get_valid_moves(game_context)
        if not moves:
            return 0

        player_state = game_context.player_state
        active = player_state.active_tokens

        # Use true progress including home column depth for me and opponents
        my_ratio = self._true_progress_ratio(game_context)
        opp_max_ratio = self._max_opponent_progress_ratio(game_context)

        behind = (
            my_ratio + StrategyConstants.BALANCED_RISK_TOLERANCE_MARGIN < opp_max_ratio
        )
        ahead = my_ratio > (
            opp_max_ratio + StrategyConstants.BALANCED_RISK_TOLERANCE_MARGIN
        )
        late_game_pressure = opp_max_ratio >= (
            StrategyConstants.BALANCED_LATE_GAME_FINISH_PUSH
            / GameConstants.TOKENS_PER_PLAYER
        )

        threat_map = compute_threats_for_moves(moves, game_context)
        block_positions = self._own_block_positions(game_context)
        my_positions = get_my_main_positions(game_context)

        # Priority 1: Immediate finish
        finish_move = self._get_move_by_type(moves, MoveType.FINISH)
        if finish_move:
            return finish_move.token_id

        # Priority 2: Deep home column (weighted more under late-game pressure)
        home_moves = self._get_moves_by_type(moves, MoveType.ADVANCE_HOME_COLUMN)
        if home_moves:
            home_weight = StrategyConstants.BALANCED_HOME_PRIORITY * (
                1.2 if late_game_pressure else 1.0
            )
            best_home = max(
                home_moves,
                key=lambda m: (
                    m.target_position * home_weight,
                    m.strategic_value,
                ),
            )
            return best_home.token_id

        # Priority 3: High-quality safe capture (progress + safety) esp. when behind.
        # When clearly ahead, require the capture landing square to be safe.
        capture_choice = self._choose_capture(moves, threat_map, aggressive=behind)
        if capture_choice is not None:
            cap_move = next((m for m in moves if m.token_id == capture_choice), None)
            if cap_move is not None:
                if not (ahead and not cap_move.is_safe_move):
                    return capture_choice

        # Priority 4: Maintain/create protective blocks while progressing
        block_moves = self._block_positive_moves(moves, block_positions, my_positions)
        if block_moves:
            pick = self._select_weighted(block_moves, threat_map, ahead)
            if pick is not None:
                return pick

        # Priority 5: Safe forward progression (moderate threat tolerance when behind)
        safe_moves = self._get_safe_moves(moves)
        if safe_moves:
            pick = self._select_weighted(safe_moves, threat_map, ahead, behind)
            if pick is not None:
                return pick

        # Priority 6: Exit home to maintain presence if needed
        if active < StrategyConstants.BALANCED_MIN_ACTIVE_TARGET or behind:
            exit_move = self._get_move_by_type(moves, MoveType.EXIT_HOME)
            if exit_move:
                return exit_move.token_id

        # Priority 7: Future capture positioning (when neither ahead nor severely threatened)
        future_pos = self._future_capture_positioning(moves, threat_map, game_context)
        if future_pos is not None:
            return future_pos

        # Fallback: Highest strategic value overall
        best = self._get_highest_value_move(moves)
        return best.token_id if best else 0

    # --- Threat Analysis: now via shared utils (compute_threats_for_moves) ---

    # --- Blocks ---
    def _own_block_positions(self, ctx: AIDecisionContext) -> List[int]:
        positions = ctx.player_state.positions_occupied
        occ: Dict[int, int] = {}
        for t in positions:
            if t >= 0 and not BoardConstants.is_home_column_position(t):
                occ[t] = occ.get(t, 0) + 1
        return [pos for pos, c in occ.items() if c >= 2]

    def _block_positive_moves(
        self, moves: List[ValidMove], blocks: List[int], my_positions: Set[int]
    ) -> List[ValidMove]:
        """Prefer moves that create or maintain stacks, avoid breaking existing blocks.

        - If moving from a block (src in blocks) and destination does not land on own token,
          consider it negative and exclude.
        - Include moves that land on own position (create/keep stack) or land on an existing block.
        """
        out: List[ValidMove] = []
        for mv in moves:
            src = mv.current_position
            dst = mv.target_position
            from_block = src in blocks if src is not None else False
            creates_stack = dst in my_positions
            lands_on_block = dst in blocks
            if from_block and not (creates_stack or lands_on_block):
                continue  # would break a block without reforming one
            if creates_stack or lands_on_block:
                out.append(mv)
        return out

    # --- Capture Evaluation ---
    def _choose_capture(
        self,
        moves: List[ValidMove],
        threat_map: Dict[int, Tuple[int, int]],
        aggressive: bool,
    ) -> Optional[int]:
        captures = self._get_capture_moves(moves)
        if not captures:
            return None
        scored: List[Tuple[float, ValidMove]] = []
        for mv in captures:
            tid = mv.token_id
            threat = threat_map.get(tid, (LARGE_THREAT_COUNT, NO_THREAT_DISTANCE))
            # when aggressive allow up to BALANCED_THREAT_SOFT_CAP else stricter
            max_threat_allowed = (
                StrategyConstants.BALANCED_THREAT_SOFT_CAP
                if aggressive
                else StrategyConstants.BALANCED_AHEAD_THREAT_CAP
            )
            if threat[0] > max_threat_allowed:
                continue
            if threat[1] <= 2 and not aggressive:
                continue  # too close to danger when not pushing
            progress_value = 0.0
            for ct in mv.captured_tokens:
                entry = BoardConstants.HOME_COLUMN_ENTRIES[ct.player_color]
                remaining = self._distance_to_finish_proxy(mv.target_position, entry)
                progress_value += (60 - remaining) * 0.01
            score = (
                StrategyConstants.BALANCED_SAFE_CAPTURE_WEIGHT
                * (1.25 if aggressive else 1.0)
                + progress_value * StrategyConstants.BALANCED_SAFE_CAPTURE_WEIGHT
            )
            scored.append((score, mv))
        if not scored:
            return None
        best = max(scored, key=lambda x: x[0])[1]
        return best.token_id

    # --- Future Capture Positioning ---
    def _future_capture_positioning(
        self, moves: List[ValidMove], threat_map: Dict[int, Tuple[int, int]], ctx: Dict
    ) -> Optional[int]:
        candidates = [m for m in moves if m.is_safe_move and not m.captures_opponent]
        if not candidates:
            return None
        scored: List[Tuple[float, ValidMove]] = []
        scan_range = StrategyConstants.BALANCED_FUTURE_CAPTURE_PROXIMITY
        for mv in candidates:
            tid = mv.token_id
            threat = threat_map.get(tid, (LARGE_THREAT_COUNT, NO_THREAT_DISTANCE))
            if threat[0] > StrategyConstants.BALANCED_THREAT_SOFT_CAP:
                continue
            potential = self._estimate_future_capture_potential(
                mv.target_position, scan_range, ctx
            )
            if potential <= 0:
                continue
            scored.append(
                (potential * StrategyConstants.BALANCED_FUTURE_CAPTURE_WEIGHT, mv)
            )
        if not scored:
            return None
        best = max(scored, key=lambda x: x[0])[1]
        return best.token_id

    def _estimate_future_capture_potential(
        self, position: int, rng: int, ctx: AIDecisionContext
    ) -> float:
        """Estimate capture potential based on actual opponent proximity within rng ahead."""
        opponent_positions = get_opponent_main_positions(ctx)
        if not opponent_positions:
            return 0.0
        hits = 0
        best_weight = 0.0
        for opp in opponent_positions:
            # distance forward from our landing to opponent
            if position <= opp:
                dist = opp - position
            else:
                dist = (GameConstants.MAIN_BOARD_SIZE - position) + opp
            if 1 <= dist <= rng:
                hits += 1
                best_weight = max(best_weight, (rng - dist + 1) / rng)
        # Combine count and proximity weight
        return hits * best_weight

    # --- Weighted Selection for progression/safety ---
    def _select_weighted(
        self,
        moves: List[ValidMove],
        threat_map: Dict[int, Tuple[int, int]],
        ahead: bool,
        behind: bool = False,
    ) -> Optional[int]:
        if not moves:
            return None
        scored: List[Tuple[float, ValidMove]] = []
        for mv in moves:
            tid = mv.token_id
            threat = threat_map.get(tid, (0, NO_THREAT_DISTANCE))
            threat_penalty = threat[0] * (2.0 if ahead else 1.0)  # stricter when ahead
            depth_bonus = 0.0
            if BoardConstants.is_home_column_position(mv.target_position):
                depth_bonus = (
                    mv.target_position - GameConstants.HOME_COLUMN_START
                ) * StrategyConstants.BALANCED_HOME_PRIORITY
            progress_component = (
                mv.strategic_value if mv.strategic_value is not None else 0
            ) * StrategyConstants.BALANCED_PROGRESS_WEIGHT
            aggressiveness = 1.2 if behind else 1.0
            composite = (
                progress_component + depth_bonus
            ) * aggressiveness - threat_penalty
            scored.append((composite, mv))
        if not scored:
            return None
        best = max(scored, key=lambda x: x[0])[1]
        return best.token_id

    @staticmethod
    def _distance_to_finish_proxy(position: int, entry: int) -> int:
        if BoardConstants.is_home_column_position(position):
            return GameConstants.FINISH_POSITION - position
        if position <= entry:
            to_entry = entry - position
        else:
            to_entry = (GameConstants.MAIN_BOARD_SIZE - position) + entry
        return to_entry + GameConstants.HOME_COLUMN_SIZE

    # --- Helpers for progress and positions ---
    def _true_progress_ratio(self, ctx: AIDecisionContext) -> float:
        """My progress: finished + normalized home depth over tokens per player."""
        finished = ctx.player_state.finished_tokens
        home_depth_sum = 0.0
        for pos in ctx.player_state.positions_occupied:
            if BoardConstants.is_home_column_position(pos):
                home_depth_sum += (
                    pos - GameConstants.HOME_COLUMN_START
                ) / GameConstants.HOME_COLUMN_SIZE
        return (finished + home_depth_sum) / GameConstants.TOKENS_PER_PLAYER

    def _max_opponent_progress_ratio(self, ctx: AIDecisionContext) -> float:
        finished = 0
        for op_info in ctx.opponents:
            finished += op_info.finished_tokens
        opp_positions = get_opponent_main_positions(ctx)
        for pos in opp_positions:
            if BoardConstants.is_home_column_position(pos):
                finished += (
                    pos - GameConstants.HOME_COLUMN_START
                ) / GameConstants.HOME_COLUMN_SIZE
        return (
            finished / GameConstants.TOKENS_PER_PLAYER / len(ctx.opponents)
            if ctx.opponents
            else 0.0
        )
