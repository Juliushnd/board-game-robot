#include <gtest/gtest.h>

#include "../src/chess_robot_controller.h"
#include "mocks/mock_board_detection.h"
#include "mocks/mock_button.h"
#include "mocks/mock_chess_robot_camera.h"
#include "mocks/mock_move_manager.h"
#include "mocks/mock_tcp_client.h"

namespace testing {

TEST(ChessRobotControllerTest, Constructor) {
  StrictMock<MockTCPClient> backendClient("localhost", 3000);
  StrictMock<MockChessRobotCamera> camera;
  StrictMock<MockBoardDetection> boardDetection;
  StrictMock<MockMoveManager> moveManager;
  StrictMock<MockButton> endOfTurnButton("chip1", 42);

  auto controller = ChessRobotController(backendClient, camera, boardDetection,
                                         moveManager, endOfTurnButton);

  EXPECT_FALSE(controller.isConnected());
  EXPECT_FALSE(controller.isRunning());
}

TEST(ChessRobotControllerTest, StartConnectStop) {
  StrictMock<MockTCPClient> backendClient("localhost", 3000);
  StrictMock<MockChessRobotCamera> camera;
  StrictMock<MockBoardDetection> boardDetection;
  StrictMock<MockMoveManager> moveManager;
  StrictMock<MockButton> endOfTurnButton("chip1", 42);

  auto controller = ChessRobotController(backendClient, camera, boardDetection,
                                         moveManager, endOfTurnButton);

  EXPECT_FALSE(controller.isConnected());
  EXPECT_FALSE(controller.isRunning());

  Expectation connect =
      EXPECT_CALL(backendClient, connectToServer).WillOnce(Return(true));
  EXPECT_CALL(backendClient, receiveMessage)
      .After(connect)
      .WillOnce(InvokeWithoutArgs([]() {
        sleep(2);
        return "";
      }));
  EXPECT_CALL(moveManager, setUp);
  EXPECT_CALL(camera, start);
  EXPECT_CALL(endOfTurnButton, init);
  EXPECT_CALL(endOfTurnButton, isPressed)
      .Times(AtLeast(1))
      .WillRepeatedly(Return(false));

  controller.start();

  sleep(1);

  EXPECT_TRUE(controller.isConnected());
  EXPECT_TRUE(controller.isRunning());

  EXPECT_CALL(camera, stop);
  EXPECT_CALL(backendClient, closeConnection);

  controller.stop();

  EXPECT_FALSE(controller.isConnected());
  EXPECT_FALSE(controller.isRunning());
}

}  // namespace testing