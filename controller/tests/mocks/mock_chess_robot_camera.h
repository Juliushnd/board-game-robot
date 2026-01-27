#ifndef MOCK_CHESS_ROBOT_CAMERA_H
#define MOCK_CHESS_ROBOT_CAMERA_H

#include <gmock/gmock.h>

#include "../../src/chess_robot_camera.h"

class MockChessRobotCamera : public ChessRobotCamera {
 public:
  MOCK_METHOD(void, start, (), (override));
  MOCK_METHOD(void, stop, (), (override));
  MOCK_METHOD(cv::Mat, captureImage, (), (override));
};

#endif  // MOCK_CHESS_ROBOT_CAMERA_H
