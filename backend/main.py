"""Chess robot backend entrypoint script."""

import asyncio

from chess_robot_backend import ChessRobotBackend
from controller_server import ControllerServer
from frontend_server import FrontendServer


async def main():
    """Main function for the chess robot backend. Initializes main class and servers."""
    frontend_host = "0.0.0.0"
    frontend_allow_origins = ["http://localhost:5173", "http://10.42.0.1"]

    chess_robot_backend = ChessRobotBackend()
    controller_server = ControllerServer(chess_robot_backend)
    frontend_server = FrontendServer(chess_robot_backend,
                                     host=frontend_host,
                                     allow_origins=frontend_allow_origins)

    await asyncio.gather(
        chess_robot_backend.run(),
        controller_server.run(),
        frontend_server.run()
    )


if __name__ == "__main__":
    asyncio.run(main())
