#include "move_manager.h"

#include <array>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#include "buildhat++/BuildHat.hpp"

using std::string, std::array;

MoveManager::MoveManager()
    : portX(2),
      portY(3),
      portZ(1),
      portG(0),
      open(400),
      closed(0),
      up(0),
      down(-700),
      downOutside(-1200),
      a1(BoardPosition(-600, -2250)),
      f8(BoardPosition(-8700, -4350)),
      x1(BoardPosition(-600, -1400)),
      y8(BoardPosition(-8500, -900)),
      camPos(BoardPosition(-6700, -1100)),
      sPortX(26),
      sPortY(27),
      sPortZ(13),
      currentDegree{0, 0, 0, 0},
      currentPos{0, 0, 0, 0} {}

MoveManager::MoveManager(MoveManagerConfig& config)
    : portX(config.portX),
      portY(config.portY),
      portZ(config.portZ),
      portG(config.portG),
      open(config.open),
      closed(config.closed),
      up(config.up),
      down(config.down),
      downOutside(config.downOutside),
      sPortX(config.sPortX),
      sPortY(config.sPortY),
      sPortZ(config.sPortZ),
      a1(config.a1),
      f8(config.f8),
      x1(config.x1),
      y8(config.y8),
      camPos(config.camPos),
      currentDegree{0, 0, 0, 0},
      currentPos{0, 0, 0, 0} {}

std::vector<std::unique_ptr<Button>> MoveManager::limitSwitches;

// gets the last string from the given port, if it exists in the
// last four strings
string MoveManager::getPortString(const int port, array<string, 4> s) {
  if (port < 0 || port > 3) {
    std::cerr << "Error: Invalid port number.\n";
    return "";
  }
  BuildHat& hat = BuildHat::getInstance();

  std::pair<int, int> p;
  for (int i = 0; i < 4; ++i) {
    p = hat.getIntFromStr(s[i], 0);
    if (p.first == port) return s[i];
  }
  return "";
}

void MoveManager::setUp() {
  // flashes drive
  BuildHat& hat = BuildHat::getInstance();
  stopMovementAll();

  // make sure gpio is ready
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));
  // order is important, 12 only dummy number
  limitSwitches.push_back(std::make_unique<Button>("gpiochip0", 12));
  limitSwitches.push_back(std::make_unique<Button>("gpiochip0", sPortZ));
  limitSwitches.push_back(std::make_unique<Button>("gpiochip0", sPortX));
  limitSwitches.push_back(std::make_unique<Button>("gpiochip0", sPortY));

  for (const auto & limitSwitch : limitSwitches) {
    limitSwitch->init();
  }

  moveToStartPosition();
}

// moves the motor on port to the degree with a PID controller
void MoveManager::moveToDegreeWithPID(const int port, const string& deg) {
  if (port < 0 || port > 3) {
    std::cerr << "Error: Invalid port number.\n";
    return;
  }

  BuildHat& hat = BuildHat::getInstance();

  string str = hat.serial_write_read(
      "port " + std::to_string(port) +
          "; plimit 1; combi 0 1 0 2 0 3 0; selonce 0; pid " +
          std::to_string(port) + " 0 5 s2 1 360 0.05 0.002 0.001 100 0 ; set " +
          deg,
      false);
}

// turns the motor at port about the given degree
void MoveManager::moveAboutDegreeWithPID(const int port, const string& deg) {
  if (port < 0 || port > 3) {
    std::cerr << "Error: Invalid port number.\n";
    return;
  }

  int newDeg = 0;

  // get degree from serial interface
  BuildHat& hat = BuildHat::getInstance();
  std::pair<int, int> val = hat.getValueOfPort(port, 2);  // index 2: degree
  if (port != 0) currentDegree[port] = positive_modulo(val.second, 360);

  // depending on the current angle of the motor, the movement is different
  // when degree higher 180, the motor adds one 360 degree rotation
  try {
    if (currentDegree[port] < 180) {
      newDeg = std::stoi(deg) + currentDegree[port];
    } else {
      newDeg = std::stoi(deg) + currentDegree[port] - 360;
    }
  } catch (const std::invalid_argument& e) {
    std::cerr << "Invalid Argument: " << deg << "'\n";
    return;
  }

  moveToDegreeWithPID(port, std::to_string(newDeg));
}

// move the motor at port to the degree using moveAboutDegreeWithPID
void MoveManager::moveToPosition(const int port, const string& pos) {
  if (port < 0 || port > 3) {
    std::cerr << "Error: Invalid port number.\n";
    return;
  }

  int position;

  try {
    position = std::stoi(pos);
  } catch (const std::invalid_argument& e) {
    std::cerr << "Invalid Argument: " << pos << "'\n";
    return;
  }

  // calculate the necessary rotation depending on current positon
  // and goal position
  int deg = currentPos[port] - position;
  currentPos[port] = position;

  moveAboutDegreeWithPID(port, std::to_string(deg));
}

// stop movement of port
void MoveManager::stopMovement(const int port) {
  if (port < 0 || port > 3) {
    std::cerr << "Error: Invalid port number.\n";
    return;
  }

  BuildHat& hat = BuildHat::getInstance();
  hat.serial_write_line("port " + std::to_string(port) + "; pwm; set 0", false);
}

// stop movement of all ports
void MoveManager::stopMovementAll() {
  BuildHat& hat = BuildHat::getInstance();
  hat.serial_write_line("port 0; pwm; set 0", false);
  hat.serial_write_line("port 1; pwm; set 0", false);
  hat.serial_write_line("port 2; pwm; set 0", false);
  hat.serial_write_line("port 3; pwm; set 0", false);
}

// set the current position of motor at port to zero
void MoveManager::setZeroPosition(int port) {
  if (port < 0 || port > 3) {
    std::cerr << "Error: Invalid port number.\n";
    return;
  }

  currentPos[port] = 0;
}

// set the current degree of motor at port to zero
void MoveManager::setZeroDegree(int port) {
  if (port < 0 || port > 3) {
    std::cerr << "Error: Invalid port number.\n";
    return;
  }

  currentDegree[port] = 0;
}

// reset all positions to zero
void MoveManager::setZeroPositionAll() {
  for (int i = 0; i < 4; ++i) {
    setZeroPosition(i);
  }
}
// move motor at port to position zero
void MoveManager::returnToZeroPosition(int port) {
  if (port < 0 || port > 3) {
    std::cerr << "Error: Invalid port number.\n";
    return;
  }

  moveToPosition(port, "0");
}

// move all motors to position zero
void MoveManager::returnToZeroPositionAll() {
  for (int i = 0; i < 4; ++i) {
    returnToZeroPosition(i);
  }
}

// move all motors to the waiting position
void MoveManager::returnToWaitPositionAll() {
  // makes sure to move grabber up to not knock over pieces
  if (currentPos[portZ] == up) {
    moveToPosition(portG, std::to_string(closed));
  } else if (currentPos[portZ] == down) {
    // otherwise movement simultaneously, which can cause knocking over pieces
    moveToPosition(portG, std::to_string(up));
    waitForStop(portG, false);
    moveToPosition(portG, std::to_string(closed));
  }

  moveToPosition(portX, "0");
  moveToPosition(portY, "0");
}

void MoveManager::moveToStartPosition() {
  BuildHat& hat = BuildHat::getInstance();

  // first move Z-Position
  int posZ = 10000;  // random high number
  // only move if not pressed at the beginning
  if (!(*limitSwitches[portZ]).isPressed())
    moveToPosition(portZ, std::to_string(posZ));

  // wait till limit switch is pressed
  while (!(*limitSwitches[portZ]).isPressed()) {
  }
  stopMovement(portZ);
  setZeroPosition(portZ);

  // move x and y simultaneously
  int speedX = 1, speedY = 1;
  int posX = 10000, posY = 10000;  // random high numbers

  // only move if not at destination already
  if (!(*limitSwitches[portY]).isPressed()) {
    moveToPosition(portY, std::to_string(posY));
  } else {
    speedY = 0;
  }
  // only move if not at destination already
  if (!(*limitSwitches[portX]).isPressed()) {
    moveToPosition(portX, std::to_string(posX));
  } else {
    speedX = 0;
  }
  // wait till limit switches are pressed
  // if one is pressed, stop movement of that motor
  while (true) {
    if ((*limitSwitches[portX]).isPressed() && speedX == 1) {
      stopMovement(portX);
      speedX = 0;
    }
    if ((*limitSwitches[portY]).isPressed() && speedY == 1) {
      stopMovement(portY);
      speedY = 0;
    }

    // if both are done, end
    if (speedX == 0 && speedY == 0) {
      setZeroPosition(portX);
      setZeroPosition(portY);

      return;
    }
  }
}

// move motor of port to limit switch
void MoveManager::moveToStart(int port) {
  if (port < 0 || port > 3) {
    std::cerr << "Error: Invalid port number.\n";
    return;
  }

  // the grabber has no limit switch
  if (port == portG) return;

  moveToPosition(port, "10000");  // random high number
  while (!(*limitSwitches[port]).isPressed()) {
  }
  stopMovement(port);
  setZeroPosition(port);
}

// only for testing
void MoveManager::test() {
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));
  movePiece(52, 36);  // e2 → e4
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(12, 28);  // e7 → e5
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(62, 45);  // g1 → f3
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(57, 42);  // b8 → c6
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(61, 34);  // f1 → c4
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(50, 34);  // d7 → d5
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(36, 28);  // e4 × e5
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(42, 36);  // c6 → e5
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(59, 31);  // d1 → h5
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(49, 31);  // d8 × h5
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(31, -1);  // Figur auf 31 (h5)
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(49, 31);  // d8 → h5
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(45, 35);  // f3 → d4
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(58, 44);  // g8 → e7
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(60, 62);  // e1 → g1 (castle)
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(4, 6);  // e8 → g8 (castle)
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(35, 28);  // d4 × e5
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(36, -2);  // Figur auf 36 (e5)
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(35, 36);  // d4 → e5
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(53, 37);  // f2 → f4
  std::this_thread::sleep_for(std::chrono::milliseconds(2000));

  movePiece(11, 27);  // d7 → d6
}

// calculates the position of the motors depending on the given square and
// the position of a1 and f8 for squares on the board, and depending
// on x1 and y8 for squares off the board

BoardPosition MoveManager::convertSquareToPos(const Square sq) const {
  BoardPosition field;
  BoardPosition pos;

  // field next to board, for captured pieces
  if (sq < 0) {
    field.X = abs(sq + 1) / 2;
    field.Y = abs(sq + 1) % 2;

    if (field.Y == 0) {
      pos.Y = x1.Y;
    } else {
      pos.Y = y8.Y;
    }
    // use the distance between first and last field, multiply with position
    // and add the offset
    pos.X = x1.X + field.X * ((y8.X - x1.X) / 7);
    return pos;
  }

  // square on the board
  field.X = (sq) % 8;
  field.Y = (sq) / 8;
  // use the distance between first and last field, multiply with position
  // and add the offset
  pos.X = a1.X + field.X * ((f8.X - a1.X) / 7);
  pos.Y = a1.Y + field.Y * ((f8.Y - a1.Y) / 7);

  return pos;
}

// waits for motor to stop moving to prevent false actions
int MoveManager::waitForStop(const int port, const bool parallel) {
  if (port < 0 || port > 3) {
    std::cerr << "Error: Invalid port number.\n";
    return 0;
  }

  BuildHat& hat = BuildHat::getInstance();

  // only wait for one motor
  if (!parallel) {
    std::pair<int, int> motor = hat.isMotorMoving(port);
    auto [port, speed] = motor;

    // wait for movement
    // -1: error/not found
    while (speed == 0 || speed == -1) {
      motor = hat.isMotorMoving(port);
      std::tie(port, speed) = motor;

      // dont overload the serial stream
      std::this_thread::sleep_for(std::chrono::milliseconds(30));
    }

    // wait till end of movement
    while (speed != 0 || speed == -1) {
      motor = hat.isMotorMoving(port);
      std::tie(port, speed) = motor;

      // dont overload the serial stream
      std::this_thread::sleep_for(std::chrono::milliseconds(30));
    }

    return 1;
  }

  // wait for X and Y movement parallel, only two motors which can move
  // in parallel

  std::pair<int, int> motor2 = hat.isMotorMoving(2);
  auto [port2, speed2] = motor2;

  std::pair<int, int> motor3 = hat.isMotorMoving(3);
  auto [port3, speed3] = motor3;

  // wait for movement
  // -1 means "error" in "isMotorMoving"
  while ((speed2 == 0 || speed2 == -1) || (speed3 == 0 || speed3 == -1)) {
    motor2 = hat.isMotorMoving(2);
    std::tie(port2, speed2) = motor2;

    motor3 = hat.isMotorMoving(3);
    std::tie(port3, speed3) = motor3;

    // dont overload the serial stream
    std::this_thread::sleep_for(std::chrono::milliseconds(30));
  }
  // wait till end of movement
  while ((speed2 != 0 || speed2 == -1) || (speed3 != 0 || speed3 == -1)) {
    motor2 = hat.isMotorMoving(2);
    std::tie(port2, speed2) = motor2;

    motor3 = hat.isMotorMoving(3);
    std::tie(port3, speed3) = motor3;

    // dont overload the serial stream
    std::this_thread::sleep_for(std::chrono::milliseconds(30));
  }
  return 1;
}

void MoveManager::moveToField(const BoardPosition& field) {
  int distX = currentPos[portX] - field.X;
  int distY = currentPos[portY] - field.Y;

  // if movement to small, detection can be buggy
  // then we wait for movement, which won't come --> deadlock

  // parallel movement of y and x axis
  if (abs(distX) > 200 && abs(distY) > 200) {
    moveToPosition(portX, std::to_string(field.X));
    moveToPosition(portY, std::to_string(field.Y));
    waitForStop(portX, true);

    return;
  }
  // move the robot to the right position and wait for stop of movement
  if (currentPos[portX] != field.X) {
    moveToPosition(portX, std::to_string(field.X));
    waitForStop(portX, false);
  }
  if (currentPos[portY] != field.Y) {
    moveToPosition(portY, std::to_string(field.Y));
    waitForStop(portY, false);
  }
}

// grabs a piece
void MoveManager::grabPiece(const bool offBoard) {
  moveToPosition(portG, std::to_string(open));
  waitForStop(portG, false);

  int downValue;  // is piece on or off the board
  offBoard ? downValue = downOutside : downValue = down;

  moveToPosition(portZ, std::to_string(downValue));
  waitForStop(portZ, false);

  moveToPosition(portG, std::to_string(closed));
  waitForStop(portG, false);

  moveToStart(portZ);
}

// drops piece off
void MoveManager::dropPiece(const bool offBoard) {
  int downValue;  // drop piece on or off board
  offBoard ? downValue = downOutside : downValue = down;

  moveToPosition(portZ, std::to_string(downValue));
  waitForStop(portZ, false);

  moveToPosition(portG, std::to_string(open));
  waitForStop(portG, false);

  moveToStart(portZ);

  moveToPosition(portG, std::to_string(closed));
  waitForStop(portG, false);
}

// routine to move a pice to the new position
void MoveManager::movePieceFromFieldToField(const BoardPosition& from,
                                            const BoardPosition& to,
                                            const bool offBoardGrab,
                                            const bool offBoardDrop) {
  moveToField(from);

  grabPiece(offBoardGrab);

  moveToField(to);

  dropPiece(offBoardDrop);

  moveToStartPosition();
}

bool MoveManager::movePiece(const Square from, const Square to) {
  // if y smaller zero, then x coordinate is counter for captured pieces
  if (from > 63 || from < -16 || to > 63 || to < -16) return false;

  if (from == to) return false;  // just pick up and drop piece

  // gets real coordinates
  const BoardPosition first = convertSquareToPos(from);
  BoardPosition second = convertSquareToPos(to);

  // parameters for movement off the board
  bool offBoardGrab, offBoarDrop;
  from < 0 ? offBoardGrab = true : offBoardGrab = false;
  to < 0 ? offBoarDrop = true : offBoarDrop = false;

  // compensate error in the robot movement
  if (first.Y < second.Y) {
    second.Y += 150;
  }
  movePieceFromFieldToField(first, second, offBoardGrab, offBoarDrop);

  return true;
}

// moves the robot in position to take a picture
void MoveManager::moveToCamPos() {
  moveToField(camPos);
}
