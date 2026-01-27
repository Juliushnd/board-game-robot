import { useGame } from '../../GameContext.jsx'
import { faRotate } from '@fortawesome/free-solid-svg-icons'
import IconButton from '../icon-button/IconButton.jsx'

/**
 * Button to flip the board orientation.
 *
 * @returns {JSX.Element}
 * @component
 */
export default function FlipBoardButton() {
  const game = useGame()

  function flipBoard() {
    if (game.gameStarted) {
      return
    }
    game.setHumanPlayerColor(game.humanPlayerColor === 'w' ? 'b' : 'w')
  }

  return (
    <IconButton variant="outline-secondary" icon={faRotate} onClick={flipBoard} disabled={game.gameStarted}>
      Flip board
    </IconButton>
  )
}
