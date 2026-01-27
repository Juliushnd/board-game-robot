import { useReducer, useEffect, useRef, useCallback, useState } from 'react'
import { GameContext } from '../../GameContext.jsx'
import ConnectingModal from '../connecting-modal/ConnectingModal.jsx'
import ErrorModal from '../error-modal/ErrorModal.jsx'

const apiUrl = import.meta.env.VITE_BACKEND_API_URL ?? 'http://localhost:8000'
const wsUrl = import.meta.env.VITE_BACKEND_WS_URL ?? 'ws://localhost:8000/ws'

/**
 * The initial game state.
 *
 * @type {GameState}
 */
const initialState = {
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

/**
 * Game state reducer function. Merges `currentState` and `newState` and returns the result.
 *
 * @param {GameState} currentState Current game state.
 * @param {*} newState New game state. May be partial.
 * @returns {GameState} Resulting merged game state.
 */
const gameReducer = (currentState, newState) => {
  return Object.assign({}, currentState, newState)
}

/**
 * Handles connection to the backend and provides `GameContext` to its children.
 *
 * This component attempts to open a WebSocket connection to the backend on mount and listens to state updates from the
 * backend on that socket. A popup is displayed while the connection is being established.
 *
 * When a consumer of the `GameContext` request a change to the game state by calling one of the context's methods, this
 * component sends an HTTP request to the backend API describing the change. If the request succeeds, the backend pushes
 * a state update via the WebSocket which is then applied to the frontend game state. If the request fails, the frontend
 * displays an error message and refreshes its game state via a GET request to the backend API.
 *
 * @param {JSX.Element} children Child components.
 * @returns {JSX.Element}
 * @component
 */
export const GameProvider = ({ children }) => {
  /** @type {[GameState, React.Dispatch<GameState>]} */
  const [state, dispatch] = useReducer(gameReducer, initialState)
  const [connecting, setConnecting] = useState(true)
  const socket = useRef(null)
  const reconnectTimeout = useRef(null)

  // Connect to WebSocket and set up event handlers.
  const connectWebSocket = useCallback(() => {
    if (socket.current) {
      socket.current.onerror = null
      socket.current.onmessage = null
      socket.current.onclose = null
      socket.current.close()
    }
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current)
      reconnectTimeout.current = null
    }
    console.log('Connecting to WebSocket...')
    socket.current = new WebSocket(wsUrl)

    socket.current.onopen = () => {
      console.log('WebSocket connected')
    }

    socket.current.onmessage = (event) => {
      const message = JSON.parse(event.data)
      console.log('Received state', message)
      setConnecting(false)
      dispatch(message)
    }

    socket.current.onclose = (event) => {
      console.log('WebSocket disconnected', event)
      setConnecting(true)
      if (!reconnectTimeout.current) {
        reconnectTimeout.current = setTimeout(() => {
          connectWebSocket()
        }, 1000)
      }
    }

    socket.current.onerror = (error) => {
      console.error('WebSocket error:', error)
      setConnecting(true)
      if (!reconnectTimeout.current) {
        reconnectTimeout.current = setTimeout(() => {
          connectWebSocket()
        }, 1000)
      }
    }
  }, [])

  const makeApiRequest = async (url, method = 'GET', payload = {}, reloadStateOnError = true) => {
    const headers = { Accept: 'application/json' }
    let body = undefined
    if (method !== 'GET') {
      headers['Content-Type'] = 'application/json'
      body = JSON.stringify(payload)
    }
    const response = await fetch(apiUrl + url, {
      headers: headers,
      method: method,
      body: body,
    })
    if (response.ok) {
      return await response.json()
    }
    let json = null
    try {
      json = await response.json()
    } catch {
      // Nop.
    }
    let error
    if (json && json.detail) {
      error = json.detail
    } else {
      error = `Backend error: ${response.status} (${method} ${url})`
    }
    console.error(error)
    if (json || response.status >= 500) {
      alert(error)
    }
    if (reloadStateOnError) {
      // Reload game state.
      await getGame()
    }
  }

  const getGame = async () => {
    const state = await makeApiRequest('/game', 'GET', null, false)
    dispatch(state)
  }

  /** @type newGame */
  const newGame = async () => {
    await makeApiRequest('/game', 'DELETE')
  }

  /** @type setInitialPosition */
  const setInitialPosition = async (initialPosition) => {
    await makeApiRequest('/game', 'PATCH', {
      initialPosition: initialPosition,
    })
  }

  /** @type setHumanPlayerColor */
  const setHumanPlayerColor = async (color) => {
    await makeApiRequest('/game', 'PATCH', {
      humanPlayerColor: color,
    })
  }

  /** @type setAgent */
  const setAgent = async (agent) => {
    await makeApiRequest('/game', 'PATCH', {
      agent: agent,
    })
  }

  /** @type startGame */
  const startGame = async () => {
    await makeApiRequest('/game', 'PATCH', {
      gameStarted: true,
      gamePaused: false,
    })
  }

  /** @type pauseGame */
  const pauseGame = async () => {
    await makeApiRequest('/game', 'PATCH', {
      gamePaused: true,
    })
  }

  /** @type setHistory */
  const setHistory = async (history) => {
    await makeApiRequest('/game/history', 'PUT', history)
  }

  /** @type makeMove */
  const makeMove = async ({ color, from, to, promotion = undefined }) => {
    await makeApiRequest('/game/history', 'POST', {
      color: color,
      from: from,
      to: to,
      promotion: promotion,
    })
  }

  /** @type endGame */
  const endGame = async () => {
    await makeApiRequest('/game', 'PATCH', {
      gameOver: true,
    })
  }

  /** @type clearError */
  const clearError = async () => {
    await makeApiRequest('/game', 'PATCH', {
      error: null,
    })
  }

  // Connect WebSocket on component mount.
  useEffect(() => {
    connectWebSocket()

    // Clean up on unmount.
    return () => {
      if (socket.current) {
        socket.current.close()
        socket.current = null
      }
    }
  }, [connectWebSocket])

  /** @type {Game} */
  const game = Object.assign({}, state, {
    newGame,
    setInitialPosition,
    setHumanPlayerColor,
    setAgent,
    startGame,
    pauseGame,
    setHistory,
    makeMove,
    endGame,
    clearError,
  })

  return (
    <GameContext.Provider value={game}>
      {children}
      <ConnectingModal show={connecting} />
      <ErrorModal />
    </GameContext.Provider>
  )
}
