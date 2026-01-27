import { useGame } from '../../GameContext.jsx'
import Modal from 'react-bootstrap/Modal'
import Button from 'react-bootstrap/Button'

/**
 * Modal which automatically pops up when an error occurs.
 *
 * @returns {JSX.Element}
 * @component
 */
export default function ErrorModal() {
  const game = useGame()

  return (
    <Modal show={game.error} onHide={() => game.clearError()} centered>
      <Modal.Header closeButton>
        <Modal.Title>Error</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {game.error}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="primary" onClick={() => game.clearError()}>
          Ok
        </Button>
      </Modal.Footer>
    </Modal>
  )
}
