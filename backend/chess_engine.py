"""
The whole module was created by Maxim Scholtz

The module only consists of the ChessEngine class and the MoveResultType Enum which differentiate between move results
    returned by stockfish

"""
from enum import Enum
from typing import Tuple
from typing import List
import copy
import chess
from stockfish import Stockfish


class MoveResultType(Enum):
    """
    The enum class which differentiate between move results
    """
    ERROR = "error"
    MOVE = "move"
    GAME_END = "game_end"


class ChessEngine:
    """
    The ChessEngine class is used to check for legality of played moves and to calculate the best next move to play
    """

    def __init__(
        self,
        stockfish_path: str = "stockfish",
        #threads: int = 1,
        #hash_size: int = 64,
        #ponder: bool = False,
        #depth: int = 10,
        #time_ms: int = 2000,
    ):
        # Initialize the board and Stockfish engine
        self._board = None
        self._moves_uci = []
        self._moves_san = []

        self._starting_position_fen = None

        self._elo_rating = 1320

        self._engine = Stockfish(
            path=stockfish_path,
            parameters={
                "UCI_LimitStrength": True,
                "UCI_Elo": 1320
            },
        )

        self._engine.set_elo_rating(self._elo_rating)


    def start_game(self, board: str):
        """
        This function has to be called before playing the first move
        It sets the starting board
        :param board: The chosen starting board
        """
        self._board = chess.Board(board)
        self._engine.set_fen_position(board)
        self._starting_position_fen = board

    def get_next_move(self) -> Tuple[MoveResultType, str]:
        """
        This function gets a move in UCI notation and no more information
            The board is set up before such that the starting position of the pieces is known

        The move is then checked for legality by chess lib
            In case of an illegal move the return is: (ILLEGAL_MOVE, "error message or the repeated move tbs")TODO

        If the move is legal the move is send to stockfish
            If stockfish return game ended the return is: (GAME_END, "winner announcement")

        Stockfish returns the best move
            If the best move end the game the return is: (GAME_END, "winner announcement")

        return (MOVE, "move in UCI")

        if at any point an error occurs the return is: (ERROR, "error message")


        :param player_move: Opponent's move in UCI notation (e.g. 'e2e4').
        :return: Tuple of (MoveResultType, move_or_message).
        """

        # Check if game is started already
        if not self._board:
            return (MoveResultType.ERROR, "Board is not set up.")

        # Check if game over after player move
        if self._board.is_game_over():
            return (MoveResultType.GAME_END, self._board.result())

        # Update engine position and get best move
        # We set the starting position again because set_position() overrides the starting position
        self._engine.set_fen_position(self._starting_position_fen)
        self._engine.make_moves_from_current_position(self._moves_uci)

        best_move = self._engine.get_best_move()

        if not best_move:
            return (MoveResultType.ERROR, "Stockfish did not return a move.")

        # Apply engine's move
        move = self._board.parse_uci(best_move)
        san = self._board.san_and_push(move)
        self._moves_uci.append(best_move)
        self._moves_san.append(san)

        # Check if game over after engine move
        if self._board.is_game_over():
            return (MoveResultType.GAME_END, best_move)

        return (MoveResultType.MOVE, best_move)

    def apply_player_move(self, player_move: str) -> bool:
        """
        Checks whether the given move is legal or not and applies the move if legal
        :param player_move:  move in UCI notation (e.g. 'e2e4').
        :return: True if the move is legal, False otherwise.
        """
        # Validate player's move
        try:
            move = self._board.parse_uci(player_move)
        except ValueError:
            return False

        # Apply player's move
        san = self._board.san_and_push(move)
        self._moves_uci.append(move.uci())
        self._moves_san.append(san)

        return True

    def get_current_board_fen(self) -> str:
        """
        :return: current board in fen notation
        """
        return self._board.fen()

    def get_current_board_engine_fen(self) -> str:
        """
        :return: current board stored in the engine in fen notation
        """
        return self._engine.get_fen_position()

    def get_moves_history_san(self) -> List[str]:
        """
        :return: move history in SAN notation
        """
        return self._moves_san

    def get_moves_history_uci(self) -> List[str]:
        """
        :return: move history in UCI notation
        """
        return self._moves_uci

    def get_most_recent_move_san(self) -> str:
        """
        :return: last stored move in san notation
        """
        return self._moves_san[-1]

    def get_piece_at(self, square: str) -> str | None:
        """
        Checks if and which piece is at the given square
        :param square: to check for piece
        :return: piece at given square (e.g. wB)
        """
        piece = self._board.piece_at(chess.parse_square(square))
        if piece is None:
            return None
        color = "w" if piece.color == chess.WHITE else "b"
        piece_type = chess.piece_symbol(piece.piece_type).upper()
        return color + piece_type

    def get_most_recent_move_type(self) -> str:
        """
        Extracts the move type of the last applied move
        :return: {castling,en_passant,capture/promotion,capture,normal}
        """
        board_copy: chess.Board = copy.deepcopy(self._board)
        # SAN of previous move is not valid in current context -> undo previous move first.
        board_copy.pop()
        move = board_copy.parse_san(self._moves_san[-1])
        if board_copy.is_castling(move):
            return "castling"

        if board_copy.is_en_passant(move):
            return "en_passant"

        if move.promotion is not None and board_copy.is_capture(move):
            return "capture/promotion"

        if move.promotion is not None:
            return "promotion"

        if board_copy.is_capture(move):
            return "capture"

        return "normal"

    def reset_standard(self):
        """
        Reset the game to the starting position.
        """
        self._board.reset()
        self._moves_uci.clear()
        self._moves_san.clear()
        self._engine.set_position([])

    def set_move_history(self, moves_uci) -> bool:
        """
        Sets the move history
        :param moves_uci: The move history in UCI notation (e.g. 'e2e4').
        :return: True if the move history was set successfully, False otherwise.
        """
        # Resetting stored data
        self.reset_standard()
        # Setting starting position
        self._board = chess.Board(fen=self._starting_position_fen)
        self._engine.set_fen_position(self._starting_position_fen)

        # Applying the moves
        for move_uci in moves_uci:

            try:

                move = self._board.parse_uci(move_uci)
                move_san = self._board.san_and_push(move)
                self._moves_uci.append(move_uci)
                self._moves_san.append(move_san)
                self._engine.make_moves_from_current_position([move_uci])
            except ValueError:
                return False

        return True

    def print_current_board(self):
        """
        Prints a visual representation of the current board.
        """
        print(self._engine.get_board_visual())

    def is_game_over(self) -> bool:
        """
        game over does not differentiate between draw,checkmate,winner or aborted games
        :return: True if game is over, False otherwise.
        """
        return self._board.is_game_over()

    def is_checkmate(self) -> bool:
        """
        :return: True if game is checkmate
        """
        return self._board.is_checkmate()

    def is_game_draw(self) -> bool:
        """
        :return: True if game is draw
        """
        return self._board.is_game_over() and not self._board.is_checkmate()

    def get_stockfish_elo(self):
        """
        :return: The set elo strength
        """
        return self._elo_rating

    def set_stockfish_elo(self, elo):
        """
        This function sets the elo setting of stockfish
        :param elo:
        """
        self._elo_rating = elo
        self._engine.set_elo_rating(elo) # TODO, check if this can be changed during a game

    def get_move_history_san(self) -> List[str]:
        """
        :return: move history in san notation
        """
        return self._moves_san
