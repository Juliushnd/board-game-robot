#ifndef MOCK_MOVE_MANAGER_H
#define MOCK_MOVE_MANAGER_H

#include <gmock/gmock.h>

#include "../../src/move_manager.h"

class MockMoveManager : public MoveManager {
 public:
  MOCK_METHOD(void, setUp, (), (override));
  MOCK_METHOD(bool, movePiece, (Square, Square), (override));
  MOCK_METHOD(void, moveToCamPos, (), (override));
};

#endif  // MOCK_MOVE_MANAGER_H
