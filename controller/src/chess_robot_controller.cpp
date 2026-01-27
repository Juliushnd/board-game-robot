#include "chess_robot_controller.h"

#include <fstream>
#include <iostream>
#include <string>

#include "move_manager.h"

constexpr int RECONNECTION_TIMEOUT_SECS = 3;
constexpr int BUTTON_POLLING_INTERVAL_MS = 5;

ChessRobotController::ChessRobotController(TCPClient &backendClient,
                                           ChessRobotCamera &camera,
                                           BoardDetection &boardDetection,
                                           MoveManager &moveManager,
                                           Button &endOfTurnButton)
    : backendClient(backendClient),
      camera(camera),
      boardDetection(boardDetection),
      moveManager(moveManager),
      moveManagerCLI(moveManager),
      endOfTurnButton(endOfTurnButton),
      running(false),
      connected(false),
      isButtonPressed(false) {}

ChessRobotController::~ChessRobotController() { stop(); }

void ChessRobotController::start() {
  if (running) return;
  moveManager.setUp();
  camera.start();
  endOfTurnButton.init();
  running = true;

  // Start threads.
  backendThread =
      std::thread(&ChessRobotController::handleBackendMessages, this);
  buttonThread =
      std::thread(&ChessRobotController::handleEndOfTurnButton, this);
}

void ChessRobotController::stop() {
  if (!running) return;
  camera.stop();
  running = false;

  disconnectFromBackend();

  // Wait for threads to finish.
  backendThread.join();
  buttonThread.join();
}

bool ChessRobotController::isRunning() const { return running; }

bool ChessRobotController::isConnected() const { return connected; }

void ChessRobotController::handleCLICommand(const std::string &line) {
  std::string command, args;
  splitCommandArgs(line, command, args);

  if (command == "quit") {
    exit(0);

  } else if (command == "turn") {
    handleHumanTurn();

  } else if (command == "mm") {
    const std::lock_guard lock(robotMutex);
    moveManagerCLI.handleCommand(args);

  } else if (command == "recv") {
    handleBackendMessage(args);

  } else if (command == "send") {
    sendBackendMessage(args);

  } else {
    std::cerr << "Unknown command: " << command << "\n";
  }
}

void ChessRobotController::connectToBackend() {
  if (connected || !running) return;
  std::cout << "Connecting to backend...\n";
  while (!backendClient.connectToServer()) {
    sleep(RECONNECTION_TIMEOUT_SECS);
  }
  connected = true;
  std::cout << "Backend connection established.\n";
}

void ChessRobotController::disconnectFromBackend() {
  if (!connected) return;
  backendClient.closeConnection();
  connected = false;
  std::cout << "Backend connection closed.\n";
}

void ChessRobotController::handleBackendMessages() {
  connectToBackend();

  while (running) {
    std::string message = backendClient.receiveMessage();
    if (message.empty()) {
      if (!running) break;
      std::cout << "Server closed the connection or error occurred.\n";
      // Reconnect backend.
      disconnectFromBackend();
      sleep(RECONNECTION_TIMEOUT_SECS);
      connectToBackend();
      continue;
    }
    std::cout << "Backend message: " << message << "\n";

    handleBackendMessage(message);
  }

  disconnectFromBackend();
}

void ChessRobotController::handleBackendMessage(const std::string &message) {
  std::string command, args;
  splitCommandArgs(message, command, args);

  if (command == "ok" || command == "error") {
    // This is a response. Save it in the `response` variable and notify any
    // threads waiting for a response.
    {
      std::unique_lock<std::mutex> lk(responseMutex);
      response = message;
    }
    responseCondition.notify_all();

  } else if (handleBackendCommand(command, args)) {
    // Command handled successfully. Send "ok" response.
    backendClient.sendMessage("ok " + message);

  } else {
    // Could not handle command. Send "error" response.
    backendClient.sendMessage("error " + message);
  }
}

bool ChessRobotController::handleBackendCommand(const std::string &command,
                                                const std::string &args) {
  if (command == "move") {
    return handleMoveCommand(args);
  }
  std::cerr << "Unknown command: " << command << "\n";
  return false;
}

bool ChessRobotController::handleMoveCommand(const std::string &args) {
  if (args.length() < 4) {
    std::cerr << "Invalid argument for move command: " << args << "\n";
    return false;
  }

  // Parse the color specified in the move command so we know the orientation of
  // the board. Store move string without color in the `move` variable.
  std::string move;
  bool isWhite = true;
  const size_t idx = args.find(' ');
  if (idx != std::string::npos) {
    const std::string robotColor = args.substr(idx + 1);
    move = args.substr(0, idx);
    if (robotColor == "b") {
      isWhite = false;
    } else if (robotColor != "w") {
      std::cerr << "Invalid color in move command: " << robotColor << "\n";
      return false;
    }
  } else {
    move = args;
  }

  // Parse start square.
  const int x1 = move.c_str()[0] - 'a';
  const int y1 = move.c_str()[1] - '1';
  if (x1 < 0 || x1 > 7 || y1 < 0 || y1 > 7) {
    std::cerr << "Invalid starting position: " << move.substr(0, 2) << "\n";
    return false;
  }
  // Compute square index based on board orientation.
  Square startSq;
  if (isWhite) {
    startSq = x1 + 8 * y1;
  } else {
    startSq = (7 - x1) + 8 * (7 - y1);
  }

  // Parse end square.
  Square endSq;
  if (args.c_str()[2] == 'x') {
    // Move is a capture.
    endSq = -atoi(move.substr(3).c_str());
    if (endSq >= 0) {
      std::cerr << "Invalid capture position: " << move.substr(2) << "\n";
      return false;
    }
  } else {
    const int x2 = move.c_str()[2] - 'a';
    const int y2 = move.c_str()[3] - '1';
    if (x2 < 0 || x2 > 7 || y2 < 0 || y2 > 7) {
      std::cerr << "Invalid ending position: " << move.substr(2) << "\n";
      return false;
    }
    // Compute square index based on board orientation.
    if (isWhite) {
      endSq = x2 + 8 * y2;
    } else {
      endSq = (7 - x2) + 8 * (7 - y2);
    }
  }

  const std::lock_guard lock(robotMutex);

  std::cerr << "Moving piece from position " << startSq << " to position "
            << endSq << "...\n";
  moveManager.movePiece(startSq, endSq);
  return true;
}

void ChessRobotController::handleEndOfTurnButton() {
  while (running) {
    if (isEndOfTurnButtonPressed()) {
      // The human has pressed the end of turn button.
      // The following code will take some time, so we don't need to worry about
      // checking the button twice during a single press.
      handleHumanTurn();
    }
    usleep(BUTTON_POLLING_INTERVAL_MS * 1000);
  }
}

bool ChessRobotController::isEndOfTurnButtonPressed() {
  const std::lock_guard lock(robotMutex);

  return endOfTurnButton.isPressed();
}

bool ChessRobotController::handleHumanTurn() {
  const std::lock_guard lock(robotMutex);
  std::cout << "Handling human turn...\n";

#if(DEBUG)
  std::time_t t = std::time(nullptr);
  char date[32];
  strftime(date, sizeof(date), "%Y-%m-%d_%H-%M-%S", localtime(&t));

  std::string filename = "/tmp/images/board_" + std::string(date);
  std::cerr << "Writing debug files to " << filename << ".*...\n";
#endif

  std::cout << "Moving to camera position...\n";
  moveManager.moveToCamPos();

  // Wait for robot to settle.
  sleep(1);

  try {
    std::cout << "Capturing image of board...\n";
    auto image = camera.captureImage();

#if(DEBUG)
    cv::imwrite(filename + ".png", image);
    cv::FileStorage fs(filename + ".xml", cv::FileStorage::APPEND);
    fs << "img" << image;
    fs.release();
#endif

    std::cout << "Running board detection...\n";
    auto rawBoard = boardDetection.detectBoard(image);

    std::stringstream rawBoardStr;
    for (int i = 0; i < 8; ++i) {
      for (int j = 0; j < 8; ++j) {
        rawBoardStr << rawBoard[i][j] << " ";
      }
      rawBoardStr << "\n";
    }

    std::cout << "Detected raw board:\n";
    std::cout << rawBoardStr.str();

#if(DEBUG)
    std::ofstream out(filename + ".txt");
    out << rawBoardStr.str();
    out.close();
#endif

    std::cout << "Sending raw board to backend...\n";
    if (updateRawBoard(rawBoard)) {
      return true;
    }
    std::cerr << "Failed to update raw board.\n";
  } catch (std::exception &e) {
    std::cerr << "Error while handling human turn: " << e.what() << "\n";
  }

  std::cout << "Could not detect human turn. Use frontend or try again.\n";
  return false;
}

bool ChessRobotController::updateRawBoard(
    const std::array<std::array<char, 8>, 8> &rawBoard) {
  // Reshape raw board into a single line of characters terminated by null.
  char rawBoardStr[65];
  for (int i = 0; i < 64; i++) {
    rawBoardStr[i] = rawBoard.at(i / 8).at(i % 8);
  }
  rawBoardStr[64] = '\0';

  return sendBackendMessage("updateRawBoard " + std::string(rawBoardStr));
}

bool ChessRobotController::sendBackendMessage(const std::string &message) {
  std::unique_lock<std::mutex> lk(responseMutex);
  response = "";

  // Send the message.
  backendClient.sendMessage(message);

  // Wait for a response.
  responseCondition.wait(lk, [this] { return !response.empty(); });

  // Handle the response.
  if (response == "ok " + message) {
    return true;
  }
  if (response == "error " + message) {
    std::cerr << "Backend error.\n";
    return false;
  }
  std::cerr << "Unexpected backend response.\n";
  return false;
}

void ChessRobotController::splitCommandArgs(const std::string &line,
                                            std::string &command,
                                            std::string &args) {
  const size_t idx = line.find(' ');
  if (idx == std::string::npos) {
    command = line;
    args = "";
  } else {
    command = line.substr(0, idx);
    args = line.substr(idx + 1);
  }
}
