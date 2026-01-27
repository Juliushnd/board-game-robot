# Backend
The backend component is the main entry point to the Board Game Robot project and necessary for playing with either the robot or frontend application. 

The backend also contains the components handling the game logic.
## Requirements
The following software must be installed:
- `npm` at version 11.3.0 or above
- `stockfish` at version 17.1 or above

## Setup
```bash
pip install -r requirements.txt
```

## Usage
To start the backend run the following command
```bash
python main.py
```
## Testing & Linting

All commands below require that the development dependencies have been installed:

```bash
pip install -r requirements-dev.txt
```

### Linting code using pylint

#### Usage

```bash
pylint --output-format=text .
```

### Testing code using pytest

#### Usage

```bash
pytest -v
```

### Updating CI docker image

The CI pipeline uses a docker image with all dependencies installed to run the backend jobs.
This image is defined in `ci.Dockerfile` and can be built and pushed using the following commands:

```bash
# Log in to TUB GitLab container registry
docker login git.tu-berlin.de:5000
# Build CI docker image
docker build -f ci.Dockerfile -t git.tu-berlin.de:5000/ees-mpsees-sose25-playing-2/board-game-robot/backend .
# Push CI docker image
docker push git.tu-berlin.de:5000/ees-mpsees-sose25-playing-2/board-game-robot/backend:latest
```
