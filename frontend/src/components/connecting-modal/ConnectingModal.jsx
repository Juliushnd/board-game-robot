import Modal from 'react-bootstrap/Modal'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import './ConnectingModal.css'
import { faCircleNotch } from '@fortawesome/free-solid-svg-icons'

/**
 * Modal to be shown while the connection to the backend is being established.
 *
 * @param {Boolean} show Whether the modal should be visible.
 * @returns {JSX.Element}
 * @component
 */
export default function ConnectingModal({ show }) {
  return (
    <Modal show={show} centered>
      <Modal.Body>
        <div className="connecting">
          <p>Connecting to backend</p>
          <FontAwesomeIcon icon={faCircleNotch} spin={true} />
        </div>
      </Modal.Body>
    </Modal>
  )
}
