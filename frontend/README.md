# Frontend

The Frontend is an optional part of the [Board Game Robot](../README.md) project which is used to visualize and control 
the game state. It is a static web application built using JavaScript and [React](https://react.dev/).

The Backend and Controller are not dependent on the Frontend and can run without it.

## Features

The frontend application has the following main features:

- Starting, ending and restarting the game
- Displaying the current board state and list of moves
- Setting the board orientation
- Changing the agent to play against
- Changing the initial board state
- Changing the list of moves to fix incorrectly detected moves
- Displaying errors

## Requirements

The following software must be installed to build and host the frontend application:

- `npm` at version 11.3.0 or above
- A web server hosting any files located in `/var/www/html` (e.g. `apache2`)

### Example `npm` setup

The following commands can be used to set up `nvm`, `node`, and `npm`:
```bash
# Install nvm (node version manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
# Install into environment (the above command outputs this)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
# Install node 22 (includes npm)
nvm install 22
```

### Example `apache2` setup

The following commands can be used to set up `apache2` as a web server:

```bash
sudo apt install apache2
```

## Setup

Run the following command to install all JavaScript dependencies:

```bash
npm install
```

## Usage

### Development mode

In development mode, the application is built on-the-fly and served by a development web server.

1. Configure the Backend API and WebSocket URL for development mode in the file `.env.development`. The default should 
   work for local development.
2. Serve the frontend application in development mode using the following command:
   ```bash
   npm run dev
   ```
3. The application is then available at [http://localhost:5173/](http://localhost:5173/). It is automatically rebuilt when changes to any 
   source files are detected. 

This mode should not be used in production environments. Use [Production mode](#production-mode) instead.

### Production mode

In production mode, the application is pre-built and minified to be hosted by a dedicated web server as a static site.

1. Configure the Backend API and WebSocket URL for production mode in the file `.env.production`. 
2. Build the frontend application as a static site for production using the following command:
   ```bash
   npm run build
   ```
3. The built application can then be found in the `dist` directory.
4. To host the application, copy the contents of the `dist` directory to `/var/www/html`:
   ```bash
   cp -r dist/* /var/www/html/
   ```
5. The `/var/www/html` directory needs to be hosted by a dedicated web server (see [Requirements](#requirements)).

## Testing & Linting

All commands below require that the development dependencies have been installed using the following command:

```bash
npm ci
```

### Linting code using eslint

The linter can be run to verify that the code adheres to the predefined coding style.

#### Usage

```bash
npm run lint
```

### Testing code using vitest

The tests can be run to verify that new changes to the code do not break existing features.

#### Usage

```bash
npm test
```

## Acknowledgements

The following third party libraries were used in this component:

- [React](https://react.dev/)
- [Font Awesome](https://fontawesome.com/)
- [Bootstrap](https://getbootstrap.com/)
- [React Bootstrap](https://react-bootstrap.github.io/)
- [React Chessboard](https://github.com/Clariity/react-chessboard)
