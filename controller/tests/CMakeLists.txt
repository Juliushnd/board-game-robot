find_package(GTest REQUIRED)

# Create test executable.
add_executable(controller_tests
        ${CMAKE_SOURCE_DIR}/tests/test_chess_robot_controller.cpp
        ${CMAKE_SOURCE_DIR}/tests/test_hough_board_detection.cpp
)

# Link controller_lib and testing libraries to test executable.
target_link_libraries(controller_tests controller_lib gtest gtest_main gmock)

# Register test executable with CTest.
add_test(NAME ControllerTests COMMAND controller_tests)

# Copy test images to build directory.
add_custom_command(TARGET controller_tests POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CMAKE_SOURCE_DIR}/tests/images
        ${CMAKE_CURRENT_BINARY_DIR}/images
)