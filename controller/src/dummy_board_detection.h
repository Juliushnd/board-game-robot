#ifndef DUMMY_BOARD_DETECTION_H_
#define DUMMY_BOARD_DETECTION_H_

#include <array>
#include <opencv2/core.hpp>

#include "board_detection.h"

class DummyBoardDetection : public BoardDetection {
 public:
    DummyBoardDetection() = default;
    ~DummyBoardDetection() override = default;

    std::array<std::array<char, 8>, 8> detectBoard(
        const cv::Mat& image) override;
};

#endif  // DUMMY_BOARD_DETECTION_H_


