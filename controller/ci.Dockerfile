FROM gcc:latest

RUN apt-get update && apt-get install -y python3-pip python3-venv cppcheck cmake libgtest-dev libgmock-dev libgpiod-dev libopencv-dev libcamera-dev libserial-dev

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install cpplint
