import { fireEvent, render, screen } from '@testing-library/react'
import EditBoardControls from './EditBoardControls.jsx'
import { GameContext } from '../../GameContext.jsx'
import { describe, it, vi, beforeEach, expect } from 'vitest'

describe('EditBoardControls', () => {
  const setEditingBoard = vi.fn()
  const newGame = vi.fn()

  const game = {
    newGame,
  }

  beforeEach(() => {
    setEditingBoard.mockReset()
    newGame.mockReset()
  })

  it('should show the edit board button when not currently editing board', () => {
    render((
      <GameContext.Provider value={game}>
        <EditBoardControls editingBoard={false} />
      </GameContext.Provider>
    ))

    const editBoardButton = screen.queryByRole('button', { name: 'Edit board' })
    const saveChangesButton = screen.queryByRole('button', { name: 'Save changes' })
    const restoreDefaultButton = screen.queryByRole('button', { name: 'Restore default' })
    expect(editBoardButton).toBeInTheDocument()
    expect(saveChangesButton).not.toBeInTheDocument()
    expect(restoreDefaultButton).not.toBeInTheDocument()
  })

  it('should show the save changes and restore default buttons when currently editing board', () => {
    render((
      <GameContext.Provider value={game}>
        <EditBoardControls editingBoard={true} />
      </GameContext.Provider>
    ))

    const editBoardButton = screen.queryByRole('button', { name: 'Edit board' })
    const saveChangesButton = screen.queryByRole('button', { name: 'Save changes' })
    const restoreDefaultButton = screen.queryByRole('button', { name: 'Restore default' })
    expect(editBoardButton).not.toBeInTheDocument()
    expect(saveChangesButton).toBeInTheDocument()
    expect(restoreDefaultButton).toBeInTheDocument()
  })

  it('should allow editing board and saving the changes', () => {
    const { rerender } = render((
      <GameContext.Provider value={game}>
        <EditBoardControls editingBoard={false} setEditingBoard={setEditingBoard} />
      </GameContext.Provider>
    ))

    const editBoardButton = screen.getByRole('button', { name: 'Edit board' })
    fireEvent.click(editBoardButton)
    expect(setEditingBoard).toHaveBeenLastCalledWith(true)
    expect(newGame).not.toHaveBeenCalled()

    rerender((
      <GameContext.Provider value={game}>
        <EditBoardControls editingBoard={true} setEditingBoard={setEditingBoard} />
      </GameContext.Provider>
    ))

    const saveChangesButton = screen.getByRole('button', { name: 'Save changes' })
    fireEvent.click(saveChangesButton)

    expect(setEditingBoard).toHaveBeenLastCalledWith(false)
    expect(newGame).not.toHaveBeenCalled()
  })

  it('should allow editing board and restoring default', () => {
    const { rerender } = render((
      <GameContext.Provider value={game}>
        <EditBoardControls editingBoard={false} setEditingBoard={setEditingBoard} />
      </GameContext.Provider>
    ))

    const editBoardButton = screen.getByRole('button', { name: 'Edit board' })
    fireEvent.click(editBoardButton)
    expect(setEditingBoard).toHaveBeenLastCalledWith(true)
    expect(newGame).not.toHaveBeenCalled()

    rerender((
      <GameContext.Provider value={game}>
        <EditBoardControls editingBoard={true} setEditingBoard={setEditingBoard} />
      </GameContext.Provider>
    ))

    const restoreDefaultButton = screen.queryByRole('button', { name: 'Restore default' })
    fireEvent.click(restoreDefaultButton)

    expect(setEditingBoard).toHaveBeenLastCalledWith(false)
    expect(newGame).toHaveBeenCalled()
  })
})
