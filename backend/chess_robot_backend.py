"""Chess Robot Backend module."""

import asyncio
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum

from game_manager import GameManager, Move, PerformedMove


class ChessAgentType(Enum):
    """Represents a chess agent type."""

    MANUAL = 1
    STOCKFISH = 2


@dataclass
class ChessAgent:
    """Represents a chess agent choosable in the frontend."""

    key: str
    """A unique key to identify the agent."""
    type: ChessAgentType
    """The type of agent."""
    name: str
    """The agent's name to display to the human."""
    stockfish_elo: int = 0
    """The ELO rating to approximate (for agents of type `STOCKFISH`)."""


class ChessRobotBackend:
    """Chess Robot backend main class.

    This class manages a `GameManager` object and exposes certain function to access and modify its
    state. Whenever the game state is modified by any external or internal cause, all calls which
    are currently awaiting the method `wait_for_update()` will return. This can be used to sync the
    game state with an external component (like the frontend and controller).

    This class does not make any connections to other components by itself. This falls into the
    responsibility of the `FrontendServer` and `ControllerServer` classes.

    The `run()` method must be scheduled as an async task in order for this class to work properly.
    """

    def __init__(self):
        self._game = GameManager()

        self._available_agents: List[ChessAgent] = [
            ChessAgent(
                key="stockfish_weak",
                type=ChessAgentType.STOCKFISH,
                name="Stockfish (weak)",
                stockfish_elo=1320),
            ChessAgent(
                key="stockfish_medium",
                type=ChessAgentType.STOCKFISH,
                name="Stockfish (medium)",
                stockfish_elo=2200),
            ChessAgent(
                key="stockfish_strong",
                type=ChessAgentType.STOCKFISH,
                name="Stockfish (strong)",
                stockfish_elo=3190),
            ChessAgent(
                key="manual",
                type=ChessAgentType.MANUAL,
                name="Manual")
        ]
        self._agent: Optional[ChessAgent] = next(iter(self._available_agents), None)
        self._game_started = False
        self._game_paused = False
        self._game_over = False
        self._error: Optional[str] = None

        self._state_changed = asyncio.Condition()
        self._game.set_up_game()

    async def run(self):
        """Run this game's main loop. Must be scheduled as an async task."""
        while True:
            await self.wait_for_update()
            if not self.is_robot_turn() or not self.get_agent():
                continue
            await self.perform_agent_move()

    async def wait_for_update(self):
        """
        Wait for something to change in the game state.

        Callers should always check whether the condition they are waiting for is actually met when
        this method returns.
        """
        async with self._state_changed:
            await self._state_changed.wait()

    async def new_game(self):
        """
        Reset the game to the beginning.

        This does NOT reset the human player color. It does reset the initial position, however.
        """
        async with self._state_changed:
            self._game_started = False
            self._game_paused = False
            self._game_over = False
            self._game.reset_game()
            self._game.set_up_game()
            self._state_changed.notify_all()

    async def set_initial_position(self, position: dict) -> bool:
        """
        Set the initial position. Only possible before the game has started.

        :param position: A position dict in the form described in `get_current_position()`.
        :return: Whether the provided position is valid and has been applied successfully.
        """
        if self._game_started:
            return False
        async with self._state_changed:
            previous = self.get_initial_position()
            self._game.set_up_game(position)
            success = self._game.is_starting_board_legal()
            if not success:
                self._game.set_up_game(previous)  # Restore previous value.
            self._state_changed.notify_all()
            return success

    def get_initial_position(self) -> dict:
        """
        Get the initial position.

        :return: A position dict in the form described in `get_current_position()`.
        """
        return self._game.get_initial_position_dict()

    def get_current_position(self) -> dict:
        """
        Get the current position.

        The position is represented as a dict in the form `{"<square>": "<piece>"}` where `<square>`
        is a chess square between `"a1"` and `"h8"` and `<piece>` is a chess piece in the form
        `"<color><type>"`, with `<color>` being one of `"b"` and `"w"` and `<type>` being character
        describing the piece type as an upper case letter. Example: `{"b2": "wP", "g8": "bN", ...}`

        :return: The current position dict.
        """
        return self._game.get_current_position_dict()

    async def set_human_player_color(self, color: str) -> bool:
        """
        Set the human player color. Only possible before the game has started.

        :param color: The color which the human player will play as. Must be one of `"b"` and `"w"`.
        :return: Whether the provided color is valid and has been applied successfully.
        """
        if self._game_started:
            return False
        if color not in ["w", "b"]:
            print("Invalid color:", color)
            return False
        self._game.set_human_player_color(color)
        async with self._state_changed:
            self._state_changed.notify_all()
        return True

    def get_human_player_color(self) -> str:
        """
        Get the human player color.

        :return: One of `"b"` and `"w"`.
        """
        return self._game.get_human_player_color()

    def get_available_agents(self) -> List[ChessAgent]:
        """
        Get the list of available agents to choose from.

        :return: The list of agents. This must not be mutated!
        """
        return self._available_agents

    async def set_agent(self, agent_key: str) -> bool:
        """
        Set the active agent.

        :param agent_key: The key of the agent to activate. Must be one a key of one of the
        agents from `get_available_agents()`.
        :return: Whether the agent key is valid and the agent has been activated successfully.
        """
        agent = next((a for a in self.get_available_agents() if a.key == agent_key), None)
        if agent is None:
            return False
        self._agent = agent
        async with self._state_changed:
            self._state_changed.notify_all()
        return True

    def get_agent(self) -> Optional[ChessAgent]:
        """
        Get the active agent.

        :return: The active agent or `None` if no agent is active.
        """
        return self._agent

    async def start_game(self) -> bool:
        """
        Start the game.

        :return: `True` if the game has been started, `False` if it had already been running.
        """
        if self._game_started:
            return False
        self._game_started = True
        # If human plays as black, we need to call apply_player_move_ui() once without a move to
        # start the game.
        if self._game.get_human_player_color() == "b":
            self._game.apply_player_move_ui(None)
        async with self._state_changed:
            self._state_changed.notify_all()
        return True

    def is_game_started(self) -> bool:
        """
        Return whether the game has been started.

        :return: `True` if the game has been started, `False` otherwise.
        """
        return self._game_started

    def get_current_player_color(self) -> str:
        """
        Get the color of the current player.

        :return: One of `"b"` and `"w"`.
        """
        return self._game.get_current_player_color()

    async def set_game_paused(self, paused: bool) -> bool:
        """
        Pause or unpause the game. Only works if the game has been started.

        :param paused: Whether the game should be paused or unpaused.
        :return: `True` if the game was paused or unpaused successfully, `False` if it has not been
        started.
        """
        if not self._game_started:
            return False
        async with self._state_changed:
            self._game_paused = paused
            self._state_changed.notify_all()
            return True

    def is_game_paused(self) -> bool:
        """
        Return whether the game has been paused.

        :return: `True` if the game has been paused, `False` otherwise.
        """
        return self._game_paused

    async def make_move(self, move: Move) -> bool:
        """
        Perform a move as the current player. Only works when the game is running.

        :param move: The move to apply.
        :return: Whether the move was valid and has been successfully applied.
        """
        if not self.is_running():
            return False
        async with self._state_changed:
            performed_move = self._game.apply_player_move_ui(move)
            if performed_move is None:
                return False
            print("Performed move:", performed_move)
            if self._game.is_game_over():
                self._game_over = True
            self._state_changed.notify_all()
        return True

    async def perform_agent_move(self) -> bool:
        """
        Calculate and apply a move as the currently active agent.

        This will return `False` if it's not the agent's turn or if the agent does not calculate
        moves by itself (e.g. "manual" mode).

        :return: Whether the move was calculated and applied successfully.
        """
        agent = self.get_agent()
        if not self.is_robot_turn() or not agent:
            return False

        print(f"Performing agent move (selected agent: {agent.key})")
        match agent.type:
            case ChessAgentType.STOCKFISH:
                await asyncio.sleep(0)  # Wait for other tasks to finish before blocking the thread.
                async with self._state_changed:
                    # Recheck whether it's the robot's turn after waiting.
                    if not self.is_robot_turn() or not agent:
                        return False
                    # Calculate move using stockfish.
                    if not self._game.set_stockfish_elo(agent.stockfish_elo):
                        print("Invalid stockfish ELO: " + str(agent.stockfish_elo))
                        return False
                    self._game.calculate_raw_next_move()  # This is blocking.
                    move = self._game.get_next_move_ui()
                    print(f"Agent chose move {move}")
                    if self._game.is_game_over():
                        self._game_over = True
                    self._state_changed.notify_all()
                return True
            case _:
                return False

    async def update_raw_board(self, raw_board: List[List[str]]) -> bool:
        """
        Process an update of the raw board as observed by the robot.

        This should be called exactly once per player turn, if the player is playing against the
        physical robot. This method starts the game if it has not been started, yet.

        :param raw_board: An 8x8 array containing only the strings `"e"`, `"b"`, and `"w"`.
        :return: Whether the update was processed successfully.
        """
        if self._game_over:
            return False

        async with self._state_changed:
            if self.get_human_player_color() == "w":
                # Human is playing as white -> we need to flip the raw board.
                raw_board = [line[::-1] for line in raw_board[::-1]]
            if not self._game.update_raw_board(raw_board):
                return False
            self._game_started = True
            if self._game.is_game_over():
                self._game_over = True

            self._state_changed.notify_all()
        return True

    def pop_next_robot_moves(self) -> List[str]:
        """
        Get the list of moves for the robot to perform next.

        :return: The list of move strings.
        """
        return self._game.get_next_move_robot()

    async def set_history(self, history: List[Move]) -> bool:
        """
        Override the game history. Only works when the game is paused.

        This does not generate any new robot moves. The given list of moves is expected to reflect
        the real world events. This can be used to correct errors in the game history caused by an
        incorrectly classified move.

        :param history: The new list of moves starting from the initial position.
        :return: Whether all moves were valid and have been successfully applied.
        """
        if not self._game_started or not self._game_paused:
            return False
        async with self._state_changed:
            result = self._game.set_move_history(moves=history, override_last_raw_board=True)

            self._state_changed.notify_all()
            return result

    def get_history(self) -> List[PerformedMove]:
        """
        Get the list of moves performed since the game has been started.

        :return: The list of moves (including SAN).
        """
        return self._game.get_move_history_ui()

    async def end_game(self) -> bool:
        """
        End the game. Only works if it is currently running.

        :return: Whether the game has been ended successfully.
        """
        if not self._game_started or self._game_over:
            return False
        async with self._state_changed:
            self._game_over = True
            self._state_changed.notify_all()
        return True

    def is_game_over(self) -> bool:
        """
        Return whether the game has ended (either by checkmate, draw, or by calling `end_game()`).

        :return: Whether the game is over.
        """
        return self._game_over

    def is_running(self) -> bool:
        """
        Return whether the game is running (and not paused).

        :return: Whether the game is running.
        """
        return self._game_started and not self._game_paused and not self._game_over

    def is_human_turn(self) -> bool:
        """
        Return whether it's currently the human's turn (and the game is not paused).

        :return: Whether it's the human's turn.
        """
        if not self.is_running():
            return False
        return self._game.get_current_player_color() == self.get_human_player_color()

    def is_robot_turn(self) -> bool:
        """
        Return whether it's currently the robot's turn (and the game is not paused).

        :return: Whether it's the robot's turn.
        """
        if not self.is_running():
            return False
        return self._game.get_current_player_color() != self.get_human_player_color()

    def is_checkmate(self) -> bool:
        """
        Return whether the game has ended by checkmate.

        :return: Whether there has been a checkmate.
        """
        return self._game.is_checkmate()

    def is_draw(self) -> bool:
        """
        Return whether the game has ended by draw.

        :return: Whether there has been a draw.
        """
        return self._game.is_game_draw()

    async def set_error(self, error: Optional[str]):
        """
        Set the error to be displayed in the frontend.

        :param error: The error message or `None` to reset it.
        """
        async with self._state_changed:
            self._error = error
            self._state_changed.notify_all()

    def get_error(self) -> Optional[str]:
        """
        Get the current error message.

        :return: The current error message or `None` if there is none.
        """
        return self._error
