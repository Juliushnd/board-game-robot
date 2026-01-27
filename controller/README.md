# Controller

## Features
### Robot Controller
All features are implemented in the "move_manager" class. 
The move_manger communicates via the build hat to control the motors of the robot. 
The move_manager contains functionality to:
- communicate with the build hat
- use the PID controller to move the motors
- access the limit switches
- move to certain positions
- wait for the end of movement
- routines to move pieces across the board
- communicating with backend

### Camera
- capturing and saving
### Board detection
- chess board detection
- chess piece classification
## Requirements


Installation of Package: libserial library Version: 1.0.0-7
```bash
sudo apt install libserial-dev
```
Installation of cmake Version: 3.25.1-1

```bash
apt-get install cmake
```
Installation of Package: libgpiod-dev Version: 1.6.3-1+b3

```bash
sudo apt install libgpiod-dev
```
instalation of Package: libgtest-dev Version: 1.12.1-0.2
```bash
sudo apt-get install libgtest-dev 
```
instalation of Package: libgmock-dev Version: 1.12.1-0.2
```bash
sudo apt-get install libgmock-dev
```
Installation of Package: libopencv-dev Version: 4.6.0+dfsg-12
```bash
sudo apt install libopencv-dev
```
Installation of Package: libcamera-dev Version: 0.5.0+rpt20250429-1

```bash
sudo apt install libcamera-dev
```





## Setup
### Robot Controller
Neccessary steps to setup the rasberry pi for the usage of the Robot:

- firmware files from python library have to be in the given folder (folder is defined in config.hpp, currently /home/pi/BuildHat/firmware/)
    - firmware.bin
    - signature.bin
    - version
- compilation with cmake (currently found in /Documents/board-game-robot/controller)
- every time the raspberry pi is restarted, the firmware has to be loaded on the buildhat, this is done automatically when starting the program
- starting of TCP client to connect with the Backend


## Usage

The following commands can be used via the command line interface. The main class
forwards the commands to the "chess_robot_controller" class. 

  ```
  quit (ends the program)
  ```
  ```
  turn (ends the turn of the player)
  ```
  ```
  mm (prefix, rest is send to move_manager_cli)
  ```
  ```
  stop (stops movement of robot)
  ```

The movement functionality is implemented in the class “move_manager”.

The class “move_manager_cli” can be used to access the move_manager.

  The move_manager_cli class:
  - needs reference to move_manager
  - uses the public function “handleCommand”, which takes in a custom command to activate some of the higher-level functions of the move_manager class
  - when using our main.cpp, the prefix "mm" can be used to send the command to the move_manager_cli
  - separate the command with spaces to the input of the function (e.g. pos 3 -1000) changes the position of the robot on port 3 (Y-Axis) to -1000, movement in the positive direction (e.g. pos 3 1000) can lead to problems
  - the start position is 0 for all motors
  - other functionality of the move_manager_cli class include:


    ```
    mm pos [port] [position] (moves motor on port to position)
    ```
    ```
    mm move [field 1] [field 2] (moves a piece from field 1 to field 2)
    ```
    ```
    mm setzero (changes the zero position of all motors to the current positions
    ```
    ```
    mm drop (executes the drop method which moves down the grabber, opens it, moves it up and closes it again)
    ```
    ```
    mm dropo (same as drop but for outside of the board)
    ```
    ```
    mm grab (analog to drop)
    ```
    ```
    mm test (starts a test function which performs 20 moves in a row)
    ```
    ```
    mm start (moves the robot to the start position, so to the position of the three limit switches)
    ```

### Camera
The ChessRobotCamera class provides an interface for capturing images using the Raspberry Pi camera through the libcamera API and OpenCV.
It starts and stops the CameraManager, initializes the camera, and manages configuration using libcamera::CameraManager.

The captured frame is in BGR format (2304x1296 resolution), which is directly supported by OpenCV.
The image buffer is converted into an OpenCV matrix for further image processing in the HoughBoardDetection class.

### HoughBoardDetection
The HoughBoardDetection class detects an image of a chessboard and extracts all the 64 fields.
It uses OpenCV to apply Canny edge detection, Hough line transformation, and image analysis techniques and filters.
Through classifying the 64 fields the class uses different parameters
and dependencies to classify the pieces on the squares as white, black or empty.
Having a OpenCV matrix as input the class provides the function "detectBoard"
which returns an char array which presents the actual board state.

The HoughBoardDetection class uses HoughLinesP to find straight lines in the image and Canny Edge Detection for further finding contours.
Having found contours, the chessboard can be extracted and lines outside the board can be filtered.
Using different functions for finding intersections and filtering only 9x9 inner points of the chess board
the class also uses K-Means clustering.
Having inner points of the board we can extract every 64 squares of the board for further piece classification

The HoughBoardDetection class detects a chessboard in an image using the following steps:
- HoughLinesP is used to detect straight lines.
- Canny edge detection for finding contours and the 4 outter edges of the board.
- Several algorithm for filtering and finding intersections of the lines detected.
- K-Means clustering identify only the inner 9×9 grid points (intersections).
- With these inner points, the board is divided into 64 squares, each of which can be used for further piece classification.
- piece classification through algorithms using parameters as:
  - hue,
  - saturation,
  - grayscale,
  - sharpness,
  - contast,
  - contours
## Testing & Linting

### Linting code using cpplint

#### Installation

```bash
pip install cpplint
```

#### Usage

```bash
cpplint --recursive src
```

### Analyzing code using cppcheck

#### Installation

```bash
sudo apt install cppcheck
```

#### Usage

```bash
mkdir -p build && cd build
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..
mkdir -p .cppcheck
cppcheck --cppcheck-build-dir=.cppcheck --error-exitcode=1 --project=compile_commands.json --suppressions-list=../cppcheck-suppressions.txt
```

### Testing code using CTest

#### Usage

```bash
mkdir -p build && cd build
cmake -DBUILD_TESTS=ON ..
make
ctest --output-on-failure
```

### Updating CI docker image

The CI pipeline uses a docker image with all build tools and dependencies installed to run the controller jobs. This image is defined in `ci.Dockerfile` and can be built and pushed using the following commands:

```bash
# Log in to TUB GitLab container registry
docker login git.tu-berlin.de:5000
# Build CI docker image
docker build -f ci.Dockerfile -t git.tu-berlin.de:5000/ees-mpsees-sose25-playing-2/board-game-robot/controller .
# Push CI docker image
docker push git.tu-berlin.de:5000/ees-mpsees-sose25-playing-2/board-game-robot/controller:latest
```
