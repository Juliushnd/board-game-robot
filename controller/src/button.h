//
// Created by adam on 21/06/25.
//

#include <gpiod.h>
#include <string>
#include <stdexcept>

#ifndef BUTTON_H_
#define BUTTON_H_



class Button {
 public:
  Button(const std::string& chipName, unsigned int lineNum);
  virtual ~Button();

  virtual void init();
  virtual bool isPressed() const;

 private:
  std::string chipName;
  unsigned int lineNum;
  gpiod_chip* chip;
  gpiod_line* line;
  bool initialized = false;
};

#endif  // BUTTON_H_
