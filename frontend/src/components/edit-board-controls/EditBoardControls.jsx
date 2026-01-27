import { useGame } from '../../GameContext.jsx'
import { faCheck, faChessBoard, faTrash } from '@fortawesome/free-solid-svg-icons'
import IconButton from '../icon-button/IconButton.jsx'

/**
 * Buttons for enabling/disabling the board editing and for resetting the board. To be displayed before the game starts.
 *
 * @param {Boolean} editingBoard Whether the board is currently being edited.
 * @param {Function} setEditingBoard Callback to enable/disable board editing.
 * @returns {JSX.Element}
 * @component
 */
export default function EditBoardControls({ editingBoard, setEditingBoard }) {
  const game = useGame()

  const startEditing = () => {
    setEditingBoard(true)
  }
  const stopEditing = () => {
    setEditingBoard(false)
  }
  const resetBoard = () => {
    game.newGame()
    stopEditing()
  }

  if (!editingBoard) {
    return (
      <IconButton key="edit" variant="outline-secondary" icon={faChessBoard} onClick={startEditing}>
        Edit board
      </IconButton>
    )
  } else {
    return (
      <>
        <IconButton key="reset" variant="outline-danger" icon={faTrash} onClick={resetBoard}>
          Restore default
        </IconButton>
        <IconButton key="save" variant="success" icon={faCheck} onClick={stopEditing}>
          Save changes
        </IconButton>
      </>
    )
  }
}
