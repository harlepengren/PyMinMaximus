# PyMinMaximus Chess Engine

A chess engine built from scratch in Python for learning and teaching the fundamentals of chess programming, game AI, and machine learning.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Project Mission

PyMinMaximus is designed to be both a functional chess engine and an educational resource. Rather than using external chess libraries, nearly everything is implemented from scratch to provide clear insights into how chess engines work under the hood. This makes it ideal for:

- **Learning chess programming fundamentals**: Move generation, board representation, and game state management
- **Understanding game AI algorithms**: Minimax, alpha-beta pruning, iterative deepening, and transposition tables
- **Building tournament-ready engines (coming soon)**: UCI protocol implementation and compatibility with chess GUIs

## 🚀 Features

### Core Engine
- **Custom board representation** with efficient piece encoding
- **Complete move generation** including special moves (castling, en passant, promotions)
- **Legal move validation** with check detection
- **FEN support** for position import/export

### Search & Evaluation
- **Minimax search** with alpha-beta pruning
- **Iterative deepening** for better time management
- **Transposition tables** for position caching
- **Move ordering** (MVV-LVA) for improved pruning
- **Sophisticated evaluation function** including:
  - Material counting with piece values
  - Piece-square tables for positional understanding
  - Pawn structure analysis (passed pawns, doubled pawns, isolated pawns)
  - King safety evaluation
  - Bishop pair bonus
  - Endgame vs middlegame phase detection

### Advanced Features
- **Custom Zobrist hashing** implementation for fast position recognition
- **Polyglot opening book** integration
- **Endgame tablebases** (King + Rook vs King implemented via retrograde analysis)
- **UCI protocol** support for tournament play and GUI compatibility

## 📊 Estimated Strength

Current engine: **~1400-1600 ELO**

The engine is competitive at intermediate levels and continues to improve through ongoing development.

## 🛠️ Installation

### Prerequisites
```bash
# Python 3.8 or higher required
python --version
```

### Basic Installation
```bash
# Clone the repository
git clone https://github.com/harlepengren/PyMinMaximus.git
cd PyMinMaximus

# No additional dependencies for core engine
python main.py
```

## 🎮 Usage

### Playing Against the Engine
```python
from board import Board
from search import SearchEngine

# Create a new game
board = Board()
engine = SearchEngine(board)

# Find best move (depth 5)
best_move, score = engine.find_best_move_alphabeta(5)
print(f"Best move: {best_move} (evaluation: {score})")

# Make the move
board.make_move(best_move)
print(board)
```

### Iterative Deepening Search
```python
# Search with time control
best_move, score = engine.iterative_deepening(
    max_depth=10,
    time_limit=5.0  # 5 seconds
)
```

### Opening Books
```python
from opening_book import OpeningBook

book = OpeningBook('path/to/book.bin')
book_move = book.get_book_move(board)
if book_move:
    board.make_move(book_move)
```

### Endgame Tablebases
```python
from tablebase import KRKTablebase

tb = KRKTablebase()
result = tb.probe(white_king_pos, white_rook_pos, black_king_pos, white_to_move)
# Returns: (result_type, distance_to_mate)
```

## 📚 Educational Resources

Comprehensive tutorials are available at [harlepengren.com/pyminmaximus](https://www.harlepengren.com/pyminmaximus), covering:

### Beginner Topics
- Chess board representation and piece encoding
- Move generation algorithms
- Basic minimax search
- Position evaluation fundamentals

### Intermediate Topics
- Alpha-beta pruning optimization
- Transposition tables and hashing
- Move ordering strategies
- Opening book integration
- UCI protocol implementation

### Advanced Topics
- Zobrist hashing from scratch
- Endgame tablebase generation

Each tutorial includes detailed explanations, code walkthroughs, and practical examples.

## 🧪 Testing

```bash
# Run all tests
python -m unittest discover tests

# Run specific test module
python -m unittest tests.test_board
python -m unittest tests.test_search
```

## 🎯 Development Roadmap

### Current Focus
- [x] Core engine with alpha-beta search
- [x] Custom Zobrist hashing
- [x] Opening book integration
- [x] KRK endgame tablebase

### Future Enhancements
- [ ] Additional endgame tablebases (KQK, KBNK, etc.)
- [ ] Null move pruning
- [ ] Late move reductions
- [ ] Aspiration windows
- [ ] Principal variation search
- [ ] Multi-threaded search (Lazy SMP)
- [ ] Time management improvements
- [ ] AlphaZero-style training pipeline
- [] Neural network evaluation (supervised learning)
- [ ] Self-play reinforcement learning
- [ ] MCTS integration with neural networks

## 🤝 Contributing

Contributions are welcome! Whether you're fixing bugs, adding features, or improving documentation, please feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📖 Learning Philosophy

PyMinMaximus emphasizes understanding over performance. While it may not be the fastest engine, every component is:
- **Built from scratch** to reveal underlying algorithms
- **Well-documented** with clear explanations
- **Pedagogically structured** to progress from simple to complex
- **Practically useful** as a foundation for tournament-level engines

The goal is to demystify chess engine development and make it accessible to programmers at all levels.

## 🔍 Technical Highlights

### Board Representation
Uses a bitboard-style encoding where pieces are stored as integers:
- Lower 3 bits: piece type (pawn, knight, bishop, rook, queen, king)
- Upper bits: color (white/black)
- Efficient for move generation and position manipulation

### Search Optimization
- **Alpha-beta pruning**: Reduces search tree by up to 90%
- **Transposition tables**: Caches evaluated positions (64MB default)
- **Move ordering**: MVV-LVA captures first for better cutoffs
- **Iterative deepening**: Progressively deeper searches with time management

### Evaluation Components
Combines multiple factors with careful tuning:
- Material: Standard piece values (P=100, N=320, B=330, R=500, Q=900)
- Position: Piece-square tables encourage strong piece placement
- Pawn structure: Rewards passed pawns, penalizes weaknesses
- King safety: Evaluates pawn shield and castling
- Phase awareness: Tapered evaluation for smooth middlegame-to-endgame transitions


## 🎓 Educational Use Cases

Perfect for:
- Computer science courses on game AI
- Self-directed learning of chess programming
- Understanding classical vs neural network approaches
- Preparing for chess programming competitions
- Building custom chess variants

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Chess programming community at [talkchess.com](http://talkchess.com)
- [Chess Programming Wiki](https://www.chessprogramming.org/) for algorithms and techniques
- Polyglot opening book format specification
- All contributors and users of PyMinMaximus

## 📧 Contact

Harlepengren - [@harlepengren](https://github.com/harlepengren)

Project Link: [https://github.com/harlepengren/PyMinMaximus](https://github.com/harlepengren/PyMinMaximus)

Tutorials: [https://www.harlepengren.com/pyminmaximus](https://www.harlepengren.com/pyminmaximus)

---

**Note**: This is an educational project. For maximum-strength chess play, consider engines like Stockfish, Python Chess, Leela Chess Zero, or Komodo. PyMinMaximus prioritizes learning and transparency over raw playing strength.