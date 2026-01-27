import { fireEvent, render, screen, within } from '@testing-library/react'
import GameInfo from './GameInfo.jsx'
import { GameContext } from '../../GameContext.jsx'
import { describe, it, vi, beforeEach, expect } from 'vitest'

describe('GameInfo', () => {
  const setHistory = vi.fn()

  let game
  beforeEach(() => {
    game = {
      setHistory,
      gameStarted: false,
      gameOver: false,
      isCheckmate: false,
      isDraw: false,
      currentPlayerColor: 'w',
      history: [],
    }
    setHistory.mockReset()
  })

  it('should show the game history', () => {
    const { rerender } = render((
      <GameContext.Provider value={game}>
        <GameInfo />
      </GameContext.Provider>
    ))

    let rows = screen.queryAllByRole('row')
    expect(rows).toHaveLength(0)

    game = {
      ...game,
      history: [{ san: 'foo' }],
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameInfo />
      </GameContext.Provider>
    ))

    rows = screen.queryAllByRole('row')
    expect(rows).toHaveLength(1)

    let cells = within(rows[0]).getAllByRole('cell')
    expect(cells).toHaveLength(3)
    expect(cells[0]).toHaveTextContent(/^1.$/)
    expect(cells[1]).toHaveTextContent(/^foo$/)
    expect(cells[2]).toHaveTextContent(/^$/)

    game = {
      ...game,
      history: [{ san: 'a' }, { san: 'b' }, { san: 'c' }, { san: 'd' }, { san: 'e' }, { san: 'f' }],
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameInfo />
      </GameContext.Provider>
    ))

    rows = screen.queryAllByRole('row')
    expect(rows).toHaveLength(3)

    cells = within(rows[0]).getAllByRole('cell')
    expect(cells).toHaveLength(3)
    expect(cells[0]).toHaveTextContent(/^1.$/)
    expect(cells[1]).toHaveTextContent(/^a$/)
    expect(cells[2]).toHaveTextContent(/^b$/)

    cells = within(rows[1]).getAllByRole('cell')
    expect(cells).toHaveLength(3)
    expect(cells[0]).toHaveTextContent(/^2.$/)
    expect(cells[1]).toHaveTextContent(/^c$/)
    expect(cells[2]).toHaveTextContent(/^d$/)

    cells = within(rows[2]).getAllByRole('cell')
    expect(cells).toHaveLength(3)
    expect(cells[0]).toHaveTextContent(/^3.$/)
    expect(cells[1]).toHaveTextContent(/^e$/)
    expect(cells[2]).toHaveTextContent(/^f$/)
  })

  it('should show the game status', () => {
    const { rerender } = render((
      <GameContext.Provider value={game}>
        <GameInfo />
      </GameContext.Provider>
    ))

    expect(screen.getByText('Game not running')).toBeInTheDocument()

    game = {
      ...game,
      gameStarted: true,
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameInfo />
      </GameContext.Provider>
    ))

    expect(screen.getByText('White to move')).toBeInTheDocument()

    game = {
      ...game,
      currentPlayerColor: 'b',
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameInfo />
      </GameContext.Provider>
    ))

    expect(screen.getByText('Black to move')).toBeInTheDocument()

    game = {
      ...game,
      gameOver: true,
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameInfo />
      </GameContext.Provider>
    ))

    expect(screen.getByText('Game over')).toBeInTheDocument()

    game = {
      ...game,
      isDraw: true,
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameInfo />
      </GameContext.Provider>
    ))

    expect(screen.getByText('Game over (draw)')).toBeInTheDocument()

    game = {
      ...game,
      isDraw: false,
      isCheckmate: true,
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameInfo />
      </GameContext.Provider>
    ))

    expect(screen.getByText('Game over (white won)')).toBeInTheDocument()

    game = {
      ...game,
      currentPlayerColor: 'w',
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameInfo />
      </GameContext.Provider>
    ))

    expect(screen.getByText('Game over (black won)')).toBeInTheDocument()
  })

  it('should allow undoing the last move if enabled', () => {
    game = {
      ...game,
      history: [{ san: 'foo' }, { san: 'bar' }],
    }

    const { rerender } = render((
      <GameContext.Provider value={game}>
        <GameInfo allowUndo={true} />
      </GameContext.Provider>
    ))

    let button = screen.getByRole('button', { name: 'Undo last move' })
    fireEvent.click(button)

    expect(setHistory).toHaveBeenLastCalledWith([{ san: 'foo' }])

    // Test with empty history.
    game = {
      ...game,
      history: [],
    }

    rerender((
      <GameContext.Provider value={game}>
        <GameInfo allowUndo={true} />
      </GameContext.Provider>
    ))

    button = screen.getByRole('button', { name: 'Undo last move' })
    fireEvent.click(button)

    expect(setHistory).toHaveBeenLastCalledWith([])
  })
})
