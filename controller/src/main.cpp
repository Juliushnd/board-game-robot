#include <iostream>
#include <string>

#include "chess_robot_controller.h"
#include "hough_board_detection.h"

// Main entrypoint of the controller application.
// Starts the controller main loop and handles CLI commands.
int main(int argc, char **argv) {
  // Parse program arguments.
  std::string backendHost = "127.0.0.1";
  int backendPort = 3000;
  if (argc > 1) {
    backendHost = argv[1];
  }
  if (argc > 2) {
    try {
      backendPort = std::stoi(argv[2]);
    } catch (std::exception &e) {
      std::cerr << "Invalid port number: \"" << argv[2] << "\"\n";
      exit(1);
    }
  }
  std::cout << "Starting controller for backend at " << backendHost << " port "
            << backendPort << "...\n";

  // Initialize subcomponents.
  auto backendClient = TCPClient(backendHost, backendPort);
  auto camera = ChessRobotCamera();
  auto boardDetection = HoughBoardDetection();
  auto moveManager = MoveManager();
  auto endOfTurnButton = Button("gpiochip0", 24);

  // Initialize main class.
  auto controller = ChessRobotController(backendClient, camera, boardDetection,
                                         moveManager, endOfTurnButton);

  // Start controller main loop.
  controller.start();

  // Handle CLI commands.
  while (true) {
    std::string line;
    std::getline(std::cin, line);

    if (!line.empty()) {
      controller.handleCLICommand(line);
    }
  }
}
