from unittest import IsolatedAsyncioTestCase
from dataclasses import dataclass, field
from typing import List
from copy import deepcopy

import pytest

from chess_robot_backend import ChessRobotBackend, Move
from game_manager import PerformedMove


class TestChessRobotBackend(IsolatedAsyncioTestCase):
    DEFAULT_INITIAL_POSITION: dict = {
        "a1": "wR", "b1": "wN", "c1": "wB", "d1": "wQ", "e1": "wK", "f1": "wB", "g1": "wN", "h1": "wR",
        "a2": "wP", "b2": "wP", "c2": "wP", "d2": "wP", "e2": "wP", "f2": "wP", "g2": "wP", "h2": "wP",
        "a7": "bP", "b7": "bP", "c7": "bP", "d7": "bP", "e7": "bP", "f7": "bP", "g7": "bP", "h7": "bP",
        "a8": "bR", "b8": "bN", "c8": "bB", "d8": "bQ", "e8": "bK", "f8": "bB", "g8": "bN", "h8": "bR",
    }

    @dataclass
    class ChessRobotBackendState:
        is_game_started: bool = False
        is_game_paused: bool = False
        is_running: bool = False
        is_human_turn: bool = False
        is_robot_turn: bool = False
        is_game_over: bool = False
        is_checkmate: bool = False
        is_draw: bool = False
        human_player_color: str = "w"
        initial_position: dict = field(default_factory=lambda: deepcopy(TestChessRobotBackend.DEFAULT_INITIAL_POSITION))
        current_position: dict = field(default_factory=lambda: deepcopy(TestChessRobotBackend.DEFAULT_INITIAL_POSITION))
        history: List[PerformedMove] = field(default_factory=list)

    def assertBackendStateEqual(self, expected: ChessRobotBackendState, backend: ChessRobotBackend):
        self.assertEqual(expected.is_game_started, backend.is_game_started(), "is_game_started() returned wrong value")
        self.assertEqual(expected.is_game_paused, backend.is_game_paused(), "is_game_paused() returned wrong value")
        self.assertEqual(expected.is_running, backend.is_running(), "is_running() returned wrong value")
        self.assertEqual(expected.is_human_turn, backend.is_human_turn(), "is_human_turn() returned wrong value")
        self.assertEqual(expected.is_robot_turn, backend.is_robot_turn(), "is_robot_turn() returned wrong value")
        self.assertEqual(expected.is_game_over, backend.is_game_over(), "is_game_over() returned wrong value")
        self.assertEqual(expected.is_checkmate, backend.is_checkmate(), "is_checkmate() returned wrong value")
        self.assertEqual(expected.is_draw, backend.is_draw(), "is_draw() returned wrong value")
        self.assertEqual(expected.human_player_color, backend.get_human_player_color(), "get_human_player_color() returned wrong value")
        self.assertDictEqual(expected.initial_position, backend.get_initial_position(), "get_initial_position() returned wrong value")
        self.assertDictEqual(expected.current_position, backend.get_current_position(), "get_current_position() returned wrong value")
        self.assertListEqual(expected.history, backend.get_history(), "get_history() returned wrong value")
        self.assertListEqual([], backend.pop_next_robot_moves(), "pop_next_robot_moves() returned unexpected robot moves")

    def set_raw_board_square(self, raw_board: List[List[str]], square: str, value: str):
        x = ord(square[:1]) - ord("a")
        y = ord(square[1:2]) - ord("1")
        raw_board[7 - y][x] = value

    async def test_frontend_game_human_plays_white_against_stockfish(self):
        backend = ChessRobotBackend()
        state = self.ChessRobotBackendState()
        self.assertBackendStateEqual(state, backend)

        # Start game.
        self.assertTrue(await backend.start_game())

        state.is_game_started = True
        state.is_running = True
        state.is_human_turn = True
        self.assertBackendStateEqual(state, backend)

        # Human move e2e4.
        self.assertTrue(await backend.make_move(Move("e2", "e4", promotion=None)))

        state.is_human_turn = False
        state.is_robot_turn = True
        state.current_position.pop("e2")
        state.current_position["e4"] = "wP"
        state.history.append(PerformedMove(from_square="e2", to_square="e4", promotion=None, san="e4"))
        self.assertBackendStateEqual(state, backend)

        # Agent move (stockfish).
        self.assertTrue(await backend.perform_agent_move())
        robot_move = backend.get_history()[-1]
        robot_move_str = robot_move.from_square + robot_move.to_square + " b"
        self.assertListEqual([robot_move_str], backend.pop_next_robot_moves())

        state.is_human_turn = True
        state.is_robot_turn = False
        state.current_position[robot_move.to_square] = state.current_position[robot_move.from_square]
        state.current_position.pop(robot_move.from_square)
        state.history.append(robot_move)
        self.assertBackendStateEqual(state, backend)

    async def test_frontend_game_human_plays_black_against_stockfish(self):
        backend = ChessRobotBackend()
        state = self.ChessRobotBackendState()
        self.assertBackendStateEqual(state, backend)

        # Set human player color.
        self.assertTrue(await backend.set_human_player_color("b"))

        state.human_player_color = "b"
        self.assertBackendStateEqual(state, backend)

        # Start game.
        self.assertTrue(await backend.start_game())

        state.is_game_started = True
        state.is_running = True
        state.is_robot_turn = True
        self.assertBackendStateEqual(state, backend)

        # Agent move (stockfish).
        self.assertTrue(await backend.perform_agent_move())
        robot_move = backend.get_history()[-1]
        robot_move_str = robot_move.from_square + robot_move.to_square + " w"
        self.assertListEqual([robot_move_str], backend.pop_next_robot_moves())

        state.is_human_turn = True
        state.is_robot_turn = False
        state.current_position[robot_move.to_square] = state.current_position[robot_move.from_square]
        state.current_position.pop(robot_move.from_square)
        state.history.append(robot_move)
        self.assertBackendStateEqual(state, backend)

    @pytest.mark.xfail(reason="Known bug in GameManager")
    async def test_frontend_game_human_plays_white_against_manual(self):
        backend = ChessRobotBackend()
        state = self.ChessRobotBackendState()
        self.assertBackendStateEqual(state, backend)

        # Start game.
        self.assertTrue(await backend.start_game())

        state.is_game_started = True
        state.is_running = True
        state.is_human_turn = True
        self.assertBackendStateEqual(state, backend)

        # Human move d2d4.
        self.assertTrue(await backend.make_move(Move("d2", "d4", promotion=None)))

        state.is_human_turn = False
        state.is_robot_turn = True
        state.current_position.pop("d2")
        state.current_position["d4"] = "wP"
        state.history.append(PerformedMove(from_square="d2", to_square="d4", promotion=None, san="d4"))
        self.assertBackendStateEqual(state, backend)

        # Agent move c7c5 (manual).
        # TODO does not work
        self.assertTrue(await backend.make_move(Move("c7", "c5", promotion=None)))
        self.assertListEqual(["c7c5 b"], backend.pop_next_robot_moves())

        state.is_human_turn = True
        state.is_robot_turn = False
        state.current_position.pop("c7")
        state.current_position["c5"] = "bP"
        state.history.append(PerformedMove(from_square="c7", to_square="c5", promotion=None, san="c5"))
        self.assertBackendStateEqual(state, backend)

    async def test_controller_game_human_plays_white_against_stockfish(self):
        backend = ChessRobotBackend()
        state = self.ChessRobotBackendState()
        self.assertBackendStateEqual(state, backend)

        # Human move f2f4.
        raw_board = [
            ['w', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],  # Rank 1 (h1–a1)
            ['w', 'w', 'e', 'w', 'w', 'w', 'w', 'w'],  # Rank 2 (h2–a2)
            ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'],  # Rank 3
            ['e', 'e', 'w', 'e', 'e', 'e', 'e', 'e'],  # Rank 4
            ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'],  # Rank 5
            ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'],  # Rank 6
            ['b', 'b', 'b', 'b', 'b', 'b', 'b', 'b'],  # Rank 7 (h7–a7)
            ['b', 'b', 'b', 'b', 'b', 'b', 'b', 'b'],  # Rank 8 (h8–a8)
        ]
        self.assertTrue(await backend.update_raw_board(deepcopy(raw_board)))

        state.is_game_started = True
        state.is_running = True
        state.is_robot_turn = True
        state.current_position.pop("f2")
        state.current_position["f4"] = "wP"
        state.history.append(PerformedMove(from_square="f2", to_square="f4", promotion=None, san="f4"))
        self.assertBackendStateEqual(state, backend)

        # Agent move (stockfish).
        self.assertTrue(await backend.perform_agent_move())
        robot_move = backend.get_history()[-1]
        robot_move_str = robot_move.from_square + robot_move.to_square + " b"
        self.assertListEqual([robot_move_str], backend.pop_next_robot_moves())

        state.is_human_turn = True
        state.is_robot_turn = False
        state.current_position[robot_move.to_square] = state.current_position[robot_move.from_square]
        state.current_position.pop(robot_move.from_square)
        state.history.append(robot_move)
        self.assertBackendStateEqual(state, backend)

    async def test_controller_game_human_plays_black_against_stockfish(self):
        backend = ChessRobotBackend()
        state = self.ChessRobotBackendState()
        self.assertBackendStateEqual(state, backend)

        # Initial raw board without human move.
        raw_board = [
            ['b', 'b', 'b', 'b', 'b', 'b', 'b', 'b'],  # Rank 8 (a8–h8)
            ['b', 'b', 'b', 'b', 'b', 'b', 'b', 'b'],  # Rank 7 (a7–h7)
            ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'],  # Rank 6
            ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'],  # Rank 5
            ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'],  # Rank 4
            ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'],  # Rank 3
            ['w', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],  # Rank 2 (a2–h2)
            ['w', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],  # Rank 1 (a1–h1)
        ]
        self.assertTrue(await backend.update_raw_board(deepcopy(raw_board)))

        state.is_game_started = True
        state.is_running = True
        state.is_robot_turn = True
        state.human_player_color = "b"
        self.assertBackendStateEqual(state, backend)

        # Agent move (stockfish).
        self.assertTrue(await backend.perform_agent_move())
        robot_move = backend.get_history()[-1]
        robot_move_str = robot_move.from_square + robot_move.to_square + " w"
        self.assertListEqual([robot_move_str], backend.pop_next_robot_moves())

        state.is_human_turn = True
        state.is_robot_turn = False
        state.current_position[robot_move.to_square] = state.current_position[robot_move.from_square]
        state.current_position.pop(robot_move.from_square)
        self.set_raw_board_square(raw_board, robot_move.from_square, "e")
        self.set_raw_board_square(raw_board, robot_move.to_square, "w")
        state.history.append(robot_move)
        self.assertBackendStateEqual(state, backend)

        # Human move a7a6.
        self.set_raw_board_square(raw_board, "a7", "e")
        self.set_raw_board_square(raw_board, "a6", "b")
        self.assertTrue(await backend.update_raw_board(deepcopy(raw_board)))

        state.is_human_turn = False
        state.is_robot_turn = True
        state.current_position.pop("a7")
        state.current_position["a6"] = "bP"
        state.history.append(PerformedMove(from_square="a7", to_square="a6", promotion=None, san="a6"))
        self.assertBackendStateEqual(state, backend)

    async def test_set_initial_position(self):
        backend = ChessRobotBackend()
        state = self.ChessRobotBackendState()
        self.assertBackendStateEqual(state, backend)

        # Changes to initial position should immediately apply to current position.
        state.initial_position["c5"] = "wP"
        state.current_position["c5"] = "wP"
        self.assertTrue(await backend.set_initial_position(deepcopy(state.initial_position)))

        self.assertBackendStateEqual(state, backend)

        self.assertTrue(await backend.start_game())

        state.initial_position["d5"] = "wP"
        self.assertFalse(await backend.set_initial_position(deepcopy(state.initial_position)))

    @pytest.mark.xfail(reason="Known bug in GameManager")
    async def test_set_history(self):
        backend = ChessRobotBackend()
        state = self.ChessRobotBackendState()
        self.assertBackendStateEqual(state, backend)

        # Cannot set history when game is not started.
        self.assertFalse(await backend.set_history([]))
        self.assertBackendStateEqual(state, backend)

        self.assertTrue(await backend.start_game())
        state.is_game_started = True
        state.is_running = True
        state.is_human_turn = True

        # Cannot set history when game is not paused.
        self.assertFalse(await backend.set_history([]))
        self.assertBackendStateEqual(state, backend)

        self.assertTrue(await backend.set_game_paused(True))
        state.is_game_paused = True
        state.is_running = False
        state.is_human_turn = False

        # Setting empty history in new game should be a no-op.
        self.assertTrue(await backend.set_history([]))
        self.assertBackendStateEqual(state, backend)

        self.assertTrue(await backend.set_history([
            Move("a2", "a4", promotion=None),
            Move("g7", "g5", promotion=None),
        ]))

        state.is_human_turn = False
        state.is_robot_turn = True
        state.current_position.pop("a2")
        state.current_position["a4"] = "wP"
        state.current_position.pop("g7")
        state.current_position["g5"] = "bP"
        state.history = [
            PerformedMove("a2", "a4", promotion=None, san="a4"),
            PerformedMove("g7", "g5", promotion=None, san="g5"),
        ]
        self.assertBackendStateEqual(state, backend)

    async def test_new_game(self):
        backend = ChessRobotBackend()
        state = self.ChessRobotBackendState()
        self.assertBackendStateEqual(state, backend)

        await backend.new_game()
        self.assertBackendStateEqual(state, backend)

        # new_game() should reset started game back to initial state.
        self.assertTrue(await backend.start_game())
        self.assertTrue(await backend.make_move(Move("h2", "h3", promotion=None)))
        await backend.new_game()
        self.assertBackendStateEqual(state, backend)

        # new_game() should reset ended game back to initial state.
        self.assertTrue(await backend.start_game())
        self.assertTrue(await backend.end_game())
        await backend.new_game()
        self.assertBackendStateEqual(state, backend)

        # Changes to the initial position should NOT be persisted on new_game().
        initial_position = deepcopy(state.initial_position)
        initial_position["c5"] = "wP"
        self.assertTrue(await backend.set_initial_position(initial_position))
        await backend.new_game()
        self.assertBackendStateEqual(state, backend)

        # Changes to the board orientation should be persisted on new_game().
        self.assertTrue(await backend.set_human_player_color("b"))
        state.human_player_color = "b"
        await backend.new_game()
        self.assertBackendStateEqual(state, backend)
