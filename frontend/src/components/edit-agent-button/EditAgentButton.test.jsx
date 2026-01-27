import { fireEvent, render, screen } from '@testing-library/react'
import EditAgentButton from './EditAgentButton.jsx'
import { GameContext } from '../../GameContext.jsx'
import { describe, it, beforeEach, expect } from 'vitest'
import { act } from 'react'

describe('EditAgentButton', () => {
  const availableAgents = [
    { key: 'manual', name: 'Manual' },
    { key: 'random', name: 'Random' },
    { key: 'foo', name: 'Bar' },
  ]

  let game
  beforeEach(() => {
    game = {
      availableAgents,
      agent: null,
      gamePaused: false,
    }
  })

  it('should show the name of the currently selected agent', () => {
    const { rerender } = render((
      <GameContext.Provider value={game}>
        <EditAgentButton />
      </GameContext.Provider>
    ))

    expect(screen.getByRole('button', { name: 'AI: None' })).toBeInTheDocument()

    for (const agent of availableAgents) {
      game.agent = agent.key
      rerender((
        <GameContext.Provider value={game}>
          <EditAgentButton />
        </GameContext.Provider>
      ))
      expect(screen.getByRole('button', { name: 'AI: ' + agent.name })).toBeInTheDocument()
    }
  })

  it('should open the agent selection modal on click and close it on cancel', async () => {
    const { rerender } = render((
      <GameContext.Provider value={game}>
        <EditAgentButton />
      </GameContext.Provider>
    ))

    const button = screen.getByRole('button', { name: 'AI: None' })
    await act(() => fireEvent.click(button))
    rerender((
      <GameContext.Provider value={game}>
        <EditAgentButton />
      </GameContext.Provider>
    ))
    expect(screen.getByText('Choose agent')).toBeInTheDocument()

    const cancelButton = screen.getByRole('button', { name: 'Cancel' })
    await act(() => fireEvent.click(cancelButton))
    rerender((
      <GameContext.Provider value={game}>
        <EditAgentButton />
      </GameContext.Provider>
    ))
    expect(screen.queryByText('Choose agent')).not.toBeInTheDocument()
  })

  it('should display "paused" next to the agent name if the game is paused', () => {
    game.gamePaused = true

    render((
      <GameContext.Provider value={game}>
        <EditAgentButton />
      </GameContext.Provider>
    ))

    expect(screen.getByRole('button', { name: 'AI: None (paused)' })).toBeInTheDocument()
  })
})
