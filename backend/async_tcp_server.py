"""Async TCP Server backend"""
import asyncio


class AsyncTCPServer:
    """Async TCP server Class for backend communication"""
    def __init__(self, host: str = "localhost",port: int = 3000):
        self._host = host
        self._port = port
        self._server = None
        self._read_socket= None
        self._write_socket = None
        self.running = False

    async def start(self):
        """Start the server and wait for a client to connect."""
        await self.stop()

        connected = asyncio.Event()

        def on_connect(read_socket: asyncio.StreamReader, write_socket: asyncio.StreamWriter):
            """Callback function when a client connects."""
            print("Connection received")
            # Disconnect previous client
            try:
                if self._write_socket:
                    self._write_socket.close()
            except ConnectionError:
                pass
            self._read_socket = read_socket
            self._write_socket = write_socket
            self.running = True
            connected.set()

        self._server = await asyncio.start_server(on_connect, self._host, self._port)
        await connected.wait()

    async def async_send(self, line: str):
        """Send a line to the connected client."""
        if self.running:
            line += "\n"
            self._write_socket.write(line.encode())
            await self._write_socket.drain()
            return True
        return False

    async def async_receive(self):
        """Async function for receiving data"""
        if self.running:
            buffer = b""
            while True:
                char = await self._read_socket.read(1)
                if not char:
                    break  # Verbindung geschlossen
                if char == b"\n":
                    break
                buffer += char
            response = buffer.decode('utf-8')
            return response
        return ""

    async def stop(self):
        """stop server!"""
        if not self.running:
            return
        self.running = False
        try:
            if self._write_socket:
                self._write_socket.close()
                await self._write_socket.wait_closed()
        except ConnectionError:
            pass
        try:
            if self._server:
                self._server.close()
                await self._server.wait_closed()
        except ConnectionError:
            pass
