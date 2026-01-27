"""
The whole module was created by Maxim Scholtz

The module only consists of the GameManager class and the Move and PerformedMove classes which represent chess moves
    in two different format used by the frontend
"""
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass
import copy

import chess_engine
from chess_engine import MoveResultType


@dataclass
class Move:
    """
    This class represents a UCI move
    """
    from_square: str
    to_square: str
    promotion: Optional[str]

    def __str__(self):
        s = f"{self.from_square}{self.to_square}"
        if self.promotion:
            s += f" {self.promotion}"
        return s


@dataclass
class PerformedMove(Move):
    """
    A PerformedMove is a Move with added SAN notation at the end
    """
    san: str

    def __str__(self):
        return f"{super().__str__()} ({self.san})"


class _TurnState(Enum):
    HUMAN_MOVE_APPLIED = "human_move_applied"
    ROBOT_MOVE_APPLIED = "robot_move_applied"
    NOT_STARTED = "not_started"
    NOT_SET_UP = "not_set_up"
    HUMAN_WON = "human_won"
    ROBOT_WON = "robot_won"
    DRAW = "draw"


class GameManager:
    """
    The GameManager is the "Chess Brain" of the program
    It handles all the main game logic, keeps track of the game state, it handles format conversions
    """

    def __init__(self):
        self._chess_engine = chess_engine.ChessEngine()

        self._raw_board_history = []  # Format: 2D-Array consisting of only 'e', 'w', 'b'
        self._board_history = []  # Format: Fen Notation

        self._move_uci_history = []
        self._move_san_history = []

        # Both move histories below are in the robot playable format
        # Only the moves from the robot
        self._robot_moves_history = []
        # This move history contains also the player moves
        self._full_move_history_for_robot_replaying = []

        # Both indexes equal to len(move_uci_history) at the moment the respective getter function
        # meaning get_next_move_{ui}/{robot} was called
        self._last_move_index_played_ui = 0
        self._last_move_index_played_robot = 0

        self._num_robot_captures = 0

        self._board_starting_position_dict = None

        self._player_color = "w"
        self._turn_state = _TurnState.NOT_SET_UP

        self._default_starting_position_dict = {
                # White pieces
                "a1": "wR", "b1": "wN", "c1": "wB", "d1": "wQ", "e1": "wK", "f1": "wB", "g1": "wN", "h1": "wR",
                "a2": "wP", "b2": "wP", "c2": "wP", "d2": "wP", "e2": "wP", "f2": "wP", "g2": "wP", "h2": "wP",
                # Black pieces
                "a7": "bP", "b7": "bP", "c7": "bP", "d7": "bP", "e7": "bP", "f7": "bP", "g7": "bP", "h7": "bP",
                "a8": "bR", "b8": "bN", "c8": "bB", "d8": "bQ", "e8": "bK", "f8": "bB", "g8": "bN", "h8": "bR",
            }

        # Set to True if you want to debug different starting positions
        debug_starting_position = False
        if debug_starting_position:
            self._default_starting_position_dict = self.get_preset_starting_positions()['Draw']


    def set_up_game(self, board: Optional[dict[str, str]] = None):
        """
        This function starts the game meaning a move can be played after
        :param board: an optional dict (format: 'a2':'wP') describing the initial board
                        if board is None the default board will be used
        """


        # Storing the initial board
        self._board_starting_position_dict = board if board else self._default_starting_position_dict

        # Converting the starting board and forwarding it to the engine
        board_fen = self._convert_dict_to_fen(self._board_starting_position_dict)

        # Because a new board was set up we override the board history
        self._board_history = [board_fen]
        self._chess_engine.start_game(board_fen)

        self._turn_state = _TurnState.NOT_STARTED

        print(f"GameManager::set_up_game() - set up game completed - starting position: "
                f"{"default" if not board else "custom"}")


    def reset_game(self):
        """
        This function resets the game state only keeping player color
        """
        self._chess_engine.reset_standard()

        self._raw_board_history = []
        self._board_history = []

        self._move_uci_history = []
        self._move_san_history = []

        self._robot_moves_history = []
        self._full_move_history_for_robot_replaying = []

        self._last_move_index_played_robot = 0
        self._last_move_index_played_ui = 0

        self._turn_state = _TurnState.NOT_STARTED
        self._board_starting_position_dict = None

        self._num_robot_captures = 0

        print("GameManager::reset_game() - reset completed")


    def get_next_move_robot(self) -> List[str]:
        """
        This function checks if there are new moves to be played by the robot
        For one chess move a robot sometimes has to do multiple moves like for castling or capturing

        :return:
            Array of moves to be played by the robot in the correct order
                [] -> in the case of an error
                [] -> if no new moves are available
            Format of each move: <from_square><to_square><color>
                from_square: the square the piece originates from -> a1...h8
                to_square:
                    for normal moves: the square the piece is moved to -> a1...h8
                    for captures: x<index> where index: is based on the capture counter from 1 to 15
                color: {b/w} the color of the player/robot depending on whose move this is


        """

        if not self._turn_state == _TurnState.ROBOT_MOVE_APPLIED:
            print("GameManager::get_robot_moves(): ERROR: It is not the robot's turn")
            return []

        moves_to_play = []

        player_is_white = self._player_color == 'w'

        # Convert last move index to robot move history index
        last_robot_move = int(self._last_move_index_played_robot / 2)

        # If the player is black we need to increment the counter after the first round
        if not player_is_white:
            last_robot_move = last_robot_move if len(self._robot_moves_history) <= 1 else last_robot_move + 1

        # Check if new moves are stored which were not already played
        if self._last_move_index_played_robot < self._last_move_index_played_ui:

            moves_to_play = self._robot_moves_history[last_robot_move]

            # Update robot move index
            self._last_move_index_played_robot = len(self._move_uci_history)

        print(f"GameManager::get_robot_moves(): new moves : {moves_to_play}")
        return moves_to_play


    def get_next_move_ui(self) -> PerformedMove:
        """
        This function returns the next move to be played by the robot in the frontend
        :return: PerformedMove
        """

        # Check if the move to be played is applied and stored
        if not self._turn_state == _TurnState.ROBOT_MOVE_APPLIED:
            print("GameManager::get_next_move_ui(): ERROR - It is not the robot's turn")
            return None

        # Now we convert the move to be played from uci format to PerformedMove
        move_uci = self._move_uci_history[-1]
        move_san = self._move_san_history[-1]

        # Extract the parts from the uci move
        from_square = move_uci[:2]
        to_square = move_uci[2:4]
        promotion = move_uci[4:] if move_uci[4:] else ''

        performed_move = PerformedMove(
            from_square=from_square,
            to_square=to_square,
            promotion=promotion,
            san=move_san,
        )

        # Set counter of last played move in the frontend
        self._last_move_index_played_ui = len(self._move_uci_history)

        return performed_move


    def calculate_raw_next_move(self):
        """
        This function gets the next move to be played by the robot in UCI notation from the
            ChessEngine and stores it

        The move can then be extracted through the get_next_move_ui() for the frontend or
            get_next_move_robot() for the
            controller
        """

        # Robot move can only be applied after human move is applied
        if not self._turn_state == _TurnState.HUMAN_MOVE_APPLIED:
            print("GameManager::_calculate_raw_next_move(): can not calculate next robot move "
                  "because of wrong turn state")
            return


        # Get next move to play by robot
        result_type, next_move = self._chess_engine.get_next_move()

        match result_type:
            case MoveResultType.ERROR:
                print(f"GameManager::update_raw_board - received this error {next_move}")
                return
            case MoveResultType.MOVE:
                print(f"GameManager::update_raw_board - next robot move is going to be {next_move}")
            case MoveResultType.GAME_END:
                print(f"GameManager::update_raw_board - robot won with this move: {next_move}")
            case _:
                print("GameManager::update_raw_board - received unknown result type")
                return

        # Store the robot move and the board after the robots move
        self._move_uci_history.append(next_move)
        self._move_san_history.append(self._chess_engine.get_most_recent_move_san())

        self._board_history.append(self._chess_engine.get_current_board_fen())
        self._turn_state = _TurnState.ROBOT_MOVE_APPLIED

        robot_moves = self._convert_normal_to_robot_moves(robot_playing=True)
        self._robot_moves_history.append(robot_moves)
        self._full_move_history_for_robot_replaying.append(robot_moves)

        print(f"GameManager::calculate_raw_next_move(): calculated next robot moves: {robot_moves}")

    def _convert_normal_to_robot_moves(self, robot_playing: bool) -> List[str]:
        """
        This function converts moves in UCI format to robot moves
        :param robot_playing: if the player or robot is playing this move
        :return: List of robot moves
        """

        move_uci = self._move_uci_history[-1]
        move_san = self._move_san_history[-1]

        current_player_color = 'b' if self._player_color == 'w' else 'w'
        current_player_color = current_player_color if robot_playing else self._player_color

        to_square = move_uci[2:4]

        move_type = self._chess_engine.get_most_recent_move_type()

        # Convert the move depending on the type
        match move_type:
            case "castling":
                if move_san == "O-O":
                    if current_player_color == "w":
                        first_move = "e1g1"  # King: e1 -> g1
                        second_move = "h1f1"  # Rook: h1 -> f1
                    else:  # black
                        first_move = "e8g8"  # King: e8 -> g8
                        second_move = "h8f8"  # Rook: h8 -> f8
                    return [first_move+f" {current_player_color}", second_move+f" {current_player_color}"]

                if move_san == "O-O-O":
                    if current_player_color == "w":
                        first_move = "e1c1"  # King: e1 -> c1
                        second_move = "a1d1"  # Rook: a1 -> d1
                    else:  # black
                        first_move = "e8c8"  # King: e8 -> c8
                        second_move = "a8d8"  # Rook: a8 -> d8
                    return [first_move+f" {current_player_color}", second_move+f" {current_player_color}"]

                return []

            case "en_passant":
                # Increase the capture counter
                self._num_robot_captures = self._num_robot_captures + 1

                # Check if more than 15 capture which is impossible happened
                if self._num_robot_captures == 16:
                    print("GameManager::convert_normal_to_robot_moves - ERROR: more than 15 pieces were captured")

                pawn_file = move_san[-2] # The captured pawn is on the same file as the other pawn after capture

                if self._player_color == 'w':
                    pawn_rank = 4
                else:
                    pawn_rank = 5

                first_move = f"{pawn_file}{pawn_rank}x{self._num_robot_captures}"

                return [first_move+f" {current_player_color}", move_uci+f" {current_player_color}"]

            case "promotion":
                # TODO, implement promotions for the robot moves
                move_no_promotion = move_uci[:-1]# For now, we delete the promotion character at the end
                return [move_no_promotion+f" {current_player_color}"]

            case "capture/promotion":
                # Increase the capture counter
                self._num_robot_captures = self._num_robot_captures + 1

                # Check if more than 15 capture which is impossible happened
                if self._num_robot_captures == 16:
                    print("GameManager::convert_normal_to_robot_moves - ERROR: more than 15 pieces were captured")

                first_move = to_square + "x" + str(self._num_robot_captures)
                second_move = move_uci[:-1] # For now, we delete the promotion character at the end

                # TODO, implement promotions for the robot moves

                return [first_move+f" {current_player_color}", second_move+f" {current_player_color}"]

            case "capture":
                # Increase the capture counter
                self._num_robot_captures = self._num_robot_captures + 1

                # Check if more than 15 capture which is impossible happened
                if self._num_robot_captures == 16:
                    print("GameManager::convert_normal_to_robot_moves - ERROR: more than 15 pieces were captured")

                first_move = to_square + "x" + str(self._num_robot_captures)
                second_move = move_uci
                return [first_move+f" {current_player_color}", second_move+f" {current_player_color}"]

            case "normal":
                return [move_uci+f" {current_player_color}"]

            case _:
                return []

    def apply_player_move_ui(self, move: Optional[Move]) -> Optional[PerformedMove]:
        """
        This function is the equivalent to the normal update_raw_board function but for playing with the frontend
        The function gets an optional move in the Move format, this move is only allowed to be None if no move has been 
            played and the player has the black pieces
            
        The function then creates a raw board from the most recent raw board on which the move gets applied

        With the created raw board the controller update_raw_board() function gets called
        """

        # For debug only
        #print(f"GameManager::apply_player_move_ui - move to be applied: {move}")

        # Check if game is set up
        if self._turn_state == _TurnState.NOT_SET_UP:
            print("GameManager::apply_player_move_ui() - ERROR: Game has to be set up before playing ")
            return None

        # Check if this is the first move played as white with the default starting position
        if self._turn_state == _TurnState.NOT_STARTED and move and not self._board_starting_position_dict:
            # In this case we have to set up the necessary variables to continue with the normal control flow
            self._board_starting_position_dict = self._default_starting_position_dict

        # First we check if move is None and another move has already been stored
        if not move and self._move_uci_history:
            print("GameManager::apply_player_move_ui() - ERROR: No move was played but the game started already")
            return None

        # If no move was given it has to be the first round and the player is black
        if not move:
            # Because no move is played we convert the starting position and call the update_raw_board()
            starting_position_raw = self._convert_dict_to_raw_board(self._board_starting_position_dict)

            if not self.update_raw_board(starting_position_raw):
                return None

            # Because the first move is to be played by the robot we return None
            return None

        # Convert move to UCI move
        orig_piece = self._chess_engine.get_piece_at(move.from_square)
        if not orig_piece:
            print("GameManager::apply_player_move_ui() - ERROR: No piece was found on the square a piece was moved "
                  "from")
            return None
        promotion = move.promotion
        if promotion == orig_piece[1].lower():
            promotion = None
        uci_move = move.from_square + move.to_square + (promotion if promotion else '')

        # Apply move on the last raw board
        # If it is the first move no last raw board is stored therefore we take the default position
        if not self._raw_board_history:
            starting_board_raw = self._convert_dict_to_raw_board(self._board_starting_position_dict)
            new_raw_board = self._apply_uci_move_on_raw_board(starting_board_raw, uci_move)
        else:
            # First we apply the robot move played before on the raw board
            # Then we apply the player move on the same raw board to get the correct board to update
            new_raw_board = self._apply_uci_move_on_raw_board(self._raw_board_history[-1], self._move_uci_history[-1])
            new_raw_board = self._apply_uci_move_on_raw_board(new_raw_board, uci_move)

        # Call update_raw_board()
        if not self.update_raw_board(new_raw_board, promotion):
            return None


        # Get SAN notation of move and with it create the PerformedMove to return
        san = self._chess_engine.get_most_recent_move_san()

        performed_move = PerformedMove(
            from_square=move.from_square,
            to_square=move.to_square,
            promotion=promotion,
            san=san,
        )

        print(f"GameManager::apply_player_move_ui - Performed move: {performed_move}")
        return performed_move

    def update_raw_board(self, board, promotion: Optional[str] = None) -> bool:
        """
        This function is to be called when the player plays the controller/robot
        When the human player played the real-world move this function has to be called with the new raw board

        This function has differentiates two cases:
        1) The first time this function is called (moves.history is empty)
        2) The second or more time this function is called (moves.history is not empty)

        only in case 1) -> The function deduces which color the player is by checking if a move has been played

        always -> The function deduces the player move and checks if the move is legal
            it then applies and stores the move and sets the turn_state to HUMAN_MOVE_APPLIED to signal the robot
            move can be calculated

        :param board: encoding  of the raw board state after CV piece detection
        format:
         Chess board representation using a 2D array of characters

         Encoding scheme:
         - 'e' = empty square
         - 'w' = square with a white piece (any type)
         - 'b' = square with a black piece (any type)

         Orientation and indexing:
         - The board is a list of 8 rows (outer list), each with 8 columns (inner list).
         - The first row (index 0) represents the *top* of the board (rank 8).
         - The last row (index 7) represents the *bottom* (rank 1).
         - Each row is ordered from left to right (files a to h).
         - So board[0][0] = a8, board[7][7] = h1, as seen from white's perspective.
         - Therefore the array is the perspective of a chess board top down with white always at the bottom

         example_chess_board = [
            ['b', 'b', 'b', 'b', 'b', 'b', 'b', 'b'],  # Rank 8 (a8-h8)
            ['b', 'b', 'b', 'b', 'b', 'b', 'b', 'b'],  # Rank 7 (a7-h7)
            ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'],  # Rank 6
            ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'],  # Rank 5
            ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'],  # Rank 4
            ['e', 'e', 'e', 'e', 'e', 'e', 'e', 'e'],  # Rank 3
            ['w', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],  # Rank 2 (a2-h2)
            ['w', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],  # Rank 1 (a1-h1)
         ]
         :param promotion: {b,r,n,q} for the piece which got promoted to
                            currently promotions to other pieces than the queen are only supported
                            by input from the frontend
        """

        # Check if the game is already set up
        if self._board_starting_position_dict is None:
            print("GameManager::update_raw_board - ERROR: Chessboard has to be set up before the game can be started")
            return False

        # Store the (raw-) board and move history to later apply in case we encounter an error
        board_history_stored = self._board_history.copy()
        raw_board_history_stored = self._raw_board_history.copy()
        moves_history_stored = self._move_uci_history.copy()

        # Check if this is the first time the raw board is updated
        if not self._raw_board_history:

            if self._turn_state != _TurnState.NOT_STARTED:
                print("GameManager::update_raw_board() - moves_history is empty but game has started ")
                return False

            # Check if the starting board is legal
            if not self.is_starting_board_legal():
                print("GameManager::update_raw_board() - illegal starting position")
                return False

            # Extracting the initial board and checking if a move has been played already
            (initial_board,
             move_happened,
             initial_raw_board) = self._initial_board_mapping(board,self._board_starting_position_dict)

            # Store the initial boards
            self._raw_board_history.append(initial_raw_board)
            self._board_history.append(initial_board)

            # Check if move already happened
            if move_happened:
                # A move already happened
                # -> Player is white, and we check the move for legality before extracting the robot move
                self._player_color = "w"

                # Store the current raw board
                self._raw_board_history.append(board)

                # Deduce the move which already happened
                move_played = self._deduce_move(promotion)

                if move_played is None:
                    # No move could be deduced so we delete the newly stored boards
                    self._raw_board_history = raw_board_history_stored
                    self._board_history = board_history_stored
                    self._move_uci_history = moves_history_stored

                    print("GameManager::update_raw_board - could not determine move")
                    return False

                # Apply the player move and check for legality
                if not self._chess_engine.apply_player_move(move_played):
                    # The move was illegal so we delete the newly stored boards
                    self._raw_board_history = raw_board_history_stored
                    self._board_history = board_history_stored
                    self._move_uci_history = moves_history_stored

                    print("GameManager::update_raw_board - player move is illegal")
                    return False

                self._move_uci_history.append(move_played)  # Add player move
                self._move_san_history.append(self._chess_engine.get_most_recent_move_san())

                self._full_move_history_for_robot_replaying.append(
                    self._convert_normal_to_robot_moves(robot_playing=False))

                # Add current board after player move
                self._board_history.append(self._chess_engine.get_current_board_fen())
                self._turn_state = _TurnState.HUMAN_MOVE_APPLIED


            else:
                # No move happened -> robot is white and has to play the first move
                self._player_color = "b"
                self._turn_state = _TurnState.HUMAN_MOVE_APPLIED

            return True

        # This is not the first round of play
        # New raw board received
        # Therefore the last robot move was played
        # Also the player did a new move

        # Check if it is still the robots turn to play else no raw board should be updated
        if self._turn_state == _TurnState.HUMAN_MOVE_APPLIED:
            print("GameManager::update_raw_board - WARNING: a new raw board is received in the humans turn")
            return False

        # Store the new raw board
        self._raw_board_history.append(board)

        # Deduce the player move
        move_played = self._deduce_move(promotion)

        if move_played is None:
            # No move could be deduced so we delete the stored raw board
            self._raw_board_history = raw_board_history_stored
            self._board_history = board_history_stored
            self._move_uci_history = moves_history_stored

            print("GameManager::update_raw_board - could not determine move")
            return False

        # Apply the player move and check for legality
        if not self._chess_engine.apply_player_move(move_played):
            # The move was illegal so we delete the stored raw board
            self._raw_board_history = raw_board_history_stored
            self._board_history = board_history_stored
            self._move_uci_history = moves_history_stored

            print("GameManager::update_raw_board - player move is illegal")
            return False

        self._move_uci_history.append(move_played)  # Add player move
        self._move_san_history.append(self._chess_engine.get_most_recent_move_san())

        self._full_move_history_for_robot_replaying.append(
            self._convert_normal_to_robot_moves(robot_playing=False))

        # Add current board after player move
        self._board_history.append(self._chess_engine.get_current_board_fen())
        self._turn_state = _TurnState.HUMAN_MOVE_APPLIED

        return True

    def print_current_board(self):
        """
        This function prints the current board in a graphical way
        """
        self._chess_engine.print_current_board()

    def get_move_history_ui(self) -> List[PerformedMove]:
        """
        This function converts the move history in UCI and SAN notation to PerformedMoves format and returns the list
        """

        # First we get the move history in SAN notation
        move_history_san = self._chess_engine.get_moves_history_san()

        # We now get the move history in UCI notation
        move_history_uci = self._chess_engine.get_moves_history_uci()

        # Then we convert the SAN and UCI notation to PerformedMove format
        performed_moves_history = []

        for uci, san in zip(move_history_uci, move_history_san):
            performed_moves_history.append(PerformedMove(
                from_square=uci[:2],
                to_square=uci[2:4],
                promotion=uci[4:] if uci[4:] else None,
                san=san,
            ))

        return performed_moves_history

    #''' Private helper functions below'''

    def _deduce_move(self, promotion: Optional[str] = None) -> str | None:
        """
        Deduces the last player move in UCI notation

        We handle two cases:
        1) No move stored in moves_history: only the player move has to be deduced
        2) At least one move is stored in the moves_history: we first apply the robot move (moves_history[-1])
            onto the raw board then we deduce the last player move

        We than map the last board in FEN notation (board_history[-1]) onto the previous raw board
            (robot move applied onto raw_board_history[-1])
        IMPORTANT: the initial board mapping has always happened in the update_raw_board function,
            therefore board_history is never empty

        We then deduce the player move by comparing the board (FEN Notation) after the robot move to the
            current raw board

        IMPORTANT: Currently the player can only promote to Queens if playing with the robot
                    If a promotion was inputted by the frontend this is fully supported

        :param promotion: The promotion to apply from the frontend

        Returns:
          A UCI string like "e2e4", "e7e8q", "e1g1", or None if it cannot find a single player move.
        """

        # Check if raw board history is correct
        if len(self._raw_board_history) < 2:
            return None

        prev_raw_board = self._raw_board_history[-2]
        curr_raw_board = self._raw_board_history[-1]

        # Check if this is NOT the first time a move is deduced
        # At the first time there is at maximum one move played and no move stored in the history
        # After the first round, first the robot move has to be applied to deduce the player move
        if self._move_uci_history:
            last_move = self._move_uci_history[-1]
            prev_raw_board = self._apply_uci_move_on_raw_board(prev_raw_board, last_move)
            # Store the raw board after applying the robot move onto it
            self._raw_board_history.insert(-1,prev_raw_board)

        # Now map the current board in FEN notation onto the prev_raw_board to deduce the player move
        prev_board = self._map_fen_on_raw_board(self._board_history[-1], prev_raw_board)

        # Now we extract the player move
        # First we start by collecting all the changes from prev_board to curr_raw_board
        # therefore we build list of (row, col, before_piece, after_piece)
        diffs = []
        for row in range(8):
            for col in range(8):
                before = prev_board[row][col]  # 'P','r','K', or 'e'
                after = curr_raw_board[row][col]  # 'w','b', or 'e'
                # map before to its color
                before_color = 'e' if before == 'e' else ('w' if before.isupper() else 'b')
                if before_color != after:
                    diffs.append((row, col, before, after))
        def to_sq( row: int, col: int) -> str:
            """
            Helper function to map col and row to square names
            """
            files = 'abcdefgh'
            ranks = '87654321'
            return files[col] + ranks[row]

        # We now extract the player move in UCI notation by going through the kinds of moves

        # 1) CASTLING (4 diffs)
        if len(diffs) == 4:
            set_diffs = set(diffs)
            white_ks = {(7, 4, 'K', 'e'), (7, 6, 'e', 'w'), (7, 7, 'R', 'e'), (7, 5, 'e', 'w')}
            white_qs = {(7, 4, 'K', 'e'), (7, 2, 'e', 'w'), (7, 0, 'R', 'e'), (7, 3, 'e', 'w')}
            black_ks = {(0, 4, 'k', 'e'), (0, 6, 'e', 'b'), (0, 7, 'r', 'e'), (0, 5, 'e', 'b')}
            black_qs = {(0, 4, 'k', 'e'), (0, 2, 'e', 'b'), (0, 0, 'r', 'e'), (0, 3, 'e', 'b')}
            if white_ks <= set_diffs:  # '<=' subset operator
                return 'e1g1'
            if white_qs <= set_diffs:
                return 'e1c1'
            if black_ks <= set_diffs:
                return 'e8g8'
            if black_qs <= set_diffs:
                return 'e8c8'

            return None

        # 2) EN PASSANT (3 diffs)
        if len(diffs) == 3:
            robot_color = 'w' if self._player_color == 'b' else 'b'
            player_color = self._player_color

            # Find the 3 diffs: origin (pawn left), dest (pawn landed), capture (robot pawn removed)
            # Find the origin square: a pawn left here
            origin = None
            for row, col, before, after in diffs:
                # 'before' was a pawn, and now it’s empty
                # if player: w -> 'before': 'P'; player: b -> 'before': 'p'
                if before == ('p' if player_color == 'b' else 'P') and after == 'e':
                    origin = (row, col)
                    break

            # Find the destination square: a pawn arrived here
            dest = None
            for row, col, before, after in diffs:
                # Square was empty, and now contains the player’s pawn
                if before == 'e' and after.lower() == player_color:
                    dest = (row, col)
                    break

            # Find the capture square: where the robot’s pawn disappeared
            capture = None
            for row, col, before, after in diffs:
                # “before” was a pawn of the robot’s color, and now it’s empty
                if (robot_color == ('w' if before.isupper() else 'b')
                        and before.lower() == 'p'
                        and after == 'e'):
                    capture = (row, col)
                    break

            if origin and dest and capture:
                dr = -1 if player_color == 'w' else 1
                # Must be a diagonal pawn step
                if dest[0] == origin[0] + dr and abs(dest[1] - origin[1]) == 1:
                    # Capture square is origin.row, dest.col
                    if capture == (origin[0], dest[1]):
                        return f"{to_sq(*origin)}{to_sq(*dest)}"

            return None

        # 3) PROMOTION to Queen (2 diffs: pawn leaves; -queen- appears)
        if len(diffs) == 2:
            origin = dest = None
            for row, col, before, after in diffs:
                # Departure: pawn vacates
                if before.lower() == 'p' and after == 'e':
                    origin = (row, col)
                # Arrival: a piece appears (should be your pawn color)
                elif ((before == 'e' or (before.islower() and self._player_color == 'w')
                                    or (before.isupper() and self._player_color == 'b'))
                                    and after == self._player_color):
                    dest = (row, col)
            if origin and dest:
                # Check it's a back‐rank pawn move
                _, origin_col = origin
                dest_row, dest_col = dest
                if (((self._player_color == 'w' and dest_row == 0) or
                    (self._player_color == 'b' and dest_row == 7)) and
                    abs(dest_col - origin_col) <= 1):

                    src, dst = to_sq(*origin), to_sq(*dest)

                    # Check if the promotion is known from the frontend

                    promotion_piece = promotion if promotion else 'q'
                    return f"{src}{dst}{promotion_piece}"

        # 4) CAPTURE (2 diffs: origin vacated; destination replaced by opposite color)
        if len(diffs) == 2:
            origin = dest = None
            for row, col, before, after in diffs:
                # Origin: any piece leaves
                if before != 'e' and after == 'e':
                    origin = (row, col)
                # Dest: occupied by opponent
                if self._player_color == 'w' and before.islower() and before != 'e' and after != 'e':
                    dest = (row, col)
                if self._player_color == 'b' and before.isupper() and before != 'e' and after != 'e':
                    dest = (row, col)
            if origin and dest:
                # Ensure it’s a capture (colors differ)
                bef = prev_board[dest[0]][dest[1]]
                # before_color vs after_color
                bef_col = 'w' if bef.isupper() else 'b'
                aft_col = curr_raw_board[dest[0]][dest[1]]
                if bef_col != aft_col:
                    src, dst = to_sq(*origin), to_sq(*dest)
                    return f"{src}{dst}"

        # 5) NORMAL MOVE (2 diffs: origin vacated; destination occupied by same color)
        if len(diffs) == 2:
            origin = dest = None
            for row, col, before, after in diffs:
                if before != 'e' and after == 'e':
                    origin = (row, col)
                elif before == 'e' and after != 'e':
                    dest = (row, col)
            if origin and dest:
                # Ensure it’s not a capture
                bef = prev_board[origin[0]][origin[1]]
                aft_col = curr_raw_board[dest[0]][dest[1]]
                bef_col = 'w' if bef.isupper() else 'b'
                if bef_col == aft_col:
                    src, dst = to_sq(*origin), to_sq(*dest)
                    return f"{src}{dst}"

        return None

    def _apply_uci_move_on_raw_board(self, raw_board, move):
        """
        Applies a UCI move on a raw chess board representation.

        param:
            raw_board:   8x8 list of lists of characters: 'e' for empty, 'w' for white piece, 'b' for black piece.
            move:        UCI move string, e.g. "e2e4", "e7e8q", "e1g1", "e1h1".

        Returns:
            A new 8x8 list of lists reflecting the raw board after the move is applied.
        """

        # Deep-copy to avoid mutating original
        board = copy.deepcopy(raw_board)

        def uci_to_coords(sq):
            """Convert UCI square (e.g. 'e4') to (row, col) indices."""
            file, rank = sq[0], sq[1]
            col = ord(file) - ord('a')  # a->0, b->1, ..., h->7
            row = 8 - int(rank)  # '8'->0, '1'->7
            return row, col

        # Parse move
        from_sq = move[:2]
        to_sq = move[2:4]
        #promotion = move[4] if len(move) == 5 else None

        from_row, from_col = uci_to_coords(from_sq)
        to_row, to_col = uci_to_coords(to_sq)
        piece = board[from_row][from_col]

        # Castling
        # Case 1: King moves two squares in the direction of the rook (standard UCI castling)
        if from_row in (0, 7) and from_col == 4 and to_row == from_row and abs(to_col - from_col) == 2 :
            # Move king
            board[to_row][to_col] = piece
            board[from_row][from_col] = 'e'

            # Determine rook source & target
            rook_from_col = 7 if to_col > from_col else 0
            rook_to_col = from_col + (1 if to_col > from_col else -1)
            board[to_row][rook_to_col] = board[to_row][rook_from_col]
            board[to_row][rook_from_col] = 'e'
            return board

        # TODO, Implement the two cases below
        # Case 2: King moves onto the square the rook is standing on
        #if from_row in (0, 7) and from_col == 4 and to_row == from_row and to_col in (0, 7) and False:
        #    # Move king onto rook square
        #    board[to_row][to_col] = piece
        #    board[from_row][from_col] = 'e'
        #
        #    # Move rook next to original king position
        #    rook_from_col = to_col
        #    rook_to_col = 3 if to_col == 0 else 5
        #    board[to_row][rook_to_col] = board[to_row][rook_from_col]
        #    board[to_row][rook_from_col] = 'e'
        #    print("case2")
        #    return board

        # Case 3: Rook moves three squares in the direction of the king (queenside castling via rook move)
        #if from_row in (0, 7) and from_col == 0 and to_row == from_row and to_col == 3 and False:
        #    # Move rook
        #    board[to_row][to_col] = piece
        #    board[from_row][from_col] = 'e'
        #
        #    # Move king to appropriate square (from col 4 to col 2)
        #    board[to_row][2] = board[to_row][4]
        #    board[to_row][4] = 'e'
        #    print("case3")
        #    return board

        # En passant
        # Pawn moves diagonally to empty square
        if piece in ('w', 'b') and from_col != to_col and board[to_row][to_col] == 'e':
            # White en passant from ran k5 -> 6 (rows 3 -> 2)
            if piece == 'w' and from_row == 3 and to_row == 2:
                board[from_row][from_col] = 'e'
                board[to_row][to_col] = piece
                board[from_row][to_col] = 'e'
                return board
            # Black en passant from rank 4 -> 3 (rows 4 -> 5)
            if piece == 'b' and from_row == 4 and to_row == 5:
                board[from_row][from_col] = 'e'
                board[to_row][to_col] = piece
                board[from_row][to_col] = 'e'
                return board

        # Normal moves
        board[from_row][from_col] = 'e'
        board[to_row][to_col] = piece

        return board


    #'''Mapping functions below'''

    def _initial_board_mapping(self, raw_board, starting_position):
        """
        param:
          - raw_board: 8x8 list of 'e'/'w'/'b' (rank 8 at row 0, rank 1 at row 7; files a-h col 0-7)
          - starting_position: dict mapping squares ('a1'...'h8') to codes like 'wP','bK', etc.
        Returns:
          A tuple (fen_string, has_moved, starting_array) where:
            - fen_string is the FEN for the standard starting position
            - has_moved is True if raw_board differs from starting_position (i.e. White’s first move has occurred)
            - starting_array is the 8×8 list representation of the standard starting position
        """

        files = 'abcdefgh'
        ranks = '87654321'

        def square_to_coords(sq):
            return ranks.index(sq[1]), files.index(sq[0])  # 'a8'->(0,0)

        def coords_to_square(r, c):
            return files[c] + ranks[r]  # (0,0)->'a8'

        # Detect whether White has already moved
        has_moved = False
        for sq in starting_position:
            r, c = square_to_coords(sq)
            if raw_board[r][c] == 'e':
                has_moved = True
                break

        # Build FEN for the standard starting position
        ranks_fen = []
        for r in range(8):
            empties = 0
            fen_rank = ""
            for c in range(8):
                sq = coords_to_square(r, c)
                if sq in starting_position:
                    if empties:
                        fen_rank += str(empties)
                        empties = 0
                    code = starting_position[sq]
                    piece = code[1] if code[0] == 'w' else code[1].lower()
                    fen_rank += piece
                else:
                    empties += 1
            if empties:
                fen_rank += str(empties)
            ranks_fen.append(fen_rank)
        placement = "/".join(ranks_fen)
        fen = f"{placement} w KQkq - 0 1"

        # Build the starting position array notation
        starting_array = [['e' for _ in range(8)] for _ in range(8)]
        for sq, code in starting_position.items():
            r, c = square_to_coords(sq)
            starting_array[r][c] = 'w' if code[0] == 'w' else 'b'

        return fen, has_moved, starting_array

    #'''Mapping functions below'''

    def _map_fen_on_raw_board(self, fen_board: str, raw_board: list[list[str]]) -> list[list[str]]:
        """
        Given a FEN notation and a raw board
        generates a new board where each square is marked by the specific piece:
          - 'P', 'R', 'N', 'B', 'Q', 'K' for white pawn, rook, knight, bishop, queen, king
          - 'p', 'r', 'n', 'b', 'q', 'k' for black pieces
          - 'e' for an empty square

        IMPORTANT: The orientation of FEN notation and raw_board is the same

        param:
            fen_board: A full FEN string (only the piece placement part is used).
            raw_board: 8x8 list of lists providing the board template (only shape/orientation used).

        Returns:
            A new 8x8 list of lists with individual piece codes or 'e'.

        Raises:
            ValueError: If raw_board is not 8x8 or FEN placement does not cover exactly 64 squares.
        """
        # Validate raw_board dimensions
        if len(raw_board) != 8 or any(len(row) != 8 for row in raw_board):
            raise ValueError("GameManager::map_fen_on_raw_board - raw_board must be 8x8")

        # Extract the piece placement section of the FEN
        placement = fen_board.split()[0]
        ranks = placement.split('/')
        if len(ranks) != 8:
            raise ValueError(
                f"GameManager::map_fen_on_raw_board - Invalid FEN placement: expected 8 ranks, got {len(ranks)}")

        new_board = [['e' for _ in range(8)] for _ in range(8)]

        for rank_idx, rank in enumerate(ranks):
            file_idx = 0
            for square in rank:
                if square.isdigit():
                    # empty squares
                    empty_count = int(square)
                    file_idx += empty_count
                elif square.isalpha():
                    if file_idx >= 8:
                        raise ValueError(f"GameManager::map_fen_on_raw_board - FEN rank {rank_idx} overflows 8 files")
                    # Place the piece character as-is (uppercase for white, lowercase for black)
                    new_board[rank_idx][file_idx] = square
                    file_idx += 1
                else:
                    raise ValueError(f"GameManager::map_fen_on_raw_board - Unexpected character in FEN: {square}")
            if file_idx != 8:
                raise ValueError(
                    f"GameManager::map_fen_on_raw_board - FEN rank {rank_idx} does not fill 8 files, only {file_idx}")

        return new_board

    #'''Conversion functions below'''

    def _convert_dict_to_fen(self, position: dict[str, str]) -> str:
        """
        Convert a React-Chessboard style position dict into a full FEN string.

        This function only handles the case where `position` is a mapping from
        algebraic square names ('a1'...'h8') to two-character piece codes:
          - First char: 'w' (white) or 'b' (black)
          - Second char: one of 'P','N','B','R','Q','K'

        Empty squares are those not present in the dict.

        Returns a FEN with default metadata:
          - active color:            w
          - castling availability:   KQkq
          - en passant target:       -
          - halfmove clock:          0
          - fullmove number:         1
        """
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = range(8, 0, -1)  # 8,7,...,1
        fen_rows = []

        for rank in ranks:
            empty_count = 0
            row_str = ''
            for file in files:
                square = f"{file}{rank}"
                piece_code = position.get(square)
                if piece_code is None:
                    empty_count += 1
                else:
                    # flush pending empties
                    if empty_count:
                        row_str += str(empty_count)
                        empty_count = 0
                    color, p_type = piece_code
                    # uppercase for white, lowercase for black
                    fen_char = p_type.upper() if color == 'w' else p_type.lower()
                    row_str += fen_char
            # flush trailing empties at end of rank
            if empty_count:
                row_str += str(empty_count)
            fen_rows.append(row_str)

        placement = '/'.join(fen_rows)
        # append default FEN fields
        return f"{placement} w KQkq - 0 1"

    def _convert_fen_to_dict(self, fen: str) -> dict[str, str]:
        """
        Convert a full FEN string into a React-Chessboard style position dict.

        This function only handles the piece placement field (the first field) of the FEN;
        it ignores active color, castling, en passant, halfmove and fullmove metadata.

        Parameters:
            fen (str): A full FEN string, e.g.
                       "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        Returns:
            dict[str, str]:
                A mapping from algebraic square names ("a1" ... "h8") to two-character piece codes:
                - First char: 'w' (white) or 'b' (black)
                - Second char: one of 'P','N','B','R','Q','K'
                Empty squares are omitted from the dict.

        Example:
            # >>> convert_fen_to_ui_board("8/8/8/4p3/4P3/8/8/7R w KQkq - 0 1")
            {'e5': 'bP', 'e4': 'wP', 'h1': 'wR'}
        """
        # split off placement field
        placement = fen.split()[0]
        ranks = placement.split('/')
        if len(ranks) != 8:
            raise ValueError(f"Invalid FEN placement: expected 8 ranks but got {len(ranks)}")

        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        board_dict: dict[str, str] = {}

        for rank_idx, rank_str in enumerate(ranks):
            rank = 8 - rank_idx
            file_idx = 0

            for ch in rank_str:
                if ch.isdigit():
                    # skip that many empty squares
                    file_idx += int(ch)
                else:
                    if file_idx >= 8:
                        raise ValueError(f"Invalid FEN rank '{rank_str}' at rank {rank}")
                    file = files[file_idx]
                    square = f"{file}{rank}"
                    if ch.isupper():
                        code = 'w' + ch  # white piece
                    else:
                        code = 'b' + ch.upper()  # black piece
                    board_dict[square] = code
                    file_idx += 1

            if file_idx != 8:
                raise ValueError(f"Invalid FEN rank '{rank_str}': incomplete (only {file_idx} files)")

        return board_dict

    def _convert_dict_to_raw_board(self, board_dict: dict[str, str]) -> list[list[str]]:
        """
        Converts a board in dict format to a raw board format

        Parameter:
            board_dict: dict mapping squares like "a1"-"h8" to two-character
                       codes, e.g. "wP", "bK". Empty squares are omitted.

        Returns:
            raw board format (2D array a8 is 00 containing only w,b,e)
        """
        # initialize 8×8 board full of 'e'
        board = [['e'] * 8 for _ in range(8)]

        for square, code in board_dict.items():
            file_char = square[0].lower()
            rank_char = square[1]
            col = ord(file_char) - ord('a')  # convert file to index (column) a -> 0, b -> 1, ..., h -> 7
            row = 8 - int(rank_char)  # # convert rank to index (row) 8 -> 0, 7 -> 1, ..., 0 -> 7

            color = code[0].lower()  # 'w' or 'b'
            if color not in ('w', 'b'):
                print(f"GameManager::convert_dict_to_raw_board - Invalid color '{color}'")

            board[row][col] = color

        return board

    #'''Simple getter and setter functions below'''

    def get_initial_position_dict(self) -> dict:
        """
        :return: the initial starting position as dict ({a1:wR ...}) if set
                    if not set, the default starting position
        """
        # Check if the game was set up and is started
        if self._board_starting_position_dict is None:
            print("GameManager::get_initial_position_dict - WARNING: Initial position is None current turnstate: "
                  f"{self._turn_state} -> no initial board ",end="")
            print("is set up -> returned default board ")

            return self._default_starting_position_dict

        return self._board_starting_position_dict

    def get_current_position_dict(self) -> dict:
        """
        :return: the current position as dict ({a1:wR ...}) if set
                    if not set, the starting position
                    if starting position is also not set, the default starting position
        """
        # Check if the game was set up and is started
        if self._turn_state == _TurnState.NOT_SET_UP:
            print("GameManager::get_current_position_dict - WARNING: Game is not set up -> no initial board ",end="")
            print("is set up -> returned default board ")

            return self._default_starting_position_dict

        if not self._board_history:
            print(f"GameManager::get_current_position_dict - WARNING: board history is empty: {self._turn_state}"
                  " -> returning default board")

            # Return starting position if set
            if self._board_starting_position_dict:
                return self._board_starting_position_dict

            return self._default_starting_position_dict

        # Convert current position to dict
        current_board_dict = self._convert_fen_to_dict(self._board_history[-1])
        return current_board_dict

    def get_human_player_color(self) -> str:
        """
        :return: player_color: {w,b}
        """
        return self._player_color

    def set_human_player_color(self, player_color: str) -> bool:
        """
        :param player_color: {w,b}
        :return: True if no error occurred, False otherwise
        """
        if self._turn_state != _TurnState.NOT_STARTED :
            print(f"GameManager::set_human_player_color - {self._turn_state} but state should be 'NOT_STARTED'")
            return False

        if player_color not in ('w', 'b'):
            print(f"GameManager::set_human_player_color - Invalid color '{player_color}'")
            return False

        self._player_color = player_color

        return True

    def get_current_player_color(self) -> str:
        """
        :return: color of whose turn it currently is: {w,b}
        """
        if self._turn_state == _TurnState.ROBOT_MOVE_APPLIED:
            return self._player_color

        if self._turn_state == _TurnState.HUMAN_MOVE_APPLIED:
            return 'w' if self._player_color != 'w' else 'b'

        print(f"GameManager::get_current_player_color - Warning: {self._turn_state} -> "
              f"returning '{self._player_color}'")
        return self._player_color

    def get_stockfish_elo(self) -> int:
        """
        :return: the set elo of stockfish
        """
        return self._chess_engine.get_stockfish_elo()

    def set_stockfish_elo(self, elo: int) -> bool:
        """
        :param elo: int in range [1320,3190]
        :return: True if no error occurred, False otherwise
        """
        # Check if the elo is supported
        if elo < 1320 or elo > 3190:
            return False

        self._chess_engine.set_stockfish_elo(elo)
        return True

    def set_move_history(self, moves: List[Move], override_last_raw_board = False) -> bool:
        """
        This function sets (overrides the move history) this is to be used in the case a move got
        incorrectly detected by the board detection

        The function applies all moves from the new move history in the chess engine
        it also overrides the last board, and move history in san and uci notation

        IMPORTANT: Every move history which results in the same current board or even a different
        one if override_last_raw_board is True is legal

        IMPORTANT: currently the robot_moves_history and full_move_history_for_robot_replaying are
                    unchanged -> this could result in problems when replaying robot moves or
                    executing the most recent robot moves

        :param moves: The new correct move history
        :param override_last_raw_board: True: the current/last stored raw board gets overridden
                                            with the raw board resulting from the new move history
                                        False: the new raw board resulting from the new move history
                                            has to be equal to the current raw board of the old move
                                            history
        :return: True if setting the move history was a success, False otherwise
        """
        # Convert Move to uci format
        uci_moves = []
        for move in moves:
            uci_move = f"{move.from_square}{move.to_square}{move.promotion if move.promotion else ''}"
            uci_moves.append(uci_move)

        # Set move history in chess engine
        chess_engine_success = self._chess_engine.set_move_history(uci_moves)

        # Check for success
        if not chess_engine_success:

            # Because the new move history is invalid we input the old move history again
            self._chess_engine.set_move_history(self._move_uci_history)

            return False

        # Extracting the raw_board from the new move history
        new_board_fen = self._chess_engine.get_current_board_engine_fen()
        new_raw_board = self._convert_dict_to_raw_board(self._convert_fen_to_dict(new_board_fen))

        if not override_last_raw_board:
            # Last raw board should not be overridden
            # We check if the raw board resulting from the new move history is equal to the one before
            if not new_raw_board == self._raw_board_history[-1]:

                # Because the new move history is invalid we input the old move history again
                self._chess_engine.set_move_history(self._move_uci_history)

                return False
        else:
            # Overriding the last raw board
            self._raw_board_history.pop()
            self._raw_board_history.append(new_raw_board)

        # Overriding the move histories
        self._move_uci_history = uci_moves
        self._move_san_history = self._chess_engine.get_move_history_san()

        # Overriding the last board
        self._board_history.pop()
        self._board_history.append(new_board_fen)

        # For now, we don't change any robot move history

        return True

    #''' Function for replaying missed robot moves below'''

    def get_moves_to_replay_robot(self):
        """
        This function returns a list of moves to be replayed by the robot to be in the same state
        as the frontend

        If frontend and robot are in sync no moves are returned

        This function also returns the moves from the player to be replayed

        :return: The missed robot moves to be replayed
        """
        moves_to_replay = []

        # Check if the robot is actually behind
        if not self.is_robot_behind():
            return moves_to_replay

        # Extract missing robot moves
        moves_to_replay = self._full_move_history_for_robot_replaying[
                          self._last_move_index_played_robot:]

        # Update the index
        self._last_move_index_played_robot = self._last_move_index_played_ui

        return moves_to_replay

    def is_robot_behind(self):
        """
        This function checks if the robot has fewer moves executed than the frontend
        :return: True if the robot is behind
        """
        return self._last_move_index_played_robot < self._last_move_index_played_ui

    #''' Function to get the game state if ended'''

    def is_game_over(self) -> bool:
        """
        This function checks if the game is over, meaning a draw or checkmate happened
        :return: True if the game is over, False otherwise
        """
        return self._chess_engine.is_game_over()

    def is_checkmate(self) -> bool:
        """
        This function checks if the game is in checkmate but does not differentiate if the player or robot won
        :return: True if the game is in checkmate, False otherwise
        """
        return self._chess_engine.is_checkmate()

    def is_game_draw(self) -> bool:
        """
        :return: True if the game is draw, False otherwise
        """
        return self._chess_engine.is_game_draw()

    def is_player_winner(self) -> bool:
        """
        :return: True if the player won the game, False otherwise
        """
        return self._chess_engine.is_checkmate() and self.get_current_player_color() != self._player_color

    def is_starting_board_legal(self) -> bool:
        """
        This function checks if a starting chess board is legal
        A legal board has to have exactly one king per color
        :return: True if the board is legal, False otherwise
        """
        # If no starting board is set the default one will be set
        if not self._board_starting_position_dict:
            return True

        # We check  if the starting position has not exactly one king for black and white
        white_king_count = sum(1 for piece in self._board_starting_position_dict.values() if
                               len(piece) == 2 and piece[-1] == 'K' and piece[-2] == 'w')
        black_king_count = sum(1 for piece in self._board_starting_position_dict.values() if
                               len(piece) == 2 and piece[-1] == 'K' and piece[-2] == 'b')

        # If there is not exactly one king per color the game can't be played
        if not white_king_count == 1 and not black_king_count == 1:
            print(
                f"GameManager::update_raw_board - king count is not 1 for both colors - white: {white_king_count},"
                f" black: {black_king_count}")
            return False

        return True


    #''' Functions for debugging below'''

    def get_preset_starting_positions(self) -> dict:
        """
        This function stores preset starting positions
        :return: dict: {name of positions: position}
        """
        promotion_dict = {
                    # White pieces
                    "a1": "wR", "b1": "wN", "c1": "wB", "d1": "wQ", "e1": "wK", "f1": "wB", "g1": "wN","h1": "wR",
                    "a2": "wP", "b2": "wP", "c2": "wP", "d2": "wP", "e2": "wP", "f2": "wP", "g2": "wP","h2": "wP",
                    # Black pieces
                    "a7": "bP", "b7": "bP", "c7": "bP", "d7": "bP", "e7": "bP", "f7": "bP", "g7": "bP","h7": "wP",
                    "a8": "bR", "b8": "bN", "c8": "bB", "d8": "bQ", "e8": "bK", "f8": "bB", "g8": "bN","h8": "bR",
                    }

        win_dict = {
                # White pieces
                "a1": "wR",  "c1": "wB", "d1": "wQ", "e1": "wK", "f1": "wB", "g1": "wN", "h1": "wR","c4":"wN",
                "a2": "wP", "b2": "wP", "c2": "wP", "d2": "wP", "e2": "wP", "f2": "wP", "g2": "wP", "h2": "wP",
                "e4": "wN",
                # Black pieces
                "a7": "bP", "b7": "bP", "c7": "bP", "d7": "bP", "f7": "bP", "g7": "bN", "h7": "bP", "e7": "bN",
                "a8": "bR", "c8": "bB", "d8": "bQ", "e8": "bK", "f8": "bB", "h8": "bR",
            }

        loose_dict = {
                # White pieces
                "a1": "wR", "b1": "wN", "c1": "wB", "d1": "wQ", "e1": "wK", "f1": "wB", "g1": "wN", "h1": "wR",
                "a2": "wP", "b2": "wP", "c2": "wP", "d2": "wP", "e2": "wP",  "h2": "wP",
                # Black pieces
                "a7": "bP", "b7": "bP", "c7": "bP", "d7": "bP", "f7": "bP", "g7": "bP", "h7": "bP",
                "a8": "bR", "b8": "bN", "c8": "bB", "d8": "bQ", "e8": "bK", "f8": "bB", "g8": "bN", "h8": "bR",
            }

        draw_dict = {
                # White pieces
                 "d1": "wQ", "e1": "wK", "c1": "wB", "g1": "wN", "h1": "wR",

                # Black pieces

                "e8": "bK", "a7":"wR","h7":"bP","h5":"wP"
            }

        opponent_promotion_dict = {
                # White pieces
                "a1": "wR", "b1": "wN", "c1": "wB", "d1": "wQ", "e1": "wK", "f1": "wB", "g1": "wN", "h1": "wR",
                "a2": "wP", "b2": "wP", "c2": "wP", "d2": "wP", "e2": "wP", "f2": "wP", "g2": "bP", "h2": "wP",
                # Black pieces
                "a7": "bP", "b7": "bP", "c7": "bP", "d7": "bP", "e7": "bP", "f7": "bP", "g7": "bP", "h7": "bP",
                "a8": "bR", "b8": "bN", "c8": "bB", "d8": "bQ", "e8": "bK", "f8": "bB", "g8": "bN", "h8": "bR",
            }


        return {'White Promotion': promotion_dict,
                'White Win': win_dict,
                'White Lose': loose_dict,
                'Draw': draw_dict,
                'Black Promotion': opponent_promotion_dict,
                }

    def set_preset_starting_position(self, position):
        """
        This function sets the specified starting board from the presets stored in get_preset_starting_boards()
        :param position: Name of the position to be set
        """
        # Check if the position name exists
        starting_position = self.get_preset_starting_positions().get(position)

        # Set the position
        if starting_position:
            self._board_starting_position_dict = starting_position
