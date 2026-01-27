import { useGame } from '../../GameContext.jsx'
import { faPlay, faPlus, faStop } from '@fortawesome/free-solid-svg-icons'
import IconButton from '../icon-button/IconButton.jsx'

/**
 * Buttons to start, end, and restart the game.
 *
 * @param {Boolean} disabled Whether the buttons should be disabled.
 * @returns {JSX.Element}
 * @component
 */
export default function GameControls({ disabled }) {
  const game = useGame()

  if (!game.gameStarted) {
    return (
      <IconButton variant="success" icon={faPlay} onClick={game.startGame} disabled={disabled}>
        Start game
      </IconButton>
    )
  } else if (!game.gameOver) {
    return (
      <IconButton variant="danger" icon={faStop} onClick={game.endGame} disabled={disabled}>
        End game
      </IconButton>
    )
  } else {
    return (
      <IconButton variant="success" icon={faPlus} onClick={game.newGame} disabled={disabled}>
        New game
      </IconButton>
    )
  }
}
