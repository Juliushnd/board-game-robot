#ifndef MOCK_BOARD_DETECTION_H
#define MOCK_BOARD_DETECTION_H

#include <gmock/gmock.h>

#include "../../src/board_detection.h"

class MockBoardDetection : public BoardDetection {
 public:
  MOCK_METHOD((std::array<std::array<char, 8>, 8>), detectBoard,
              (const cv::Mat&), (override));
};

#endif  // MOCK_BOARD_DETECTION_H
