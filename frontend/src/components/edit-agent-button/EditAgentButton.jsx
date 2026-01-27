import { useGame } from '../../GameContext.jsx'
import { useMemo, useState } from 'react'
import { faEdit } from '@fortawesome/free-solid-svg-icons'
import SelectAgentModal from '../select-agent-modal/SelectAgentModal.jsx'
import IconButton from '../icon-button/IconButton.jsx'

/**
 * Button which displays the currently active agent and shows a `SelectAgentModal` when pressed.
 *
 * @returns {JSX.Element}
 * @component
 */
export default function EditAgentButton() {
  const game = useGame()

  const [show, setShow] = useState(false)

  const agentName = useMemo(() => {
    const agentObj = game.availableAgents.find(agentObj => agentObj.key === game.agent)
    if (agentObj) {
      return agentObj.name
    } else {
      return 'None'
    }
  }, [game.agent, game.availableAgents])

  return (
    <>
      <IconButton variant="none" iconRight={faEdit} onClick={() => setShow(true)}>
        AI: {agentName}
        {game.gamePaused && <> (paused)</>}
      </IconButton>
      <SelectAgentModal
        show={show}
        onHide={() => setShow(false)}
      />
    </>
  )
}
