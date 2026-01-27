import { render, screen } from '@testing-library/react'
import { GameProvider } from './GameProvider.jsx'
import { describe, it, vi, beforeAll, afterAll, afterEach, expect } from 'vitest'
import { setupServer } from 'msw/node'
import { http, HttpResponse, ws } from 'msw'
import { useGame } from '../../GameContext.jsx'

describe('GameProvider', () => {
  let game = null
  const GameConsumer = function () {
    game = useGame()
    return <></>
  }

  // Keep track of most recently connected WebSocket client.
  let wsClient = null
  const onWsConnected = vi.fn(client => wsClient = client)

  const onRequest = vi.fn(() => HttpResponse.json({}))

  // Set up server mock.
  const chat = ws.link('ws://localhost:8000/ws')

  const wsHandlers = [
    chat.addEventListener('connection', ({ client }) => {
      onWsConnected(client)
    }),
  ]

  const restHandlers = [
    http.all('*', async ({ request }) => {
      return onRequest({
        method: request.method,
        url: request.url,
        body: request.method !== 'GET' ? await request.clone().json() : null,
      })
    }),
  ]

  const server = setupServer(...restHandlers, ...wsHandlers)

  beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))

  afterAll(() => server.close())

  afterEach(() => {
    server.resetHandlers()
    onWsConnected.mockReset()
    wsClient = null
    onRequest.mockReset()
  })

  it('should start a WebSocket connection on mount', async () => {
    render((
      <GameProvider />
    ))

    expect(screen.queryByText('Connecting to backend')).toBeInTheDocument()

    await vi.waitFor(() => expect(onWsConnected).toHaveBeenCalled())
    expect(wsClient).not.toBeNull()

    // Send initial state.
    wsClient.send(JSON.stringify({}))

    await vi.waitFor(() => expect(screen.queryByText('Connecting to backend')).not.toBeInTheDocument())

    expect(onRequest).not.toHaveBeenCalled()
  })

  it('should try reconnecting when the WebSocket connection fails', async () => {
    onWsConnected.mockImplementation(client => client.close())

    render((
      <GameProvider />
    ))

    // Wait for two unsuccessful connection attempts.
    await vi.waitFor(() => expect(onWsConnected).toHaveBeenCalled())
    expect(wsClient).toBeNull()

    onWsConnected.mockClear() // Reset mock calls.

    await vi.waitFor(() => expect(onWsConnected).toHaveBeenCalled(), { timeout: 2000 })
    expect(wsClient).toBeNull()

    onWsConnected.mockReset() // Reset mock implementation to default.

    // Wait for successful connection attempt.
    await vi.waitFor(() => expect(onWsConnected).toHaveBeenCalled(), { timeout: 2000 })
    expect(wsClient).not.toBeNull()

    expect(onRequest).not.toHaveBeenCalled()
  })

  it('should apply updates sent over the WebSocket to the game state', async () => {
    render((
      <GameProvider>
        <GameConsumer />
      </GameProvider>
    ))

    const expectedState = {
      initialPosition: null,
      currentPosition: null,
      currentPlayerColor: 'w',
      humanPlayerColor: 'w',
      availableAgents: [],
      agent: null,
      history: [],
      gameStarted: false,
      gamePaused: false,
      gameOver: false,
      isDraw: false,
      isCheckmate: false,
      error: null,
    }
    expect(game).toStrictEqual({ ...game, ...expectedState }) // We only compare fields defined above, not functions.

    await vi.waitFor(() => expect(onWsConnected).toHaveBeenCalled())
    expect(wsClient).not.toBeNull()

    // Send state changes.
    const changes = {
      initialPosition: 'foo',
      currentPosition: 'bar',
      currentPlayerColor: 'b',
      humanPlayerColor: 'b',
      availableAgents: [{ key: 'test', name: 'Test' }],
      agent: 'test',
      history: [{ san: 'aaa' }],
      gameStarted: true,
      gamePaused: true,
      gameOver: true,
      isDraw: true,
      isCheckmate: true,
      error: 'error',
    }
    wsClient.send(JSON.stringify(changes))

    await vi.waitFor(() => expect(game).toStrictEqual({ ...game, ...changes }))

    expect(onRequest).not.toHaveBeenCalled()
  })

  it('should allow starting a new game', async () => {
    render((
      <GameProvider>
        <GameConsumer />
      </GameProvider>
    ))

    await vi.waitFor(() => expect(game).not.toBeNull())

    await game.newGame()

    expect(onRequest).toHaveBeenCalledTimes(1)
    expect(onRequest).toHaveBeenCalledWith({
      method: 'DELETE',
      url: 'http://localhost:8000/game',
      body: {},
    })
  })

  it('should allow setting the initial position', async () => {
    render((
      <GameProvider>
        <GameConsumer />
      </GameProvider>
    ))

    await vi.waitFor(() => expect(game).not.toBeNull())

    await game.setInitialPosition({ a1: 'wP', b2: 'bP' })

    expect(onRequest).toHaveBeenCalledTimes(1)
    expect(onRequest).toHaveBeenCalledWith({
      method: 'PATCH',
      url: 'http://localhost:8000/game',
      body: {
        initialPosition: { a1: 'wP', b2: 'bP' },
      },
    })
  })

  it('should allow setting the human player color', async () => {
    render((
      <GameProvider>
        <GameConsumer />
      </GameProvider>
    ))

    await vi.waitFor(() => expect(game).not.toBeNull())

    await game.setHumanPlayerColor('b')

    expect(onRequest).toHaveBeenCalledTimes(1)
    expect(onRequest).toHaveBeenCalledWith({
      method: 'PATCH',
      url: 'http://localhost:8000/game',
      body: {
        humanPlayerColor: 'b',
      },
    })
  })

  it('should allow setting the agent', async () => {
    render((
      <GameProvider>
        <GameConsumer />
      </GameProvider>
    ))

    await vi.waitFor(() => expect(game).not.toBeNull())

    await game.setAgent('random')

    expect(onRequest).toHaveBeenCalledTimes(1)
    expect(onRequest).toHaveBeenCalledWith({
      method: 'PATCH',
      url: 'http://localhost:8000/game',
      body: {
        agent: 'random',
      },
    })
  })

  it('should allow starting the game', async () => {
    render((
      <GameProvider>
        <GameConsumer />
      </GameProvider>
    ))

    await vi.waitFor(() => expect(game).not.toBeNull())

    await game.startGame()

    expect(onRequest).toHaveBeenCalledTimes(1)
    expect(onRequest).toHaveBeenCalledWith({
      method: 'PATCH',
      url: 'http://localhost:8000/game',
      body: {
        gameStarted: true,
        gamePaused: false,
      },
    })
  })

  it('should allow pausing the game', async () => {
    render((
      <GameProvider>
        <GameConsumer />
      </GameProvider>
    ))

    await vi.waitFor(() => expect(game).not.toBeNull())

    await game.pauseGame()

    expect(onRequest).toHaveBeenCalledTimes(1)
    expect(onRequest).toHaveBeenCalledWith({
      method: 'PATCH',
      url: 'http://localhost:8000/game',
      body: {
        gamePaused: true,
      },
    })
  })

  it('should allow setting the history', async () => {
    render((
      <GameProvider>
        <GameConsumer />
      </GameProvider>
    ))

    await vi.waitFor(() => expect(game).not.toBeNull())

    await game.setHistory([{ san: 'foo' }, { san: 'bar' }])

    expect(onRequest).toHaveBeenCalledTimes(1)
    expect(onRequest).toHaveBeenCalledWith({
      method: 'PUT',
      url: 'http://localhost:8000/game/history',
      body: [{ san: 'foo' }, { san: 'bar' }],
    })
  })

  it('should allow making a move', async () => {
    render((
      <GameProvider>
        <GameConsumer />
      </GameProvider>
    ))

    await vi.waitFor(() => expect(game).not.toBeNull())

    await game.makeMove({ color: 'w', from: 'a1', to: 'b2', promotion: 'q' })

    expect(onRequest).toHaveBeenCalledTimes(1)
    expect(onRequest).toHaveBeenCalledWith({
      method: 'POST',
      url: 'http://localhost:8000/game/history',
      body: { color: 'w', from: 'a1', to: 'b2', promotion: 'q' },
    })

    onRequest.mockClear()

    await game.makeMove({ color: 'b', from: 'h8', to: 'f4' })

    expect(onRequest).toHaveBeenCalledTimes(1)
    expect(onRequest).toHaveBeenCalledWith({
      method: 'POST',
      url: 'http://localhost:8000/game/history',
      body: { color: 'b', from: 'h8', to: 'f4' },
    })
  })

  it('should allow ending the game', async () => {
    render((
      <GameProvider>
        <GameConsumer />
      </GameProvider>
    ))

    await vi.waitFor(() => expect(game).not.toBeNull())

    await game.endGame()

    expect(onRequest).toHaveBeenCalledTimes(1)
    expect(onRequest).toHaveBeenCalledWith({
      method: 'PATCH',
      url: 'http://localhost:8000/game',
      body: {
        gameOver: true,
      },
    })
  })

  it('should allow clearing the current error', async () => {
    render((
      <GameProvider>
        <GameConsumer />
      </GameProvider>
    ))

    await vi.waitFor(() => expect(onWsConnected).toHaveBeenCalled())
    expect(wsClient).not.toBeNull()

    // Send error.
    wsClient.send(JSON.stringify({ error: 'error' }))

    await vi.waitFor(() => expect(game.error).toBe('error'))

    await game.clearError()

    expect(onRequest).toHaveBeenCalledTimes(1)
    expect(onRequest).toHaveBeenCalledWith({
      method: 'PATCH',
      url: 'http://localhost:8000/game',
      body: {
        error: null,
      },
    })
  })

  it('should handle server errors by updating the state', async () => {
    render((
      <GameProvider>
        <GameConsumer />
      </GameProvider>
    ))

    await vi.waitFor(() => expect(game).not.toBeNull())

    const newState = {
      initialPosition: 'foo',
      currentPosition: 'bar',
      currentPlayerColor: 'b',
      humanPlayerColor: 'b',
      availableAgents: [{ key: 'test', name: 'Test' }],
      agent: 'test',
      history: [{ san: 'aaa' }],
      gameStarted: true,
      gamePaused: true,
      gameOver: true,
      isDraw: true,
      isCheckmate: true,
    }
    onRequest
      .mockImplementationOnce(() => HttpResponse.json({ detail: 'Human-friendly server error' }, { status: 500 }))
      .mockImplementationOnce(() => HttpResponse.json(newState))

    await game.startGame()

    expect(onRequest).toHaveBeenCalledTimes(2)
    expect(onRequest).toHaveBeenNthCalledWith(1, {
      method: 'PATCH',
      url: 'http://localhost:8000/game',
      body: {
        gameStarted: true,
        gamePaused: false,
      },
    })
    expect(onRequest).toHaveBeenNthCalledWith(2, {
      method: 'GET',
      url: 'http://localhost:8000/game',
      body: null,
    })

    await vi.waitFor(() => expect(game).toStrictEqual({ ...game, ...newState }))
  })

  it('should handle client errors by updating the state', async () => {
    render((
      <GameProvider>
        <GameConsumer />
      </GameProvider>
    ))

    await vi.waitFor(() => expect(game).not.toBeNull())

    const newState = {
      initialPosition: 'foo',
      currentPosition: 'bar',
      currentPlayerColor: 'b',
      humanPlayerColor: 'b',
      availableAgents: [{ key: 'test', name: 'Test' }],
      agent: 'test',
      history: [{ san: 'aaa' }],
      gameStarted: true,
      gamePaused: true,
      gameOver: true,
      isDraw: true,
      isCheckmate: true,
    }
    onRequest
      .mockImplementationOnce(() => HttpResponse.text('Not authorized', { status: 401 }))
      .mockImplementationOnce(() => HttpResponse.json(newState))

    await game.startGame()

    expect(onRequest).toHaveBeenCalledTimes(2)
    expect(onRequest).toHaveBeenNthCalledWith(1, {
      method: 'PATCH',
      url: 'http://localhost:8000/game',
      body: {
        gameStarted: true,
        gamePaused: false,
      },
    })
    expect(onRequest).toHaveBeenNthCalledWith(2, {
      method: 'GET',
      url: 'http://localhost:8000/game',
      body: null,
    })

    await vi.waitFor(() => expect(game).toStrictEqual({ ...game, ...newState }))
  })
})
