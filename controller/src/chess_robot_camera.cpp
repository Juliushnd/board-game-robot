#include "chess_robot_camera.h"

#include <libcamera/camera.h>
#include <libcamera/stream.h>
#include <libcamera/formats.h>
#include <libcamera/camera_manager.h>
#include <libcamera/framebuffer_allocator.h>
#include <libcamera/request.h>
#include <unistd.h>
#include <sys/mman.h>

#include <chrono>
#include <iostream>
#include <memory>
#include <thread>

#include <opencv2/opencv.hpp>

ChessRobotCamera::ChessRobotCamera() {}
ChessRobotCamera::~ChessRobotCamera() {}

void ChessRobotCamera::start() {
  if (manager.start() != 0) {
    std::cerr << "CameraManager may not start!\n";
  }
}

void ChessRobotCamera::stop() {
  manager.stop();
}

cv::Mat ChessRobotCamera::captureImage() {
  if (manager.cameras().empty()) {
    std::cerr << "no camera found!\n";
    return {};
  }

  std::shared_ptr<libcamera::Camera> camera = manager.cameras()[0];
  camera->acquire();
  std::unique_ptr<libcamera::CameraConfiguration> config =
    camera->generateConfiguration({libcamera::StreamRole::StillCapture});
  config->at(0).pixelFormat = libcamera::formats::BGR888;
  config->at(0).size.width = 2304;
  config->at(0).size.height = 1296;
  camera->configure(config.get());

  libcamera::Stream* stream = config->at(0).stream();

  libcamera::FrameBufferAllocator allocator(camera);
  allocator.allocate(stream);

  std::unique_ptr<libcamera::Request> request = camera->createRequest();
  libcamera::FrameBuffer* buffer = allocator.buffers(stream)[0].get();
  request->addBuffer(stream, buffer);

  camera->start();
  camera->queueRequest(request.get());
  std::this_thread::sleep_for(std::chrono::milliseconds(500));
  camera->stop();

  int fd = buffer->planes()[0].fd.get();
  size_t length = buffer->planes()[0].length;
  void* data = mmap(nullptr, length, PROT_READ, MAP_SHARED, fd, 0);

  if (data == MAP_FAILED) {
    std::cerr << "mmap failed!\n";
    camera->release();
    return {};
  }

  cv::Mat image(1296, 2304, CV_8UC3, data);
  cv::Mat result = image.clone();
  munmap(data, length);

  std::this_thread::sleep_for(std::chrono::milliseconds(200));
  camera->release();
  return result;
}
