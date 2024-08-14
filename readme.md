# BlackJack Game

This project implements a multiplayer BlackJack game with a Python backend server and a React frontend.

## Project Structure

- `multi-deck.py`: Python server that manages the deck and card drawing
- `index.html`: HTML entry point for the React application
- `styles.css`: CSS styles for the game interface
- `game.js`: React component implementing the game logic and UI

## Features

- Multiplayer support for up to 7 players
- Realistic deck management with multiple decks
- Betting system
- Full game logic including hit, stand, and double down actions
- Responsive design for various screen sizes

## Prerequisites

- Python 3.7+
- Node.js and npm

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/blackjack-game.git
   cd blackjack-game
   ```

2. Install Python dependencies:
   ```
   pip install numpy
   ```

3. Install Node.js dependencies:
   ```
   npm install react react-dom
   ```

## Running the Game

1. Start the Python server:
   ```
   python multi-deck.py
   ```
   The server will run on `http://localhost:3040` by default.

2. In a new terminal, start the React development server:
   ```
   npx create-react-app .
   npm start
   ```
   The React app will run on `http://localhost:3000` by default.

3. Open your browser and navigate to `http://localhost:3000` to play the game.

## Game Rules

- The game uses 6 decks of cards.
- Each player starts with a balance of $1000.
- Players can bet between $10 and their current balance.
- Players can hit, stand, or double down.
- The dealer must hit on 16 and stand on 17.
- Blackjack pays 3:2.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
