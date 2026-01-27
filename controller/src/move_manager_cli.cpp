
#include "move_manager_cli.h"

#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

using std::string, std::array;

MoveManagerCLI::MoveManagerCLI(MoveManager& Manager) : manager(Manager) {}

void MoveManagerCLI::handleCommand(const string& command) const {
  std::istringstream iss(command);
  std::vector<std::string> args;
  string token;

  while (iss >> token) {
    args.push_back(token);
  }

  if (args.size() == 0) return;

  if (args[0] == "pos" && args.size() == 3) {
    manager.moveToPosition(std::stoi(args[1]), args[2]);
  } else if (args[0] == "move" && args.size() == 3) {
    manager.movePiece(std::stoi(args[1]), std::stoi(args[2]));
  } else if (args[0] == "setzero" && args.size() == 1) {
    manager.setZeroPositionAll();
  } else if (args[0] == "drop" && args.size() == 1) {
    manager.dropPiece(false);
  } else if (args[0] == "dropo" && args.size() == 1) {
    manager.dropPiece(true);
  } else if (args[0] == "grab" && args.size() == 1) {
    manager.grabPiece(false);
  } else if (args[0] == "test" && args.size() == 1) {
    manager.test();
  } else if (args[0] == "start" && args.size() == 1) {
    manager.moveToStartPosition();
  } else {
    std::cout << "command not found" << std::endl;
  }
}
