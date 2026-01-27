import { fireEvent, render, screen } from '@testing-library/react'
import GameControls from './GameControls.jsx'
import { GameContext } from '../../GameContext.jsx'
import { describe, it, vi, beforeEach, expect } from 'vitest'

describe('GameControls', () => {
  const startGame = vi.fn()
  const endGame = vi.fn()
  const newGame = vi.fn()

  let game
  beforeEach(() => {
    game = {
      startGame,
      endGame,
      newGame,
    }
    startGame.mockReset()
    endGame.mockReset()
    newGame.mockReset()
  })

  it('should show start game button before game has started', () => {
    game.gameStarted = false
    game.gameOver = false

    render((
      <GameContext.Provider value={game}>
        <GameControls />
      </GameContext.Provider>
    ))

    const startGameButton = screen.queryByRole('button', { name: 'Start game' })
    const endGameButton = screen.queryByRole('button', { name: 'End game' })
    const newGameButton = screen.queryByRole('button', { name: 'New game' })
    expect(startGameButton).toBeInTheDocument()
    expect(endGameButton).not.toBeInTheDocument()
    expect(newGameButton).not.toBeInTheDocument()
    fireEvent.click(startGameButton)
    expect(startGame).toHaveBeenCalled()
    expect(endGame).not.toHaveBeenCalled()
    expect(newGame).not.toHaveBeenCalled()
  })

  it('should show end game button after game has started', () => {
    game.gameStarted = true
    game.gameOver = false

    render((
      <GameContext.Provider value={game}>
        <GameControls />
      </GameContext.Provider>
    ))

    const startGameButton = screen.queryByRole('button', { name: 'Start game' })
    const endGameButton = screen.queryByRole('button', { name: 'End game' })
    const newGameButton = screen.queryByRole('button', { name: 'New game' })
    expect(startGameButton).not.toBeInTheDocument()
    expect(endGameButton).toBeInTheDocument()
    expect(newGameButton).not.toBeInTheDocument()
    fireEvent.click(endGameButton)
    expect(startGame).not.toHaveBeenCalled()
    expect(endGame).toHaveBeenCalled()
    expect(newGame).not.toHaveBeenCalled()
  })

  it('should show new game button after game has ended', () => {
    game.gameStarted = true
    game.gameOver = true

    render((
      <GameContext.Provider value={game}>
        <GameControls />
      </GameContext.Provider>
    ))

    const startGameButton = screen.queryByRole('button', { name: 'Start game' })
    const endGameButton = screen.queryByRole('button', { name: 'End game' })
    const newGameButton = screen.queryByRole('button', { name: 'New game' })
    expect(startGameButton).not.toBeInTheDocument()
    expect(endGameButton).not.toBeInTheDocument()
    expect(newGameButton).toBeInTheDocument()
    fireEvent.click(newGameButton)
    expect(startGame).not.toHaveBeenCalled()
    expect(endGame).not.toHaveBeenCalled()
    expect(newGame).toHaveBeenCalled()
  })

  it('should be able to show a disabled start game button', () => {
    game.gameStarted = false
    game.gameOver = false

    render((
      <GameContext.Provider value={game}>
        <GameControls disabled={true} />
      </GameContext.Provider>
    ))

    const button = screen.getByRole('button', { name: 'Start game' })
    expect(button).toBeDisabled()
  })

  it('should be able to show a disabled end game button', () => {
    game.gameStarted = true
    game.gameOver = false

    render((
      <GameContext.Provider value={game}>
        <GameControls disabled={true} />
      </GameContext.Provider>
    ))

    const button = screen.getByRole('button', { name: 'End game' })
    expect(button).toBeDisabled()
  })

  it('should be able to show a disabled new game button', () => {
    game.gameStarted = true
    game.gameOver = true

    render((
      <GameContext.Provider value={game}>
        <GameControls disabled={true} />
      </GameContext.Provider>
    ))

    const button = screen.getByRole('button', { name: 'New game' })
    expect(button).toBeDisabled()
  })
})
