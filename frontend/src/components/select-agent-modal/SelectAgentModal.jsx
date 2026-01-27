import { useGame } from '../../GameContext.jsx'
import Modal from 'react-bootstrap/Modal'
import Button from 'react-bootstrap/Button'
import './SelectAgentModal.css'

/**
 * Modal which allows changing the active agent.
 *
 * @param {Boolean} show Whether the modal should be visible.
 * @param {Function} onHide Callback to hide the modal.
 * @returns {JSX.Element}
 * @component
 */
export default function SelectAgentModal({ show, onHide }) {
  const game = useGame()

  function onSelect(agent) {
    game.setAgent(agent)
    onHide()
  }
  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>Choose agent</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <div className="agent-options">
          {game.availableAgents.map(agent => <Button key={agent.key} variant="outline-dark" onClick={() => onSelect(agent.key)}>{agent.name}</Button>)}
        </div>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="outline-secondary" onClick={onHide}>
          Cancel
        </Button>
      </Modal.Footer>
    </Modal>
  )
}
