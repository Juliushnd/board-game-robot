# pylint: disable=protected-access
"""
The whole module was created by Maxim Scholtz

The module only tests the deduce_move function of the GameManager
"""

from pprint import pprint  # Used for full printing of the board
import pytest
from game_manager import GameManager


def create_empty_board():
    """
    :return: empty raw board
    """
    return [['e'] * 8 for _ in range(8)]


# Castling
board_bef_castling_qs_w = create_empty_board()
board_bef_castling_qs_w[7][0] = 'w'  # a1 (rook)
board_bef_castling_qs_w[7][4] = 'w'  # e1 (king)
board_aft_castling_qs_w = create_empty_board()
board_aft_castling_qs_w[7][2] = 'w'  # c1 (king)
board_aft_castling_qs_w[7][3] = 'w'  # d1 (rook)

board_bef_castling_ks_w = create_empty_board()
board_bef_castling_ks_w[7][4] = 'w'  # e1 (king)
board_bef_castling_ks_w[7][7] = 'w'  # h1 (rook)
board_aft_castling_ks_w = create_empty_board()
board_aft_castling_ks_w[7][6] = 'w'  # g1 (king)
board_aft_castling_ks_w[7][5] = 'w'  # f1 (rook)

board_bef_castling_qs_b = create_empty_board()
board_bef_castling_qs_b[0][0] = 'b'  # a8 (rook)
board_bef_castling_qs_b[0][4] = 'b'  # e8 (king)
board_aft_castling_qs_b = create_empty_board()
board_aft_castling_qs_b[0][2] = 'b'  # c8 (king)
board_aft_castling_qs_b[0][3] = 'b'  # d8 (rook)

board_bef_castling_ks_b = create_empty_board()
board_bef_castling_ks_b[0][4] = 'b'  # e8 (king)
board_bef_castling_ks_b[0][7] = 'b'  # h8 (rook)
board_aft_castling_ks_b = create_empty_board()
board_aft_castling_ks_b[0][6] = 'b'  # g8 (king)
board_aft_castling_ks_b[0][5] = 'b'  # f8 (rook)

# En passant
board_bef_enpassant_w = create_empty_board()
board_bef_enpassant_w[3][4] = 'w'  # e5
board_bef_enpassant_w[3][3] = 'b'  # d5
board_aft_enpassant_w = create_empty_board()
board_aft_enpassant_w[2][3] = 'w'  # d6

board_bef_enpassant_b = create_empty_board()
board_bef_enpassant_b[4][4] = 'b'  # e4
board_bef_enpassant_b[4][3] = 'w'  # d4
board_aft_enpassant_b = create_empty_board()
board_aft_enpassant_b[5][3] = 'b'  # d3

# Promotion
board_bef_promotion_w = create_empty_board()
board_bef_promotion_w[1][4] = 'w'  # e7
board_aft_promotion_w = create_empty_board()
board_aft_promotion_w[0][4] = 'w'  # e8

board_bef_promotion_b = create_empty_board()
board_bef_promotion_b[6][4] = 'b'  # e2
board_aft_promotion_b = create_empty_board()
board_aft_promotion_b[7][4] = 'b'  # e1

# Pawn Captures
board_bef_capture_w = create_empty_board()
board_bef_capture_w[4][4] = 'w'  # e4
board_bef_capture_w[3][3] = 'b'  # d5
board_aft_capture_w = create_empty_board()
board_aft_capture_w[3][3] = 'w'  # d5

board_bef_capture_b = create_empty_board()
board_bef_capture_b[3][4] = 'b'  # e5
board_bef_capture_b[4][3] = 'w'  # d4
board_aft_capture_b = create_empty_board()
board_aft_capture_b[4][3] = 'b'  # d4

# Captures: one for each piece type (knight, bishop, rook, queen, king)
# White knight capture: b1->c3
board_bef_capture_w_knight = create_empty_board()
board_bef_capture_w_knight[7][1] = 'w'  # b1
board_bef_capture_w_knight[5][2] = 'b'  # c3
board_aft_capture_w_knight = create_empty_board()
board_aft_capture_w_knight[5][2] = 'w'  # c3

# Black knight capture: b8->c6
board_bef_capture_b_knight = create_empty_board()
board_bef_capture_b_knight[0][1] = 'b'  # b8
board_bef_capture_b_knight[2][2] = 'w'  # c6
board_aft_capture_b_knight = create_empty_board()
board_aft_capture_b_knight[2][2] = 'b'  # c6

# White bishop capture: c1->f4
board_bef_capture_w_bishop = create_empty_board()
board_bef_capture_w_bishop[7][2] = 'w'  # c1
board_bef_capture_w_bishop[4][5] = 'b'  # f4
board_aft_capture_w_bishop = create_empty_board()
board_aft_capture_w_bishop[4][5] = 'w'  # f4

# Black bishop capture: c8->f5
board_bef_capture_b_bishop = create_empty_board()
board_bef_capture_b_bishop[0][2] = 'b'  # c8
board_bef_capture_b_bishop[3][5] = 'w'  # f5
board_aft_capture_b_bishop = create_empty_board()
board_aft_capture_b_bishop[3][5] = 'b'  # f5

# White rook capture: a1->a4
board_bef_capture_w_rook = create_empty_board()
board_bef_capture_w_rook[7][0] = 'w'  # a1
board_bef_capture_w_rook[4][0] = 'b'  # a4
board_aft_capture_w_rook = create_empty_board()
board_aft_capture_w_rook[4][0] = 'w'  # a4

# Black rook capture: a8->a5
board_bef_capture_b_rook = create_empty_board()
board_bef_capture_b_rook[0][0] = 'b'  # a8
board_bef_capture_b_rook[3][0] = 'w'  # a5
board_aft_capture_b_rook = create_empty_board()
board_aft_capture_b_rook[3][0] = 'b'  # a5

# White queen capture: d1->h5
board_bef_capture_w_queen = create_empty_board()
board_bef_capture_w_queen[7][3] = 'w'  # d1
board_bef_capture_w_queen[3][7] = 'b'  # h5
board_aft_capture_w_queen = create_empty_board()
board_aft_capture_w_queen[3][7] = 'w'  # h5

# Black queen capture: d8->h4
board_bef_capture_b_queen = create_empty_board()
board_bef_capture_b_queen[0][3] = 'b'  # d8
board_bef_capture_b_queen[4][7] = 'w'  # h4
board_aft_capture_b_queen = create_empty_board()
board_aft_capture_b_queen[4][7] = 'b'  # h4

# White king capture: e1->d2
board_bef_capture_w_king = create_empty_board()
board_bef_capture_w_king[7][4] = 'w'  # e1
board_bef_capture_w_king[6][3] = 'b'  # d2
board_aft_capture_w_king = create_empty_board()
board_aft_capture_w_king[6][3] = 'w'  # d2

# Black king capture: e8->d7
board_bef_capture_b_king = create_empty_board()
board_bef_capture_b_king[0][4] = 'b'  # e8
board_bef_capture_b_king[1][3] = 'w'  # d7
board_aft_capture_b_king = create_empty_board()
board_aft_capture_b_king[1][3] = 'b'  # d7

# Illegal / ambiguous moves (expanded)
# 1) No movement
board_bef_illegal1 = create_empty_board()
board_aft_illegal1 = create_empty_board()

# 2) Two pawns moved simultaneously
board_bef_illegal2 = create_empty_board()
board_bef_illegal2[6][0] = 'w'  # a2
board_bef_illegal2[6][1] = 'w'  # b2
board_aft_illegal2 = create_empty_board()
board_aft_illegal2[5][0] = 'w'  # a3
board_aft_illegal2[5][1] = 'w'  # b3

# 3) Random four-square diff (non-castling)
board_bef_illegal3 = create_empty_board()
board_bef_illegal3[7][0] = 'w'
board_bef_illegal3[7][1] = 'w'
board_aft_illegal3 = create_empty_board()
board_aft_illegal3[7][2] = 'w'
board_aft_illegal3[7][3] = 'w'

# 4) Five diffs (too many changes)
board_bef_illegal4 = create_empty_board()
board_bef_illegal4[7][2] = 'w'
board_bef_illegal4[7][5] = 'w'
board_aft_illegal4 = create_empty_board()
board_aft_illegal4[7][3] = 'w'
board_aft_illegal4[7][6] = 'w'
board_aft_illegal4[0][0] = 'b'

# 5) Three diffs but invalid pattern (no proper capture or en passant)
board_bef_illegal5 = create_empty_board()
board_bef_illegal5[4][4] = 'w'
board_bef_illegal5[3][3] = 'b'
board_bef_illegal5[2][2] = 'w'
board_aft_illegal5 = create_empty_board()
board_aft_illegal5[3][3] = 'w'
board_aft_illegal5[2][2] = 'e'
board_aft_illegal5[4][4] = 'e'

@pytest.mark.parametrize(
    "before, after, expected, player_color, fen",
    [
        # Castling
        (board_bef_castling_qs_w, board_aft_castling_qs_w, 'e1c1', 'w', '8/8/8/8/8/8/8/R3K3 w - - 0 1'),
        (board_bef_castling_ks_w, board_aft_castling_ks_w, 'e1g1', 'w', '8/8/8/8/8/8/8/4K2R w - - 0 1'),
        (board_bef_castling_qs_b, board_aft_castling_qs_b, 'e8c8', 'b', 'r3k3/8/8/8/8/8/8/8 b - - 0 1'),
        (board_bef_castling_ks_b, board_aft_castling_ks_b, 'e8g8', 'b', '4k2r/8/8/8/8/8/8/8 b - - 0 1'),
        # En passant
        (board_bef_enpassant_w, board_aft_enpassant_w, 'e5d6', 'w', '8/8/8/3pP3/8/8/8/8 w - - 0 1'),
        (board_bef_enpassant_b, board_aft_enpassant_b, 'e4d3', 'b', '8/8/8/8/3Pp3/8/8/8 b - - 0 1'),
        # Promotion
        (board_bef_promotion_w, board_aft_promotion_w, 'e7e8q', 'w', '8/4P3/8/8/8/8/8/8 w - - 0 1'),
        (board_bef_promotion_b, board_aft_promotion_b, 'e2e1q', 'b', '8/8/8/8/8/8/4p3/8 b - - 0 1'),
        # Captures (pawn)
        (board_bef_capture_w, board_aft_capture_w, 'e4d5', 'w', '8/8/8/3p4/4P3/8/8/8 w - - 0 1'),
        (board_bef_capture_b, board_aft_capture_b, 'e5d4', 'b', '8/8/8/4p3/3P4/8/8/8 b - - 0 1'),
        # Captures (knight)
        (board_bef_capture_w_knight, board_aft_capture_w_knight, 'b1c3', 'w', '8/8/8/8/8/2p5/8/1N6 w - - 0 1'),
        (board_bef_capture_b_knight, board_aft_capture_b_knight, 'b8c6', 'b', '1n6/8/2P5/8/8/8/8/8 b - - 0 1'),
        # Captures (bishop)
        (board_bef_capture_w_bishop, board_aft_capture_w_bishop, 'c1f4', 'w', '8/8/8/8/5p2/8/8/2B5 w - - 0 1'),
        (board_bef_capture_b_bishop, board_aft_capture_b_bishop, 'c8f5', 'b', '2b5/8/8/5P2/8/8/8/8 b - - 0 1'),
        # Captures (rook)
        (board_bef_capture_w_rook, board_aft_capture_w_rook, 'a1a4', 'w', '8/8/8/8/p7/8/8/R7 w - - 0 1'),
        (board_bef_capture_b_rook, board_aft_capture_b_rook, 'a8a5', 'b', 'r7/8/8/P7/8/8/8/8 b - - 0 1'),
        # Captures (queen)
        (board_bef_capture_w_queen, board_aft_capture_w_queen, 'd1h5', 'w', '8/8/8/7p/8/8/8/3Q4 w - - 0 1'),
        (board_bef_capture_b_queen, board_aft_capture_b_queen, 'd8h4', 'b', '3q4/8/8/8/7P/8/8/8 b - - 0 1'),
        # Captures (king)
        (board_bef_capture_w_king, board_aft_capture_w_king, 'e1d2', 'w', '8/8/8/8/8/8/3p4/4K3 w - - 0 1'),
        (board_bef_capture_b_king, board_aft_capture_b_king, 'e8d7', 'b', '4k3/3P4/8/8/8/8/8/8 b - - 0 1'),
        # Illegal
        (board_bef_illegal1, board_aft_illegal1, None, 'w', '8/8/8/8/8/8/8/8 w - - 0 1'),
        (board_bef_illegal2, board_aft_illegal2, None, 'w', '8/8/8/8/8/8/PP6/8 w - - 0 1'),
        (board_bef_illegal3, board_aft_illegal3, None, 'w', '8/8/8/8/8/8/8/PP6 w - - 0 1'),
        (board_bef_illegal4, board_aft_illegal4, None, 'w', '8/8/8/8/8/8/8/2P2P2 w - - 0 1'),
        (board_bef_illegal5, board_aft_illegal5, None, 'w', '8/8/2P5/3p4/4P3/8/8/8 w - - 0 1'),
    ]
)
def test_deduce_move_all_cases(before, after, expected, player_color,fen):
    """
    Tests the deduce_move function of the GameManager class
    :param before: raw board before
    :param after:  raw board after
    :param expected: expected result
    :param player_color:
    :param fen: fen notation of the raw board before
    """
    game = GameManager()
    game._player_color = player_color
    game._raw_board_history = [before, after]
    game._board_history = [fen]
    try:
        result = game._deduce_move()
        print(f"  result: {result}")
        assert result == expected
    except Exception as e:
        print("\n=== FULL BOARD DUMP ON FAILURE ===")
        print("Before:")
        pprint(before, width=200)
        print("After:")
        pprint(after, width=200)
        print(f"Expected: {expected}; Actual: {result}")
        print(f"exception: {e}")
        raise
