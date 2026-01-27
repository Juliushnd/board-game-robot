#ifndef BOARD_DETECTION_H_
#define BOARD_DETECTION_H_

#include <array>
#include <opencv2/core.hpp>

class BoardDetection {
 public:
    virtual ~BoardDetection() = default;
    virtual std::array<std::array<char, 8>, 8> detectBoard(
        const cv::Mat& image) = 0;
};

#endif  // BOARD_DETECTION_H_


