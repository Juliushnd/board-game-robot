import { SparePiece } from 'react-chessboard'
import './SparePieceRow.css'

/**
 * One row of spare chess pieces to be dragged onto the `Chessboard` component during board editing.
 *
 * @param {Color} color Color of the pieces.
 * @param {String} dndId The ID of the `Chessboard` component.
 * @returns {JSX.Element}
 * @component
 */
export default function SparePieceRow({ color, dndId }) {
  const pieceTypes = ['P', 'N', 'B', 'R', 'Q', 'K']

  return (
    <div className="spare-piece-row">
      {pieceTypes.map(type => (
        <SparePiece key={color + type} piece={color + type} dndId={dndId} width="100%" />
      ))}
    </div>
  )
}
