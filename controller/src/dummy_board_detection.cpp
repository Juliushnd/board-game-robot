#include "dummy_board_detection.h"
#include <iostream>

std::array<std::array<char, 8>, 8> DummyBoardDetection::detectBoard(
    const cv::Mat& image) {
    std::cout << "DummyBoardDetection: detectBoard called" << std::endl;
    std::array<std::array<char, 8>, 8> board{};
    for (auto& row : board) {
        row.fill('e');
    }
    return board;
}

