import { useGame } from '../../GameContext.jsx'
import { useEffect, useRef, useState } from 'react'
import { faPlus, faRobot, faUser } from '@fortawesome/free-solid-svg-icons'
import Modal from 'react-bootstrap/Modal'
import PlayerCard from '../player-card/PlayerCard.jsx'
import './GameOverModal.css'
import IconButton from '../icon-button/IconButton.jsx'

/**
 * Modal which automatically pops up when the game has ended by checkmate or draw and displays the result.
 *
 * @returns {JSX.Element}
 * @component
 */
export default function GameOverModal() {
  const game = useGame()

  const [show, setShow] = useState(false)

  const prevGameOver = useRef(game.gameOver)
  useEffect(() => {
    if (game.gameOver && (game.isCheckmate || game.isDraw) && !game.gamePaused) {
      if (!prevGameOver.current) {
        setShow(true)
      }
    } else {
      setShow(false)
    }
    prevGameOver.current = game.gameOver
  }, [game.gameOver, game.isCheckmate, game.isDraw, game.gamePaused, setShow, prevGameOver])

  const onNewGameClicked = () => {
    setShow(false)
    game.newGame()
  }

  let result = null
  if (game.gameOver) {
    if (game.isDraw) {
      result = 'A draw has been reached!'
    } else if (game.isCheckmate) {
      let winner
      if (game.currentPlayerColor === game.humanPlayerColor) {
        winner = <PlayerCard name="Robot" icon={faRobot} />
      } else {
        winner = <PlayerCard name="Human" icon={faUser} />
      }
      result = <>{winner} has won the game!</>
    } else {
      result = 'The game has been ended.'
    }
  }
  return (
    <Modal show={show} onHide={() => setShow(false)} centered>
      <Modal.Header closeButton>
        <Modal.Title>Game Over</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <div className="game-over-result">
          {result}
        </div>
      </Modal.Body>
      <Modal.Footer>
        <IconButton variant="success" icon={faPlus} onClick={onNewGameClicked}>
          New game
        </IconButton>
      </Modal.Footer>
    </Modal>
  )
}
