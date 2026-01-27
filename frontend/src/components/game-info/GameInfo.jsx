import { useGame } from '../../GameContext.jsx'
import Table from 'react-bootstrap/Table'
import { faUndo } from '@fortawesome/free-solid-svg-icons'
import './GameInfo.css'
import IconButton from '../icon-button/IconButton.jsx'

/**
 * Game info UI to be displayed in the right panel of the frontend app during the game.
 *
 * Displays the move sequence and the current game state (i.e., whose turn it is or whether the game has ended).
 *
 * If `allowUndo` is set to `true`, an "Undo" button is displayed which allows undoing the last move.
 *
 * @param {Boolean} allowUndo Whether the "Undo" button should be displayed.
 * @returns {JSX.Element}
 * @component
 */
export default function GameInfo({ allowUndo }) {
  const game = useGame()

  const undo = () => {
    if (!allowUndo) {
      return
    }
    const newHistory = game.history.slice(0, -1)
    game.setHistory(newHistory)
  }

  let rows = []
  for (let i = 0; i < game.history.length; i += 2) {
    rows.push((
      <tr key={i / 2}>
        <td>
          {i / 2 + 1}.
        </td>
        <td>
          {game.history[i].san}
        </td>
        <td>
          {i + 1 < game.history.length && game.history[i + 1].san}
        </td>
      </tr>
    ))
  }
  let status
  if (!game.gameStarted) {
    status = 'Game not running'
  } else if (!game.gameOver) {
    status = game.currentPlayerColor === 'w' ? 'White to move' : 'Black to move'
  } else if (game.isDraw) {
    status = 'Game over (draw)'
  } else if (game.isCheckmate) {
    const color = game.currentPlayerColor === 'b' ? 'white' : 'black'
    status = `Game over (${color} won)`
  } else {
    status = 'Game over'
  }
  return (
    <div className="game-info">
      <div className="history-table-container">
        <Table striped className="history-table">
          <tbody>
            {rows}
          </tbody>
        </Table>
      </div>
      <div className="game-info-footer">
        {allowUndo && (
          <IconButton key="undo" variant="none" icon={faUndo} onClick={undo}>
            Undo last move
          </IconButton>
        )}
        <div>
          {status}
        </div>
      </div>
    </div>
  )
}
