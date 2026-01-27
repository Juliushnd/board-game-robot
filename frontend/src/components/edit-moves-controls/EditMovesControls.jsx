import { useGame } from '../../GameContext.jsx'
import { useRef } from 'react'
import { faCheck, faList, faTrash } from '@fortawesome/free-solid-svg-icons'
import IconButton from '../icon-button/IconButton.jsx'

/**
 * Button for enabling/disabling move editing and for discarding any changes made to the move sequence. To be displayed
 * after the game has started.
 *
 * @param {Boolean} editingMoves Whether the move sequence is currently being edited.
 * @param setEditingMoves Callback to enable/disable move editing.
 * @returns {JSX.Element}
 * @component
 */
export default function EditMovesControls({ editingMoves, setEditingMoves }) {
  const game = useGame()

  const prevHistory = useRef(game.history)

  const onBeginEdit = () => {
    if (!game.gameStarted) {
      return
    }
    prevHistory.current = game.history.slice()
    game.pauseGame().then(() => setEditingMoves(true))
  }

  const onDiscard = () => {
    if (!game.gameStarted) {
      return
    }
    game.setHistory(prevHistory.current)
    onFinishEdit()
  }

  const onFinishEdit = () => {
    if (!game.gameStarted) {
      return
    }
    setEditingMoves(false)
    game.startGame()
  }

  if (!editingMoves) {
    return (
      <IconButton key="edit" variant="outline-secondary" icon={faList} onClick={onBeginEdit}>
        Edit moves
      </IconButton>
    )
  } else {
    return (
      <>
        <IconButton key="discard" variant="outline-danger" icon={faTrash} onClick={onDiscard}>
          Discard changes
        </IconButton>
        <IconButton key="save" variant="success" icon={faCheck} onClick={onFinishEdit}>
          Save changes
        </IconButton>
      </>
    )
  }
}
