"""Controller server module."""

from typing import Optional
import asyncio

import chess_robot_backend
from async_tcp_server import AsyncTCPServer


class ControllerException(Exception):
    """Represents an exception in the `ControllerServer` class."""


class ControllerServer:
    """Manages the connection to the robot controller and keeps the game state in sync."""

    def __init__(
            self,
            game: "chess_robot_backend.ChessRobotBackend",
            host: str = "localhost",
            port: int = 3000
    ):
        """
        Create a new controller server instance.

        :param game: The chess robot backend main class to sync the game state with.
        :param host: The host to bind to.
        :param port: The TCP port to listen on.
        """
        self._game = game
        self._host = host
        self._port = port
        self._server = AsyncTCPServer(host, port)

        self._response_available = asyncio.Condition()
        self._available_response: Optional[str] = None

    async def run(self):
        """Run this server. Must be scheduled as an async task."""
        print(f"Starting controller server on {self._host}:{self._port}.")
        print("Waiting for controller connection...")
        await self._server.start()
        await asyncio.gather(
            self._main_loop(),
            self._handle_messages()
        )

    async def _main_loop(self):
        while True:
            await self._game.wait_for_update()
            moves = self._game.pop_next_robot_moves()
            if not moves:
                continue
            try:
                # Reset error before first move.
                await self._game.set_error(None)
                while moves:
                    await self._perform_move(moves[0])
                    moves.pop(0)
            except ControllerException as e:
                failed_moves = ", ".join(moves)
                print(f"Controller could not perform move(s) {failed_moves}: {str(e)}")
                await self._game.set_error(
                    f"The robot could not perform the move \"{failed_moves}\". "
                    "Please perform the move manually.")

    async def _handle_messages(self):
        while True:
            message = None
            try:
                message = await self._server.async_receive()
            except ConnectionError as e:
                print(f"Could not receive message from controller: {str(e)}")
            if not message:
                print("Controller connection lost. Restarting server.")
                print("Waiting for controller connection...")
                await self._server.start()
                continue
            await self._handle_message(message)

    async def _handle_message(self, message: str):
        print("Controller message: " + message)
        if message.startswith("ok ") or message.startswith("error "):
            async with self._response_available:
                self._available_response = message
                self._response_available.notify_all()
            return
        parts = message.split(" ", 1)
        success = await self._handle_command(*parts)
        if success:
            await self._server.async_send("ok " + message)
        else:
            await self._server.async_send("error " + message)

    async def _handle_command(self, command: str, args: str = "") -> bool:
        if command == "updateRawBoard":
            if len(args) != 64:
                print("Error in setRawBoard command: Args must be 64 characters.")
                return False
            if any((c not in ["w", "b", "e"] for c in args)):
                print("Error in setRawBoard command: Args contains invalid characters.")
                return False
            raw_board = [list(args[i * 8: (i + 1) * 8]) for i in range(8)]
            print("Received raw board:\n" + "\n".join(" ".join(line) for line in raw_board))
            if self._game.is_game_started() and not self._game.is_human_turn():
                print("Controller error: Raw board is out of turn.")
                return False
            if not await self._game.update_raw_board(raw_board):
                print("Controller error: Raw board does not match a valid move.")
                await self._game.set_error("The robot could not recognize the move you played. "
                                           "Please repeat the move in the frontend or press the "
                                           "end of turn button to try again.")
                return False
            # Update successful -> reset error.
            await self._game.set_error(None)
            return True

        print("Unknown command: " + command)
        return False

    async def _wait_for_response(self, message: str):
        async with self._response_available:
            await self._response_available.wait_for(lambda: self._available_response is not None)
            response = self._available_response
            self._available_response = None

        if response == f"ok {message}":
            return
        if response == f"error {message}":
            raise ControllerException("Controller error")

        raise ControllerException(f"Unexpected controller response: \"{response}\"")

    async def _send_message(self, message: str):
        try:
            if not await self._server.async_send(message):
                raise ControllerException("Controller not connected")
        except ConnectionError as e:
            raise ControllerException(f"Could not send message to controller: {str(e)}") from e
        await self._wait_for_response(message)

    async def _perform_move(self, move: str):
        print(f"Robot: Performing move {move}")
        await self._send_message(f"move {move}")
