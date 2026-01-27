FROM python:3.12-slim

RUN apt-get update && apt-get install -y stockfish

# Add stockfish to PATH.
ENV PATH="/usr/games:$PATH"
