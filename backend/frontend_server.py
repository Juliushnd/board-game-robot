"""Frontend Server module."""

import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import chess_robot_backend


class JsonModel(BaseModel):
    """Base model for models being converted from and to JSON."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True
    )


class JsonMove(JsonModel):
    """Represents a chess move."""

    from_square: str = Field(alias="from")
    """The start square of the move. Must be between `"a1"` and `"h8"`."""
    to_square: str = Field(alias="to")
    """The end square of the move. Must be between `"a1"` and `"h8"`."""
    promotion: Optional[str] = Field(None)
    """
    The promotion piece type as a lower-case letter if there has been a promotion, `None` otherwise.
    """


class JsonMoveWithColor(JsonMove):
    """Represents a chess move with the color of the player whose move it is."""

    color: str
    """The player's color. Must be one of `"b"` and `"w"`."""

class JsonMoveWithSAN(JsonMove):
    """Represents a chess move with SAN."""

    san: str
    """The move in Standard Algebraic Notation (SAN)."""


class JsonChessAgent(JsonModel):
    """Represents a chess agent choosable in the frontend and convertible to JSON."""

    key: str
    """A unique key to identify the agent."""
    name: str
    """The agent's name to display to the human."""
    allow_frontend_moves: bool
    """Whether the frontend is allowed to perform moves for this agent."""


class JsonGameState(JsonModel):
    """
    Represents the game state as expected by the frontend.

    All fields must have a default value so that this model can be used to parse PATCH requests to
    /game (see `update_game()`).
    """

    initial_position: Optional[dict] = Field(None)
    """The initial position as described in `ChessRobotBackend.get_current_position()`."""
    current_position: Optional[dict] = Field(None)
    """The current position as described in `ChessRobotBackend.get_current_position()`."""
    current_player_color: str = Field("w")
    """The current player's color. Must be one of `"b"` and `"w"`."""
    human_player_color: str = Field("w")
    """The human player's color. Must be one of `"b"` and `"w"`."""
    available_agents: List[JsonChessAgent] = Field([])
    """The list of agents to choose from."""
    agent: Optional[str] = Field(None)
    """The key of the currently selected agent."""
    history: List[JsonMoveWithSAN] = Field([])
    """The game history as a list of moves including SAN."""
    game_started: bool = Field(False)
    """Whether the game has been started."""
    game_paused: bool = Field(False)
    """Whether the game has been paused."""
    game_over: bool = Field(False)
    """Whether the game has ended."""
    is_draw: bool = Field(False)
    """Whether the game has ended by draw."""
    is_checkmate: bool = Field(False)
    """Whether the game has ended by checkmate."""
    error: Optional[str] = Field(None)
    """The error message to display in the frontend, or `None` if there is none."""


class FrontendServer:
    """Manages the connection to the frontend(s) and keeps the game state in sync."""

    def __init__(
            self,
            game: "chess_robot_backend.ChessRobotBackend",
            host: str = "localhost",
            port: int = 8000,
            allow_origins: Optional[List[str]] = None
    ):
        """
        Create a new frontend server instance.

        :param game: The chess robot backend main class to sync the game state with.
        :param host: The host to bind to.
        :param port: The HTTP port to listen on.
        :param allow_origins: The list of origins to allow.
        """
        self.game = game
        self.host = host
        self.port = port
        self.websocket_handlers: List[asyncio.Task] = []

        self.app = FastAPI()
        if allow_origins is not None:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=allow_origins,
                allow_methods=["*"],
            )
        self._define_routes()

    def _define_routes(self):
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            # Create a task to handle the WebSocket connection (i.e., send state updates to the
            # client).
            websocket_handler = asyncio.create_task(self._handle_websocket(websocket))
            self.websocket_handlers.append(websocket_handler)
            print(f"WebSocket connected ({len(self.websocket_handlers)} connected)")
            try:
                while True:
                    # Create a second task which receives data from the WebSocket.
                    # This task failing means that the WebSocket connection was closed.
                    receive_task = asyncio.create_task(websocket.receive())
                    # Wait for either of the two tasks to complete.
                    await asyncio.wait(
                        [websocket_handler, receive_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    # If the handler task is done, an exception must have occurred.
                    # -> We can close the WebSocket.
                    if websocket_handler.done():
                        await websocket.close(reason="Backend error")
                        if websocket_handler.exception():
                            # Re-raise exception.
                            raise websocket_handler.exception()
                        break
                    # If the receive task has failed, the WebSocket connection was closed.
                    # -> We can cancel the handler task.
                    if receive_task.done() and receive_task.exception():
                        websocket_handler.cancel()
                        break
            finally:
                self.websocket_handlers.remove(websocket_handler)
                print(f"WebSocket disconnected ({len(self.websocket_handlers)} connected)")

        @self.app.get("/game")
        async def get_game() -> JsonGameState:
            return self._export_state()

        @self.app.delete("/game")
        async def new_game():
            await self.game.new_game()

        @self.app.patch("/game")
        async def update_game(updated_state: JsonGameState):
            updated_fields = updated_state.model_dump(exclude_unset=True, by_alias=False)
            print("Received update:", updated_fields)
            for key in updated_fields:
                match key:
                    case "initial_position":
                        if not await self.game.set_initial_position(updated_state.initial_position):
                            raise HTTPException(status_code=400, detail="Invalid initial position")
                    case "human_player_color":
                        if not await self.game.set_human_player_color(
                                updated_state.human_player_color):
                            raise HTTPException(status_code=400,
                                                detail="Could not change human player color")
                    case "agent":
                        if not await self.game.set_agent(updated_state.agent):
                            raise HTTPException(status_code=400, detail="Invalid agent")
                    case "game_started":
                        if updated_state.game_started and not self.game.is_game_started():
                            if not await self.game.start_game():
                                raise HTTPException(status_code=400, detail="Could not start game")
                    case "game_paused":
                        if not await self.game.set_game_paused(updated_state.game_paused):
                            raise HTTPException(status_code=400, detail="Could not pause game")
                    case "game_over":
                        if updated_state.game_over and not self.game.is_game_over():
                            if not await self.game.end_game():
                                raise HTTPException(status_code=400, detail="Could not end game")
                    case "error":
                        if updated_state.error is not None:
                            raise HTTPException(status_code=400, detail="Can only reset error")
                        await self.game.set_error(None)

        @self.app.put("/game/history")
        async def set_history(history: List[JsonMove]):
            moves = [
                chess_robot_backend.Move(
                    from_square=move.from_square,
                    to_square=move.to_square,
                    promotion=move.promotion
                ) for move in history
            ]
            if not await self.game.set_history(moves):
                raise HTTPException(status_code=400, detail="Invalid history")

        @self.app.post("/game/history")
        async def make_move(move: JsonMoveWithColor):
            if self.game.get_current_player_color() != move.color:
                raise HTTPException(status_code=400, detail="Out of sync. Please reload the page.")
            if not self.game.is_running():
                raise HTTPException(status_code=400, detail="The game is not running.")
            if self.game.is_robot_turn() and self.game.get_agent() \
                    and not self._allow_frontend_moves(self.game.get_agent()):
                raise HTTPException(status_code=400, detail="Not allowed to make agent moves.")
            move = chess_robot_backend.Move(
                from_square=move.from_square,
                to_square=move.to_square,
                promotion=move.promotion
            )
            if not await self.game.make_move(move):
                raise HTTPException(status_code=400, detail="Illegal move.")

    async def run(self):
        """Run this server. Must be scheduled as an async task."""
        print(f"Starting frontend server on {self.host}:{self.port}")
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port
        )
        server = uvicorn.Server(config=config)
        await server.serve()

    async def _handle_websocket(self, websocket: WebSocket):
        try:
            while True:
                await websocket.send_text(self._export_state().model_dump_json())
                await self.game.wait_for_update()
        except asyncio.CancelledError:
            pass

    def _allow_frontend_moves(self, agent: chess_robot_backend.ChessAgent) -> bool:
        return agent.type in [chess_robot_backend.ChessAgentType.MANUAL]

    def _export_state(self):
        return JsonGameState(
            initial_position=self.game.get_initial_position(),
            current_position=self.game.get_current_position(),
            current_player_color=self.game.get_current_player_color(),
            human_player_color=self.game.get_human_player_color(),
            available_agents=[JsonChessAgent(
                key=agent.key,
                name=agent.name,
                allow_frontend_moves=self._allow_frontend_moves(agent)
            ) for agent in self.game.get_available_agents()],
            agent=self.game.get_agent().key if self.game.get_agent() else None,
            history=[JsonMoveWithSAN(
                from_square=move.from_square,
                to_square=move.to_square,
                promotion=move.promotion,
                san=move.san,
            ) for move in self.game.get_history()],
            game_started=self.game.is_game_started(),
            game_paused=self.game.is_game_paused(),
            game_over=self.game.is_game_over(),
            is_draw=self.game.is_draw(),
            is_checkmate=self.game.is_checkmate(),
            error=self.game.get_error()
        )
