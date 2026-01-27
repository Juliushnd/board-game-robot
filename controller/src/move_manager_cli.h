
#include "move_manager.h"
#include <string>

#ifndef MOVE_MANAGER_CLI_H_
#define MOVE_MANAGER_CLI_H_

class MoveManagerCLI {
 public:
  explicit MoveManagerCLI(MoveManager& Manager);

  ~MoveManagerCLI() = default;

  void handleCommand(const std::string& command) const;

 protected:
  MoveManager& manager;
};

#endif  // MOVE_MANAGER_CLI_H_
