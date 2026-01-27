import { fireEvent, render, screen } from '@testing-library/react'
import FlipBoardButton from './FlipBoardButton.jsx'
import { GameContext } from '../../GameContext.jsx'
import { describe, it, vi, beforeEach, expect } from 'vitest'

describe('FlipBoardButton', () => {
  const setHumanPlayerColor = vi.fn()

  let game
  beforeEach(() => {
    game = {
      setHumanPlayerColor,
      gameStarted: false,
      humanPlayerColor: 'w',
    }
    setHumanPlayerColor.mockReset()
  })

  it('should set the human player\'s color to black on click if it was white before', () => {
    render((
      <GameContext.Provider value={game}>
        <FlipBoardButton />
      </GameContext.Provider>
    ))

    const button = screen.getByRole('button', { name: 'Flip board' })
    fireEvent.click(button)
    expect(setHumanPlayerColor).toHaveBeenLastCalledWith('b')
  })

  it('should set the human player\'s color to white on click if it was black before', () => {
    game.humanPlayerColor = 'b'

    render((
      <GameContext.Provider value={game}>
        <FlipBoardButton />
      </GameContext.Provider>
    ))

    const button = screen.getByRole('button', { name: 'Flip board' })
    fireEvent.click(button)
    expect(setHumanPlayerColor).toHaveBeenLastCalledWith('w')
  })

  it('should be disabled if the game has started', () => {
    game.gameStarted = true

    render((
      <GameContext.Provider value={game}>
        <FlipBoardButton />
      </GameContext.Provider>
    ))

    const button = screen.getByRole('button', { name: 'Flip board' })
    expect(button).toBeDisabled()
  })
})
