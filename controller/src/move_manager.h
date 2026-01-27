#ifndef MOVE_MANAGER_H_
#define MOVE_MANAGER_H_
#include <array>
#include <iostream>
#include <memory>
#include <optional>
#include <vector>
#include <utility>
#include <string>

#include "button.h"

typedef int Square;
using std::string;

struct BoardPosition {
  int X;
  int Y;

  BoardPosition(int x, int y) : X(x), Y(y) {}
  BoardPosition() : X(0), Y(0) {}
};

struct MoveManagerConfig {
  const int portX, portY, portZ, portG;
  const int open, closed, up, down, downOutside;
  int sPortX, sPortY, sPortZ;

  const BoardPosition a1, f8, x1, y8, camPos;

  MoveManagerConfig(int PortX, int PortY, int PortZ, int PortG, int Open,
                    int Closed, int Up, int Down, int DownOutside,
                    BoardPosition A1, BoardPosition F8, BoardPosition X1,
                    BoardPosition Y8, BoardPosition CamPos, int SPortX,
                    int SPortY, int SPortZ)
      :

        portX(PortX),
        portY(PortY),
        portZ(PortZ),
        portG(PortG),
        open(Open),
        closed(Closed),
        up(Up),
        down(Down),
        downOutside(DownOutside),
        a1(A1),
        f8(F8),
        x1(X1),
        y8(Y8),
        camPos(CamPos),
        sPortX(SPortX),
        sPortY(SPortY),
        sPortZ(SPortZ) {}
};

class MoveManager {
 public:
  MoveManager();

  explicit MoveManager(MoveManagerConfig& config);

  virtual ~MoveManager() = default;

  virtual void moveToDegreeWithPID(int port, const std::string& deg);
  virtual void moveAboutDegreeWithPID(int port, const std::string& deg);
  virtual void moveToPosition(int port, const std::string& pos);

  virtual void stopMovement(int port);
  virtual void stopMovementAll();

  virtual void returnToZeroPosition(int port);
  virtual void returnToZeroPositionAll();

  virtual void moveToStartPosition();
  virtual void moveToStart(int port);

  virtual void returnToWaitPositionAll();

  virtual void setZeroPosition(int port);
  virtual void setZeroPositionAll();
  virtual void setZeroDegree(int port);

  virtual void setUp();

  // higher level functions
  virtual void moveToField(const BoardPosition& field);

  virtual void grabPiece(bool offBoard);
  virtual void dropPiece(bool offBoard);

  virtual void movePieceFromFieldToField(const BoardPosition& from,
                                 const BoardPosition& to, bool offBoardGrab,
                                 bool offBoardDrop);

  virtual bool movePiece(Square from, Square to);

  virtual void moveToCamPos();

  int currentDegree[4];
  int currentPos[4];

  static std::vector<std::unique_ptr<Button>> limitSwitches;
  int sPortX, sPortY, sPortZ;
  virtual void test();

 private:
  // variables

  const int portX, portY, portZ, portG;

  const int open, closed, up, down, downOutside;

  const BoardPosition a1, f8, x1, y8, camPos;

  // functions
  static int positive_modulo(const int value, const int mod) {
    return (value % mod + mod) % mod;
  }


  static std::string getPortString(int port, std::array<std::string, 4>);

  static int waitForStop(int port, bool parallel);

  [[nodiscard]] BoardPosition convertSquareToPos(Square sq) const;
};

#endif  // MOVE_MANAGER_H_
