import { createContext, useContext } from 'react'

/**
 * This file contains some JSDoc typedefs and exports `GameContext` and the `useGame()` function.
 */

/**
 * A game context.
 *
 * @type {React.Context<Game|null>}
 */
export const GameContext = createContext(null)

/**
 * Get the `GameContext` provided by a `GameProvider` component further up in the DOM hierarchy.
 *
 * @returns {Game|null}
 */
export const useGame = () => {
  const context = useContext(GameContext)
  if (!context) {
    throw new Error('useGame must be used within a GameProvider')
  }
  return context
}

/**
 * A chess position.
 *
 * @typedef {Object} Position
 */

/**
 * A chess piece color.
 *
 * @typedef {"w"|"b"} Color
 */

/**
 * A chess agent.
 *
 * @typedef {Object} Agent
 * @property {String} key
 * @property {String} name
 * @property {Boolean} allowFrontendMoves
 */

/**
 * A chess move.
 *
 * @typedef {Object} Move
 * @property {String|undefined} color
 * @property {String} from
 * @property {String} to
 * @property {String|null} promotion
 * @property {String|undefined} san
 */

/**
 * Callback to reset the game.
 *
 * @callback newGame
 */

/**
 * Callback to set the initial position.
 *
 * @callback setInitialPosition
 * @param {Position} initialPosition
 */

/**
 * Callback to set the color which the human player will play as.
 *
 * @callback setHumanPlayerColor
 * @param {Color} color The new human player color.
 */

/**
 * Callback to set the active agent.
 *
 * @callback setAgent
 * @param {String} agent Key of the agent to activate.
 */

/**
 * Callback to start or resume the game.
 *
 * @callback startGame
 */

/**
 * Callback to pause the game.
 *
 * @callback pauseGame
 */

/**
 * Callback to override the move sequence.
 *
 * @callback setHistory
 * @param {Move[]} history The new history.
 */

/**
 * Callback to make a move.
 *
 * @callback makeMove
 * @param {Move} move The move to make.
 */

/**
 * Callback to end the game.
 *
 * @callback endGame
 */

/**
 * Callback to clear the current error.
 *
 * @callback clearError
 */

/**
 * A game state.
 *
 * @typedef {Object} GameState
 * @property {Position} initialPosition
 * @property {Position} currentPosition
 * @property {Color} currentPlayerColor
 * @property {Color} humanPlayerColor
 * @property {Agent[]} availableAgents
 * @property {String|null} agent
 * @property {Move[]} history
 * @property {Boolean} gameStarted
 * @property {Boolean} gamePaused
 * @property {Boolean} gameOver
 * @property {Boolean} isDraw
 * @property {Boolean} isCheckmate
 * @property {String|null} error
 */

/**
 * Game callbacks.
 *
 * @typedef {Object} GameCallbacks
 * @property {newGame} newGame
 * @property {setInitialPosition} setInitialPosition
 * @property {setHumanPlayerColor} setHumanPlayerColor
 * @property {setAgent} setAgent
 * @property {startGame} startGame
 * @property {pauseGame} pauseGame
 * @property {setHistory} setHistory
 * @property {makeMove} makeMove
 * @property {endGame} endGame
 * @property {clearError} clearError
 */

/**
 * A game.
 *
 * @typedef {GameState & GameCallbacks} Game
 */
