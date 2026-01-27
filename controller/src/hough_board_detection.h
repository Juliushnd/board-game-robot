#ifndef HOUGH_BOARD_DETECTION_H_
#define HOUGH_BOARD_DETECTION_H_

#include <vector>
#include <opencv2/opencv.hpp>

#include "board_detection.h"

class HoughBoardDetection : public BoardDetection{
 public:
  std::array<std::array<char, 8>, 8> detectBoard(
    const cv::Mat& image) override;

 private:
  std::vector<float> cluster_id(const std::vector<float>& values);
  std::vector<cv::Point2f> filter_to_9x9_hough_grid(
    const std::vector<cv::Point2f>& hough_points);
  std::vector<cv::Point2f> find_intersections(
    const std::vector<cv::Vec4i>& verticals,
    const std::vector<cv::Vec4i>& horizontals);
  std::vector<cv::Vec4i> filter_close_verticals(
    const std::vector<cv::Vec4i>& input, int min_dist);
  std::vector<cv::Vec4i> filter_close_horizontals(
    const std::vector<cv::Vec4i>& input, int min_dist);
  std::array<std::array<char, 8>, 8> classify_boardpieces(
    std::vector<std::vector<cv::Point2f>> grid_vector,
    const cv::Mat& board_image, const cv::Mat& board_gray);

  std::vector<cv::Vec4i> horizontals_;
  std::vector<cv::Vec4i> verticals_;
};
#endif  // HOUGH_BOARD_DETECTION_H_
