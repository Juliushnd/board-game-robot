cmake_minimum_required(VERSION 3.10)
project(controller)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find and set up dependencies.
find_package(PkgConfig REQUIRED)
find_package(OpenCV REQUIRED)
find_package(Threads REQUIRED)
find_library(SERIAL_LIB serial)
pkg_check_modules(GPIOD REQUIRED libgpiod)
pkg_check_modules(LIBCAMERA REQUIRED libcamera)
pkg_check_modules(OPENCV REQUIRED opencv4)

include_directories(${LIBCAMERA_INCLUDE_DIRS} ${OPENCV_INCLUDE_DIRS} ${GPIOD_INCLUDE_DIRS})
link_directories(${LIBCAMERA_LIBRARY_DIRS} ${OPENCV_LIBRARY_DIRS})
link_libraries(
        Threads::Threads
        ${LIBCAMERA_LIBRARIES}
        ${OPENCV_LIBRARIES}
        ${SERIAL_LIB}
        ${GPIOD_LIBRARIES}
)
add_compile_options(${LIBCAMERA_CFLAGS_OTHER} ${OPENCV_CFLAGS_OTHER})
add_compile_definitions("DEBUG=$<IF:$<CONFIG:Debug>,1,0>")

# Create a library containing the buildhat++ code.
add_library(buildhat_lib
        ${CMAKE_SOURCE_DIR}/src/buildhat++/BuildHat.cpp
        ${CMAKE_SOURCE_DIR}/src/buildhat++/BuildHat.hpp
        ${CMAKE_SOURCE_DIR}/src/buildhat++/config.hpp
        ${CMAKE_SOURCE_DIR}/src/buildhat++/utils/Utilities.cpp
        ${CMAKE_SOURCE_DIR}/src/buildhat++/utils/Utilities.hpp
)

# Create a library containing all of the controller code so we don't need to compile it again for testing.
add_library(controller_lib
        ${CMAKE_SOURCE_DIR}/src/chess_robot_camera.cpp
        ${CMAKE_SOURCE_DIR}/src/chess_robot_camera.h
        ${CMAKE_SOURCE_DIR}/src/tcp_client.cpp
        ${CMAKE_SOURCE_DIR}/src/tcp_client.h
        ${CMAKE_SOURCE_DIR}/src/button.cpp
        ${CMAKE_SOURCE_DIR}/src/button.h
        ${CMAKE_SOURCE_DIR}/src/chess_robot_controller.cpp
        ${CMAKE_SOURCE_DIR}/src/chess_robot_controller.h
        ${CMAKE_SOURCE_DIR}/src/move_manager.cpp
        ${CMAKE_SOURCE_DIR}/src/move_manager.h
        ${CMAKE_SOURCE_DIR}/src/move_manager_cli.cpp
        ${CMAKE_SOURCE_DIR}/src/move_manager_cli.h
        ${CMAKE_SOURCE_DIR}/src/board_detection.h
        ${CMAKE_SOURCE_DIR}/src/dummy_board_detection.h
        ${CMAKE_SOURCE_DIR}/src/dummy_board_detection.cpp
        ${CMAKE_SOURCE_DIR}/src/hough_board_detection.h
        ${CMAKE_SOURCE_DIR}/src/hough_board_detection.cpp
)

# Create the main controller executable.
add_executable(controller ${CMAKE_SOURCE_DIR}/src/main.cpp)

# Link buildhat_lib to controller_lib.
target_link_libraries(controller_lib buildhat_lib)

# Link controller_lib to main executable.
target_link_libraries(controller controller_lib)

# Set up tests (see tests/CMakeLists.txt).
enable_testing()
add_subdirectory(tests)