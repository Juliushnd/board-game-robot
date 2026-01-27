#ifndef MOCK_BUTTON_H
#define MOCK_BUTTON_H

#include <gmock/gmock.h>

#include "../../src/button.h"

class MockButton : public Button {
 public:
  MockButton(const std::string& chipName, unsigned int lineNum)
      : Button(chipName, lineNum) {};

  MOCK_METHOD(void, init, (), (override));
  MOCK_METHOD(bool, isPressed, (), (const, override));
};

#endif  // MOCK_BUTTON_H
