import { fireEvent, render, screen } from '@testing-library/react'
import EditMovesControls from './EditMovesControls.jsx'
import { GameContext } from '../../GameContext.jsx'
import { describe, it, vi, beforeEach, expect } from 'vitest'

describe('EditMovesControls', () => {
  const setEditingMoves = vi.fn()
  const startGame = vi.fn()
  const pauseGame = vi.fn(async () => {})
  const setHistory = vi.fn()

  let game
  beforeEach(() => {
    game = {
      startGame,
      pauseGame,
      gameStarted: true,
      history: [],
      setHistory,
    }
    setEditingMoves.mockReset()
    startGame.mockReset()
    pauseGame.mockReset()
    setHistory.mockReset()
  })

  it('should show the edit moves button when not currently editing moves', () => {
    render((
      <GameContext.Provider value={game}>
        <EditMovesControls editingMoves={false} />
      </GameContext.Provider>
    ))

    const editMovesButton = screen.queryByRole('button', { name: 'Edit moves' })
    const saveChangesButton = screen.queryByRole('button', { name: 'Save changes' })
    const discardChangesButton = screen.queryByRole('button', { name: 'Discard changes' })
    expect(editMovesButton).toBeInTheDocument()
    expect(saveChangesButton).not.toBeInTheDocument()
    expect(discardChangesButton).not.toBeInTheDocument()
  })

  it('should show the save and discard changes buttons when currently editing moves', () => {
    render((
      <GameContext.Provider value={game}>
        <EditMovesControls editingMoves={true} />
      </GameContext.Provider>
    ))

    const editMovesButton = screen.queryByRole('button', { name: 'Edit moves' })
    const saveChangesButton = screen.queryByRole('button', { name: 'Save changes' })
    const discardChangesButton = screen.queryByRole('button', { name: 'Discard changes' })
    expect(editMovesButton).not.toBeInTheDocument()
    expect(saveChangesButton).toBeInTheDocument()
    expect(discardChangesButton).toBeInTheDocument()
  })

  it('should allow editing moves and saving the changes', async () => {
    const { rerender } = render((
      <GameContext.Provider value={game}>
        <EditMovesControls editingMoves={false} setEditingMoves={setEditingMoves} />
      </GameContext.Provider>
    ))

    const editMovesButton = screen.getByRole('button', { name: 'Edit moves' })
    fireEvent.click(editMovesButton)

    expect(pauseGame).toHaveBeenCalled()
    // setEditingMoves is called after pauseGame has finished.
    await vi.waitFor(() => expect(setEditingMoves).toHaveBeenLastCalledWith(true))
    expect(startGame).not.toHaveBeenCalled()
    expect(setHistory).not.toHaveBeenCalled()

    setEditingMoves.mockReset()
    pauseGame.mockReset()

    rerender((
      <GameContext.Provider value={game}>
        <EditMovesControls editingMoves={true} setEditingMoves={setEditingMoves} />
      </GameContext.Provider>
    ))

    const saveChangesButton = screen.getByRole('button', { name: 'Save changes' })
    fireEvent.click(saveChangesButton)

    expect(setEditingMoves).toHaveBeenLastCalledWith(false)
    expect(pauseGame).not.toHaveBeenCalled()
    expect(startGame).toHaveBeenCalled()
    expect(setHistory).not.toHaveBeenCalled()
  })

  it('should allow editing moves and discarding the changes', async () => {
    game.history = [{ from: 'a1', to: 'a2' }, { from: 'b1', to: 'b2' }]

    const { rerender } = render((
      <GameContext.Provider value={game}>
        <EditMovesControls editingMoves={false} setEditingMoves={setEditingMoves} />
      </GameContext.Provider>
    ))

    const editMovesButton = screen.getByRole('button', { name: 'Edit moves' })
    fireEvent.click(editMovesButton)

    expect(pauseGame).toHaveBeenCalled()
    // setEditingMoves is called after pauseGame has finished.
    await vi.waitFor(() => expect(setEditingMoves).toHaveBeenLastCalledWith(true))
    expect(startGame).not.toHaveBeenCalled()
    expect(setHistory).not.toHaveBeenCalled()

    setEditingMoves.mockReset()
    pauseGame.mockReset()

    rerender((
      <GameContext.Provider value={game}>
        <EditMovesControls editingMoves={true} setEditingMoves={setEditingMoves} />
      </GameContext.Provider>
    ))

    const discardChangesButton = screen.getByRole('button', { name: 'Discard changes' })
    fireEvent.click(discardChangesButton)

    expect(setEditingMoves).toHaveBeenLastCalledWith(false)
    expect(pauseGame).not.toHaveBeenCalled()
    expect(startGame).toHaveBeenCalled()
    expect(setHistory).toHaveBeenLastCalledWith(game.history)
  })

  it('should not react when game is not started', () => {
    game.gameStarted = false

    const { rerender } = render((
      <GameContext.Provider value={game}>
        <EditMovesControls editingMoves={false} setEditingMoves={setEditingMoves} />
      </GameContext.Provider>
    ))

    const editMovesButton = screen.getByRole('button', { name: 'Edit moves' })
    fireEvent.click(editMovesButton)

    expect(setEditingMoves).not.toHaveBeenCalled()
    expect(pauseGame).not.toHaveBeenCalled()
    expect(startGame).not.toHaveBeenCalled()
    expect(setHistory).not.toHaveBeenCalled()

    rerender((
      <GameContext.Provider value={game}>
        <EditMovesControls editingMoves={true} setEditingMoves={setEditingMoves} />
      </GameContext.Provider>
    ))

    const saveChangesButton = screen.getByRole('button', { name: 'Save changes' })
    fireEvent.click(saveChangesButton)

    const discardChangesButton = screen.getByRole('button', { name: 'Discard changes' })
    fireEvent.click(discardChangesButton)

    expect(setEditingMoves).not.toHaveBeenCalled()
    expect(pauseGame).not.toHaveBeenCalled()
    expect(startGame).not.toHaveBeenCalled()
    expect(setHistory).not.toHaveBeenCalled()
  })
})
