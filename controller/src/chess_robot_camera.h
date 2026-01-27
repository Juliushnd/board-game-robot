#ifndef CHESS_ROBOT_CAMERA_H_
#define CHESS_ROBOT_CAMERA_H_
#include <libcamera/camera_manager.h>
#include <opencv2/opencv.hpp>

class ChessRobotCamera{
 public:
    ChessRobotCamera();
    virtual ~ChessRobotCamera();
    virtual void start();
    virtual void stop();
    virtual cv::Mat captureImage();

 private:
    libcamera::CameraManager manager;
};
#endif  // CHESS_ROBOT_CAMERA_H_
