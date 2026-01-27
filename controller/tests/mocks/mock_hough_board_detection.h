#ifndef MOCK_HOUGH_BOARD_DETECTION_H
#define MOCK_HOUGH_BOARD_DETECTION_H

#include <gmock/gmock.h>

#include "../../src/hough_board_detection.h"

class MockBoardDetection : public HoughBoardDetection {
public:
  MOCK_METHOD((std::array<std::array<char, 8>, 8>), detectBoard,
              (const cv::Mat&), (override));
};

#endif  // MOCK_HOUGH_BOARD_DETECTION_H
