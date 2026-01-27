import { fireEvent, render, screen } from '@testing-library/react'
import GameOverModal from './GameOverModal.jsx'
import { GameContext } from '../../GameContext.jsx'
import { describe, it, vi, beforeEach, expect } from 'vitest'

describe('GameOverModal', () => {
  const newGame = vi.fn()

  let game
  beforeEach(() => {
    game = {
      newGame,
      isPaused: false,
      gameOver: false,
      isCheckmate: false,
      isDraw: false,
      humanPlayerColor: 'w',
      currentPlayerColor: 'w',
    }
    newGame.mockReset()
  })

  it('should automatically show itself when the game is over by checkmate', () => {
    const { rerender } = render((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    expect(screen.queryByText('Game Over')).not.toBeInTheDocument()

    game = {
      ...game,
      gameOver: true,
      isCheckmate: true,
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    expect(screen.getByText('Game Over')).toBeInTheDocument()
  })

  it('should automatically show itself when the game is over by draw', () => {
    const { rerender } = render((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    expect(screen.queryByText('Game Over')).not.toBeInTheDocument()

    game = {
      ...game,
      gameOver: true,
      isDraw: true,
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    expect(screen.getByText('Game Over')).toBeInTheDocument()
  })

  it('should not automatically show itself when the game is over but not by checkmate or draw', () => {
    const { rerender } = render((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    expect(screen.queryByText('Game Over')).not.toBeInTheDocument()

    game = {
      ...game,
      gameOver: true,
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    expect(screen.queryByText('Game Over')).not.toBeInTheDocument()
  })

  it('should not automatically show itself when the game is over but paused', () => {
    game.gamePaused = true

    const { rerender } = render((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    expect(screen.queryByText('Game Over')).not.toBeInTheDocument()

    game = {
      ...game,
      gameOver: true,
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    expect(screen.queryByText('Game Over')).not.toBeInTheDocument()
  })

  it('should automatically hide itself when the game is not over anymore', async () => {
    const { rerender } = render((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    game = {
      ...game,
      gameOver: true,
      isCheckmate: true,
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    await vi.waitFor(() => expect(screen.getByText('Game Over')).toBeInTheDocument())

    game = {
      ...game,
      gameOver: false,
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    await vi.waitFor(() => expect(screen.queryByText('Game Over')).not.toBeInTheDocument())
  })

  it('should display the winner if the game is over by checkmate', async () => {
    const { rerender } = render((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    game = {
      ...game,
      gameOver: true,
      isCheckmate: true,
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    await vi.waitFor(() => expect(screen.getByText('Game Over')).toBeInTheDocument())
    expect(screen.getByText('Robot')).toBeInTheDocument()
    expect(screen.queryByText('Human')).not.toBeInTheDocument()
    expect(screen.getByText('has won the game!')).toBeInTheDocument()

    game = {
      ...game,
      currentPlayerColor: 'b',
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    expect(screen.queryByText('Robot')).not.toBeInTheDocument()
    expect(screen.getByText('Human')).toBeInTheDocument()
    expect(screen.getByText('has won the game!')).toBeInTheDocument()
  })

  it('should announce a draw if the game is over by draw', async () => {
    const { rerender } = render((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    game = {
      ...game,
      gameOver: true,
      isDraw: true,
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    await vi.waitFor(() => expect(screen.getByText('Game Over')).toBeInTheDocument())
    expect(screen.getByText('A draw has been reached!')).toBeInTheDocument()
  })

  it('should allow starting a new game', async () => {
    const { rerender } = render((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    game = {
      ...game,
      gameOver: true,
      isDraw: true,
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    await vi.waitFor(() => expect(screen.getByText('Game Over')).toBeInTheDocument())

    const button = screen.getByRole('button', { name: 'New game' })
    fireEvent.click(button)

    await vi.waitFor(() => expect(screen.queryByText('Game Over')).not.toBeInTheDocument())

    expect(newGame).toHaveBeenCalled()
  })

  it('should hide itself when the close button is clicked', async () => {
    const { rerender } = render((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    game = {
      ...game,
      gameOver: true,
      isDraw: true,
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameOverModal />
      </GameContext.Provider>
    ))

    await vi.waitFor(() => expect(screen.getByText('Game Over')).toBeInTheDocument())

    const button = screen.getByLabelText('Close')
    fireEvent.click(button)

    await vi.waitFor(() => expect(screen.queryByText('Game Over')).not.toBeInTheDocument())

    expect(newGame).not.toHaveBeenCalled()
  })
})
