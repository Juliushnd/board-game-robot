//
// Created by adam on 21.05.25.
//

#include "tcp_client.h"

#include <iostream>
#include <string>

TCPClient::TCPClient(const std::string& serverIP, int port)
    : serverIP(serverIP), port(port), sockfd(-1), connected(false) {}

bool TCPClient::connectToServer() {
  sockfd = socket(AF_INET, SOCK_STREAM, 0);
  if (sockfd < 0) {
    std::cerr << "Socket creation failed\n";
    return false;
  }

  sockaddr_in serverAddr{};
  serverAddr.sin_family = AF_INET;
  serverAddr.sin_port = htons(port);

  if (inet_pton(AF_INET, serverIP.c_str(), &serverAddr.sin_addr) <= 0) {
    std::cerr << "Invalid address or address not supported\n";
    return false;
  }
  int sizeServerAddr = sizeof(serverAddr);
  if (connect(sockfd, (struct sockaddr*)&serverAddr, sizeServerAddr) < 0) {
    std::cerr << "Connection to server failed\n";
    return false;
  }

  connected = true;
  std::cout << "Connected to server\n";
  return true;
}

bool TCPClient::sendMessage(const std::string& message) {
  if (!connected) return false;
  std::string sendMessage = message + "\n";
  if (send(sockfd, sendMessage.c_str(), sendMessage.length(), 0) < 0) {
    std::cerr << "Failed to send message\n";
    return false;
  }
  return true;
}

std::string TCPClient::receiveMessage() {
  if (!connected) return "";
  char byte;
  std::string message;

  while (true) {
    int bytesReceived = recv(sockfd, &byte, 1, 0);
    if (bytesReceived <= 0) {
      std::cerr << "Failed to receive message or connection closed\n";
      break;
    }
    if (byte == '\n') {
      break;
    }
    message += byte;
  }
  return message;
}

void TCPClient::closeConnection() {
  if (connected) {
    close(sockfd);
    connected = false;
    std::cout << "Connection closed\n";
  }
}
