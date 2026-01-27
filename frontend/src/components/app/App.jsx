import { useEffect, useState } from 'react'
import { faRobot, faUser } from '@fortawesome/free-solid-svg-icons'
import { ChessboardDnDProvider } from 'react-chessboard'
import { useGame } from '../../GameContext.jsx'
import PlayerCard from '../player-card/PlayerCard.jsx'
import EditAgentButton from '../edit-agent-button/EditAgentButton.jsx'
import EditBoardControls from '../edit-board-controls/EditBoardControls.jsx'
import EditMovesControls from '../edit-moves-controls/EditMovesControls.jsx'
import Board from '../board/Board.jsx'
import FlipBoardButton from '../flip-board-button/FlipBoardButton.jsx'
import BoardEditor from '../board-editor/BoardEditor.jsx'
import GameInfo from '../game-info/GameInfo.jsx'
import GameControls from '../game-controls/GameControls.jsx'
import GameOverModal from '../game-over-modal/GameOverModal.jsx'
import './App.css'

/**
 * Main frontend UI. Needs to be placed inside a `GameProvider` component.
 *
 * @returns {JSX.Element}
 * @component
 */
export default function App() {
  const game = useGame()

  const [editingBoard, setEditingBoard] = useState(false)
  const [editingMoves, setEditingMoves] = useState(false)

  useEffect(() => {
    if (game.gameStarted) {
      setEditingBoard(false)
    } else {
      setEditingMoves(false)
    }
  }, [game.gameStarted])

  const boardId = 'board'

  return (
    <ChessboardDnDProvider>
      <div className="app-wrapper">
        <div className="app">
          <div className="app-header">
            <div className="app-header-left">
              <PlayerCard name="Robot" icon={faRobot} />
              <div className="align-right-on-break">
                <EditAgentButton />
              </div>
            </div>
            <div className="app-header-right">
              <div className="buttons">
                {!game.gameStarted && (
                  <EditBoardControls
                    editingBoard={editingBoard}
                    setEditingBoard={setEditingBoard}
                  />
                )}
                {game.gameStarted && (
                  <EditMovesControls
                    editingMoves={editingMoves}
                    setEditingMoves={setEditingMoves}
                  />
                )}
              </div>
            </div>
          </div>
          <div className="app-body">
            <div className="panels">
              <div className="left-panel">
                <div className="left-container">
                  <Board id={boardId} editingBoard={editingBoard} editingMoves={editingMoves} />
                </div>
                <div className="panel-footer">
                  <div className="bottom-row-left">
                    <PlayerCard name="Human" icon={faUser} />
                  </div>
                  <div className="panel-footer-right">
                    {!game.gameStarted && <FlipBoardButton />}
                  </div>
                </div>
              </div>
              <div className="right-panel">
                <div className="right-container">
                  {editingBoard && <BoardEditor dndId={boardId} />}
                  {!editingBoard && <GameInfo allowUndo={editingMoves && game.history.length > 0} />}
                </div>
                <div className="panel-footer">
                  <div className="panel-footer-right buttons">
                    <GameControls disabled={editingBoard || editingMoves} />
                    <GameOverModal />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ChessboardDnDProvider>
  )
}
