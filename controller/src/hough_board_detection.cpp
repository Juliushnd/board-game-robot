#include "hough_board_detection.h"

#include <unistd.h>
#include <sys/mman.h>

#include <chrono>
#include <thread>
#include <iostream>
#include <memory>
#include <vector>
#include <string>
#include <algorithm>
#include <cmath>
#include <limits>

#include <opencv2/opencv.hpp>

std::vector<float> HoughBoardDetection::cluster_id(
    const std::vector<float>& values) {
  cv::Mat data(values.size(), 1, CV_32F);
  for (int i = 0; i < values.size(); ++i) {
    data.at<float>(i, 0) = values[i];
  }

  cv::Mat labels, centers;
  cv::kmeans(data,
             9,
             labels,
             cv::TermCriteria(cv::TermCriteria::EPS |
                              cv::TermCriteria::COUNT,
                              100,
                              0.1),
             3,
             cv::KMEANS_PP_CENTERS,
             centers);

  std::vector<float> raw;
  for (int i = 0; i < centers.rows; ++i) {
    raw.push_back(centers.at<float>(i, 0));
  }

  std::sort(raw.begin(), raw.end());
  float totalSpan = raw.back() - raw.front();
  float idealStep = totalSpan / 8.0f;

  std::vector<float> result;
  for (int i = 0; i < 9; ++i) {
    result.push_back(raw.front() + i * idealStep);
  }
  return result;
}

std::vector<cv::Point2f> HoughBoardDetection::filter_to_9x9_hough_grid(
    const std::vector<cv::Point2f>& houghPoints) {
  std::vector<float> xs, ys;
  xs.reserve(houghPoints.size());
  ys.reserve(houghPoints.size());

  for (const auto& p : houghPoints) {
    xs.push_back(p.x);
    ys.push_back(p.y);
  }

  std::vector<float> xGrid = cluster_id(xs);
  std::vector<float> yGrid = cluster_id(ys);

  std::vector<cv::Point2f> result;
  result.reserve(81);

  for (float y : yGrid) {
    for (float x : xGrid) {
      cv::Point2f target(x, y);
      float bestDist = std::numeric_limits<float>::max();
      cv::Point2f bestPoint;

      for (const auto& hp : houghPoints) {
        float d = cv::norm(hp - target);
        if (d < bestDist) {
          bestDist = d;
          bestPoint = hp;
        }
      }
      result.push_back(bestPoint);
    }
  }
  return result;
}

std::vector<cv::Point2f> HoughBoardDetection::find_intersections(
    const std::vector<cv::Vec4i>& verticals,
    const std::vector<cv::Vec4i>& horizontals) {
  std::vector<cv::Point2f> houghPoints;

  for (const auto& h : horizontals) {
    cv::Point2f hp1(h[0], h[1]), hp2(h[2], h[3]);

    for (const auto& v : verticals) {
      cv::Point2f vp1(v[0], v[1]), vp2(v[2], v[3]);

      float A1 = hp2.y - hp1.y;
      float B1 = hp1.x - hp2.x;
      float C1 = A1 * hp1.x + B1 * hp1.y;

      float A2 = vp2.y - vp1.y;
      float B2 = vp1.x - vp2.x;
      float C2 = A2 * vp1.x + B2 * vp1.y;

      float det = A1 * B2 - A2 * B1;
      if (std::abs(det) < 1e-5f) continue;

      float x = (B2 * C1 - B1 * C2) / det;
      float y = (A1 * C2 - A2 * C1) / det;
      houghPoints.emplace_back(x, y);
    }
  }
  return houghPoints;
}

std::vector<cv::Vec4i> HoughBoardDetection::filter_close_verticals(
    const std::vector<cv::Vec4i>& input, int minDist) {
  std::vector<std::pair<int, cv::Vec4i>> sorted;
  sorted.reserve(input.size());

  for (const auto& l : input) {
    int mx = (l[0] + l[2]) / 2;
    sorted.emplace_back(mx, l);
  }

  std::sort(sorted.begin(),
            sorted.end(),
            [](const auto& a, const auto& b) { return a.first < b.first; });

  std::vector<cv::Vec4i> result;
  int lastX = -10000;
  for (const auto& [x, line] : sorted) {
    if (std::abs(x - lastX) >= minDist) {
      result.push_back(line);
      lastX = x;
    }
  }
  return result;
}

std::vector<cv::Vec4i> HoughBoardDetection::filter_close_horizontals(
    const std::vector<cv::Vec4i>& input, int minDist) {
  std::vector<std::pair<int, cv::Vec4i>> sorted;
  sorted.reserve(input.size());

  for (const auto& l : input) {
    int my = (l[1] + l[3]) / 2;
    sorted.emplace_back(my, l);
  }

  std::sort(sorted.begin(),
            sorted.end(),
            [](const auto& a, const auto& b) { return a.first < b.first; });

  std::vector<cv::Vec4i> result;
  int lastY = -10000;
  for (const auto& [y, line] : sorted) {
    if (std::abs(y - lastY) >= minDist) {
      result.push_back(line);
      lastY = y;
    }
  }
  return result;
}


std::array<std::array<char, 8>, 8> HoughBoardDetection::classify_boardpieces(
    std::vector<std::vector<cv::Point2f>> grid_vector,
    const cv::Mat& board_image, const cv::Mat& board_gray) {
  cv::Mat binary;
  int count = 0;
  cv::GaussianBlur(board_gray, board_gray, cv::Size(3, 3), 0.8);
  cv::Canny(board_gray, binary, 50, 150);
  std::array<std::array<char, 8>, 8> board_state;
  for (int y = 0; y < 8; ++y) {
    for (int x = 0; x < 8; ++x) {
      cv::Point2f p1 = grid_vector[y][x];
      cv::Point2f p2 = grid_vector[y][x + 1];
      cv::Point2f p3 = grid_vector[y + 1][x + 1];
      cv::Point2f p4 = grid_vector[y + 1][x];

      std::vector<cv::Point> square = {p1, p2, p3, p4};
      cv::Rect roi = cv::boundingRect(square);
      cv::Rect inner = roi;
      inner.x += roi.width * 0.3;
      inner.y += roi.height * 0.3;
      inner.width *= 0.4;
      inner.height *= 0.4;

      cv::Mat field = board_gray(inner);
      cv::Mat hsvImage;
      cv::cvtColor(board_image, hsvImage, cv::COLOR_BGR2HSV);
      cv::Mat fieldHSV = hsvImage(inner);

      cv::Scalar meanHSV, stddevHSV;
      cv::meanStdDev(fieldHSV, meanHSV, stddevHSV);

      cv::Scalar mean, stddev;
      cv::meanStdDev(field, mean, stddev);

      cv::Mat fieldFull = board_gray(roi);
      cv::Scalar meanFull, stddevFull;
      cv::meanStdDev(fieldFull, meanFull, stddevFull);

      cv::Mat hsvImageFull;
      cv::cvtColor(board_image, hsvImageFull, cv::COLOR_BGR2HSV);
      cv::Mat fieldHSVFull = hsvImageFull(roi);

      cv::Scalar meanHSVFull, stddevHSVFull;
      cv::meanStdDev(fieldHSVFull, meanHSVFull, stddevHSVFull);

      cv::Mat lap;
      cv::Laplacian(field, lap, CV_64F);
      cv::Scalar meanLap, stddevLap;
      cv::meanStdDev(lap, meanLap, stddevLap);
      double sharpness = stddevLap[0];
      cv::Mat binaryInner = binary(inner);
      std::vector<std::vector<cv::Point>> contours;
      cv::findContours(binaryInner, contours,
        cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
      int contourCount = contours.size();
      count = count + 1;
      char classification = 'e';
      double empty = 1.5*(contourCount < 2) + (contourCount < 1)
        - (sharpness/30) - 0.5*(meanHSV[1]/255) - (stddev[0]/7);
      double white = (10*(meanHSVFull[1]-meanHSV[1])/255)
        + (-10*(meanHSVFull[2]-meanHSV[2])/255);
      double black = (-10*(meanHSVFull[1]-meanHSV[1])/255)
        + (10*(meanHSVFull[2]-meanHSV[2])/255);
      float delta_s = (meanHSVFull[1] - meanHSV[1]) / (meanHSVFull[1]);
      float delta_v = (meanHSVFull[2] - meanHSV[2]) / (meanHSVFull[2]);
      float delta_l = (meanFull[0] - mean[0]) / (meanFull[0]);
      if (empty < 1 || (empty < white ||
        empty < (delta_s + 3*delta_v + delta_l))) {
        if (((delta_s + delta_v > 0.15)
          && delta_v > 0.03 && delta_l > 0.03)
          && (delta_s + 2*delta_v + delta_l > 0.6)
          || (delta_v + delta_l > 1) ) {
          classification = 'b';
        } else {
          classification = 'w';
        }
      }
      board_state[y][x] = classification;
    }
  }
  return board_state;
}

std::array<std::array<char, 8>, 8>
    HoughBoardDetection::detectBoard(const cv::Mat& img) {
  std::vector<uchar> buf;
  cv::Mat image = img.clone();
  cv::imencode(".jpg", image, buf, {cv::IMWRITE_JPEG_QUALITY, 90});
  image = cv::imdecode(buf, cv::IMREAD_COLOR);
  std::array<std::array<char, 8>, 8> result;
  cv::Mat gray;
  cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);
  cv::GaussianBlur(gray, gray, cv::Size(5, 5), 0.8);

  cv::Mat edges;
  cv::Canny(gray, edges, 20, 150);

  cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(3, 3));
  cv::dilate(edges, edges, kernel);
  cv::morphologyEx(edges, edges, cv::MORPH_CLOSE,
                   cv::getStructuringElement(cv::MORPH_RECT, cv::Size(2, 2)));

  std::vector<cv::Vec4i> linesP;
  cv::HoughLinesP(edges, linesP, 1, CV_PI / 180, 250, 70, 100);


  std::vector<cv::Vec4i> filteredLinesP;
  std::vector<std::vector<cv::Point>> contours;
  std::vector<cv::Vec4i> hierarchy;
  cv::findContours(edges, contours, hierarchy, cv::RETR_EXTERNAL,
                   cv::CHAIN_APPROX_SIMPLE);

  std::vector<cv::Point> bestApprox;
  double minDistanceToCenter = std::numeric_limits<double>::max();
  cv::Point2f imageCenter(image.cols / 2.0f, image.rows / 2.0f);

  for (const auto& contour : contours) {
    double area = cv::contourArea(contour);
    if (area < 100000) continue;

    double epsilon = 0.02 * cv::arcLength(contour, true);
    std::vector<cv::Point> approx;
    cv::approxPolyDP(contour, approx, epsilon, true);

    if (approx.size() == 4 && cv::isContourConvex(approx)) {
      cv::Moments m = cv::moments(approx);
      if (m.m00 == 0) continue;

      cv::Point2f center(m.m10 / m.m00, m.m01 / m.m00);
      double dist = cv::norm(center - imageCenter);
      if (dist < minDistanceToCenter) {
        minDistanceToCenter = dist;
        bestApprox = approx;
      }
    }
  }

  if (!bestApprox.empty()) {
    cv::Mat debugContour = image.clone();
    std::vector<std::vector<cv::Point>> drawVec = {bestApprox};
    cv::polylines(debugContour, drawVec, true, cv::Scalar(0, 255, 255), 3);

    for (size_t i = 0; i < bestApprox.size(); ++i) {
      cv::circle(debugContour, bestApprox[i], 5, cv::Scalar(0, 0, 255), -1);
      cv::putText(debugContour, std::to_string(i),
        bestApprox[i] + cv::Point(5, 5),
        cv::FONT_HERSHEY_SIMPLEX, 0.5,
        cv::Scalar(255, 255, 255), 1);
    }
  }

  for (const auto& l : linesP) {
    int mx = (l[0] + l[2]) / 2;
    int my = (l[1] + l[3]) / 2;

    if (cv::pointPolygonTest(bestApprox, cv::Point(mx, my), false) >= 0) {
      filteredLinesP.push_back(l);
    }
  }

  horizontals_.clear();
  verticals_.clear();
  for (const auto& line : filteredLinesP) {
    int x1 = line[0], y1 = line[1], x2 = line[2], y2 = line[3];
    double dx = std::abs(x1 - x2);
    double dy = std::abs(y1 - y2);
    if (dy > dx * 2)
      verticals_.push_back(line);
    else if (dx > dy * 2)
      horizontals_.push_back(line);
  }

  verticals_ = filter_close_verticals(verticals_, 10);
  horizontals_ = filter_close_horizontals(horizontals_, 10);

  std::vector<cv::Point2f> houghPoints =
      find_intersections(horizontals_, verticals_);
  std::vector<cv::Point2f> points = filter_to_9x9_hough_grid(houghPoints);

  std::sort(points.begin(), points.end(),
            [](const cv::Point2f& a, const cv::Point2f& b) {
              return a.y < b.y;
            });

  std::vector<std::vector<cv::Point2f>> grid(9);
  for (int i = 0; i < 9; ++i) {
    grid[i].assign(points.begin() + i * 9, points.begin() + (i + 1) * 9);
    std::sort(grid[i].begin(), grid[i].end(),
              [](const cv::Point2f& a, const cv::Point2f& b) {
                return a.x < b.x;
              });
  }
  result = classify_boardpieces(grid, image, gray);
  return result;
}
