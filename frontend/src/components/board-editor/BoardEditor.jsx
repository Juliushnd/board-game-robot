import { useGame } from '../../GameContext.jsx'
import SparePieceRow from '../spare-piece-row/SparePieceRow.jsx'
import './BoardEditor.css'

/**
 * Editor UI to be displayed in the right panel of the frontend app when the board is being edited.
 *
 * Offers a list of black and white chess pieces to be dragged onto the chessboard.
 *
 * @param {String} dndId The ID of the `Chessboard` component.
 * @returns {JSX.Element}
 * @component
 */
export default function BoardEditor({ dndId }) {
  const game = useGame()

  return (
    <div className="board-editor">
      <SparePieceRow color={game.humanPlayerColor === 'w' ? 'b' : 'w'} dndId={dndId} />
      <div className="board-editor-spacer"></div>
      <SparePieceRow color={game.humanPlayerColor} dndId={dndId} />
    </div>
  )
}
