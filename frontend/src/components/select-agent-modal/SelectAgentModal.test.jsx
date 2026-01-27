import { fireEvent, render, screen } from '@testing-library/react'
import SelectAgentModal from './SelectAgentModal.jsx'
import { GameContext } from '../../GameContext.jsx'
import { describe, it, vi, beforeEach, expect } from 'vitest'

describe('SelectAgentModal', () => {
  const availableAgents = [
    { key: 'manual', name: 'Manual' },
    { key: 'random', name: 'Random' },
    { key: 'foo', name: 'Bar' },
  ]
  const setAgent = vi.fn()
  const onHide = vi.fn()

  const game = {
    availableAgents,
    setAgent,
  }

  beforeEach(() => {
    setAgent.mockReset()
    onHide.mockReset()
  })

  it('should allow the user to choose an agent', () => {
    render((
      <GameContext.Provider value={game}>
        <SelectAgentModal show={true} onHide={onHide} />
      </GameContext.Provider>
    ))

    for (const agent of availableAgents) {
      const button = screen.getByRole('button', { name: agent.name })
      fireEvent.click(button)
      expect(setAgent).toHaveBeenLastCalledWith(agent.key)
      expect(onHide).toHaveBeenCalled()
    }
  })

  it('should be closeable using the close button', () => {
    render((
      <GameContext.Provider value={game}>
        <SelectAgentModal show={true} onHide={onHide} />
      </GameContext.Provider>
    ))

    const button = screen.getByLabelText('Close')
    fireEvent.click(button)
    expect(setAgent).not.toHaveBeenCalled()
    expect(onHide).toHaveBeenCalled()
  })

  it('should be closeable using the cancel button', () => {
    render((
      <GameContext.Provider value={game}>
        <SelectAgentModal show={true} onHide={onHide} />
      </GameContext.Provider>
    ))

    const button = screen.getByRole('button', { name: 'Cancel' })
    fireEvent.click(button)
    expect(setAgent).not.toHaveBeenCalled()
    expect(onHide).toHaveBeenCalled()
  })
})
