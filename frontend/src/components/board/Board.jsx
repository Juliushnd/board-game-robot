import { useGame } from '../../GameContext.jsx'
import { useEffect, useMemo, useState } from 'react'
import { Chessboard } from 'react-chessboard'

/**
 * Displays the current board state and allows moving pieces or editing the board if certain conditions are met.
 *
 * During normal play, only moves made for the human player are allowed and lead to a call to `GameContext.makeMove()`.
 *
 * When `editingBoard` is set to `true`, any board modification is allowed and leads to a call to
 * `GameContext.setInitialPosition()`.
 *
 * When `editingMoves` is set to `true`, any normal move is allowed and leads to a call to `GameContext.setHistory()`.
 *
 * Setting both `editingBoard` and `editingMoves` to `true` is not supported.
 *
 * @param {String} id The ID of the `Chessboard` component.
 * @param {Boolean} editingBoard Whether the board is currently being edited.
 * @param {Boolean} editingMoves Whether the sequence of moves is currently being edited.
 * @returns {JSX.Element}
 * @component
 */
export default function Board({ id, editingBoard, editingMoves }) {
  const game = useGame()

  const [position, setPosition] = useState({})

  const agent = useMemo(() => game.availableAgents.find(a => a.key === game.agent), [game.availableAgents, game.agent])

  useEffect(() => {
    setPosition({
      ...game.currentPosition,
    })
  }, [game.currentPosition])

  const onPieceDrop = (sourceSquare, targetSquare, piece) => {
    if (!editingBoard && !editingMoves) {
      if (!game.gameStarted || game.gameOver) {
        return false
      }
      if (game.currentPlayerColor !== game.humanPlayerColor && agent && !agent.allowFrontendMoves) {
        return false
      }
    }

    const newPosition = { ...position }
    delete newPosition[sourceSquare]
    newPosition[targetSquare] = piece
    setPosition(newPosition)

    if (editingBoard) {
      game.setInitialPosition(newPosition)
      return true
    }

    /** @type {Move} */
    const move = {
      color: game.currentPlayerColor,
      from: sourceSquare,
      to: targetSquare,
      promotion: piece[1].toLowerCase() ?? 'q',
    }

    if (editingMoves) {
      const newHistory = game.history.slice()
      newHistory.push(move)
      game.setHistory(newHistory)
      return true
    }

    game.makeMove(move)
    return true
  }

  const onPieceDropOffBoard = (sourceSquare) => {
    if (!editingBoard) {
      return
    }

    const newPosition = { ...position }
    delete newPosition[sourceSquare]
    setPosition(newPosition)
    game.setInitialPosition(newPosition)
  }

  const onSparePieceDrop = (piece, targetSquare) => {
    if (!editingBoard) {
      return false
    }

    const newPosition = {
      ...position,
      [targetSquare]: piece,
    }
    setPosition(newPosition)
    game.setInitialPosition(newPosition)
    return true
  }

  const isDraggablePiece = ({ piece: piece }) => {
    if (!game.gameStarted) {
      return editingBoard
    } else {
      const color = piece[0]
      if (game.currentPlayerColor !== color) {
        return false
      }
      return color === game.humanPlayerColor || !agent || agent.allowFrontendMoves || editingMoves
    }
  }

  return (
    <Chessboard
      id={id}
      position={position}
      // This key is needed to rerender the Chessboard component when the game starts or the board is edited because the
      // isDraggablePiece function is not properly reactive.
      key={JSON.stringify({ editingBoard: editingBoard, gameStarted: game.gameStarted })}
      boardOrientation={game.humanPlayerColor === 'w' ? 'white' : 'black'}
      onPieceDrop={onPieceDrop}
      onPieceDropOffBoard={onPieceDropOffBoard}
      onSparePieceDrop={onSparePieceDrop}
      dropOffBoardAction={editingBoard ? 'trash' : 'snapback'}
      isDraggablePiece={isDraggablePiece}
    />
  )
}
