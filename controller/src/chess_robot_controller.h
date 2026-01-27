#ifndef CHESS_ROBOT_CONTROLLER_H_
#define CHESS_ROBOT_CONTROLLER_H_

#include <bits/std_thread.h>

#include <condition_variable>
#include <mutex>
#include <string>

#include "board_detection.h"
#include "chess_robot_camera.h"
#include "button.h"
#include "move_manager.h"
#include "move_manager_cli.h"
#include "tcp_client.h"

// Main class for the chess robot controller.
// Handles messages from the backend, CLI commands, and the end of turn button.
// All methods are thread safe.
class ChessRobotController {
 public:
  // Initialize a new ChessRobotController. All other objects which this class
  // uses are passed here already initialized with their respective options.
  // This is done to improve separation of concerns and ensure testability.
  // They should still be in their initial state, however, i.e., the
  // `backendClient` should not be connected to the backend and the
  // `moveManager` should not be set up, yet.
  ChessRobotController(TCPClient &backendClient, ChessRobotCamera &camera,
                       BoardDetection &boardDetection, MoveManager &moveManager,
                       Button &endOfTurnButton);

  ~ChessRobotController();

  // Start the controller main loop. This connects to the backend and handles
  // backend messages in one thread and polls the end of turn button in another.
  void start();

  // Stop the controller main loop. This shuts down the connection to the
  // backend and waits for all threads to exit gracefully.
  void stop();

  // Handle a command sent to the application via the Command Line Interface.
  void handleCLICommand(const std::string &line);

  // Return whether the controller main loop is currently running.
  [[nodiscard]] bool isRunning() const;

  // Return whether the controller is currently connected to the backend.
  [[nodiscard]] bool isConnected() const;

 private:
  TCPClient &backendClient;
  ChessRobotCamera &camera;
  BoardDetection &boardDetection;
  MoveManager &moveManager;
  MoveManagerCLI moveManagerCLI;
  Button &endOfTurnButton;

  bool running, connected;
  std::thread backendThread;
  std::thread buttonThread;
  std::mutex robotMutex;
  std::condition_variable responseCondition;
  std::mutex responseMutex;
  std::string response;
  bool isButtonPressed;

  void connectToBackend();

  void disconnectFromBackend();

  void handleBackendMessages();

  void handleBackendMessage(const std::string &message);

  bool handleBackendCommand(const std::string &command,
                            const std::string &args = "");

  bool handleMoveCommand(const std::string &args);

  void handleEndOfTurnButton();

  bool isEndOfTurnButtonPressed();

  bool handleHumanTurn();

  bool updateRawBoard(const std::array<std::array<char, 8>, 8> &rawBoard);

  bool sendBackendMessage(const std::string &message);

  // Splits a line of text into a `command` part and an `args` part on the first
  // space character. If there is no space character, `args` will be set to an
  // empty string.
  static void splitCommandArgs(const std::string &line, std::string &command,
                               std::string &args);
};

#endif  // CHESS_ROBOT_CONTROLLER_H_
