import sys
import time
from board import Board
from search import SearchEngine
from evaluation import Evaluator
from opening_book import OpeningBook
from move import Move
from constants import *
import os
import threading

class UCIHandler:
    """
    Universal Chess Interface protocol handler for PyMinMaximus.
    """
    
    def __init__(self):
        self.board = Board()
        self.evaluator = Evaluator()
        
        # Engine configuration
        self.engine_name = "PyMinMaximus"
        self.engine_version = "1.0"
        self.author = "Harlepengren"

        bookfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'books/kasparov.bin')
        
        # UCI options
        self.options = {
            'Hash': 64,  # MB for transposition table
            'OwnBook': True,  # Use opening book
            'BookFile': bookfile,
        }
        
        # Initialize components
        self.opening_book = None
        self.engine = None
        self._init_engine()
    
    def _init_engine(self):
        """Initialize the search engine with current options."""
        # Load opening book if enabled
        if self.options['OwnBook'] and self.options['BookFile']:
            try:
                self.opening_book = OpeningBook(self.options['BookFile'])
            except:
                self.opening_book = None
        
        # Create search engine
        self.engine = SearchEngine(self.board, self.evaluator, self.opening_book)
    
    def uci(self):
        """Handle 'uci' command - identify engine and options."""
        print(f"id name {self.engine_name} {self.engine_version}")
        print(f"id author {self.author}")
        
        # Report available options
        print("option name Hash type spin default 64 min 1 max 1024")
        print("option name OwnBook type check default true")
        print("option name BookFile type string default books/performance.bin")
        
        print("uciok")
        sys.stdout.flush()
    
    def isready(self):
        """Handle 'isready' command - confirm ready state."""
        print("readyok")
        sys.stdout.flush()
    
    def ucinewgame(self):
        """Handle 'ucinewgame' command - reset for new game."""
        self.board = Board()
        self._init_engine()
        self.engine.tt.table.clear()  # Clear transposition table
    
    def position(self, args):
        """
        Handle 'position' command - set up position.
        
        Format: position [fen <fenstring> | startpos] moves <move1> <move2> ...
        """
        # Reset to starting position or FEN
        if args[0] == 'startpos':
            self.board = Board()
            move_start = 1
        elif args[0] == 'fen':
            # Find where moves start
            try:
                moves_idx = args.index('moves')
                fen = ' '.join(args[1:moves_idx])
                move_start = moves_idx
            except ValueError:
                # No moves, just FEN
                fen = ' '.join(args[1:])
                move_start = len(args)
            
            self.board = Board()
            self.board.from_fen(fen)
        
        # Apply moves if present
        if move_start < len(args) and args[move_start] == 'moves':
            for move_str in args[move_start + 1:]:
                move = self.board.convert_uci(move_str)
                if move:
                    self.board.make_move(move)
        
        # Update engine with new position
        self.engine.board = self.board
    
    def go(self, args):
        """
        Handle 'go' command - start searching.
        
        Supported options:
        - movetime <ms> - search for exactly this many milliseconds
        - wtime <ms> - white's remaining time
        - btime <ms> - black's remaining time
        - winc <ms> - white's increment
        - binc <ms> - black's increment
        - depth <d> - search to this depth
        - infinite - search until 'stop' command
        """
        # Parse go arguments
        movetime = None
        depth = 6  # Default depth
        wtime = btime = None
        winc = binc = 0
        increment = 500
        
        i = 0
        while i < len(args):
            if args[i] == 'movetime':
                movetime = int(args[i + 1]) / 1000  # Convert ms to seconds
                i += 2
            elif args[i] == 'depth':
                depth = int(args[i + 1])
                i += 2
            elif args[i] == 'wtime':
                wtime = int(args[i + 1])
                i += 2
            elif args[i] == 'btime':
                btime = int(args[i + 1])
                i += 2
            elif args[i] == 'winc':
                winc = int(args[i + 1])
                i += 2
            elif args[i] == 'binc':
                binc = int(args[i + 1])
                i += 2
            elif args[i] == 'infinite':
                movetime = None
                depth = 100
                i += 1
            else:
                i += 1
        
        # Calculate time allocation if using clock
        if movetime is None and wtime is not None and btime is not None:
            # Use simple time management: allocate 1/30 of remaining time + increment
            if self.board.to_move == WHITE:
                if winc is not None:
                    increment = winc
                movetime = (wtime / 1000) / 30 + (increment / 1000) * self.board.fullmove_number
            else:
                if binc is not None:
                    increment = binc
                movetime = (btime / 1000) / 30 + (increment / 1000) * self.board.fullmove_number
            
            # Ensure minimum time
            movetime = max(movetime, 0.1)
        print(f"# Starting search: depth={depth}, movetime={movetime}s")
        sys.stdout.flush()
        
        # Calculate move number for opening book
        move_number = self.board.fullmove_number
        
        # Search for best move
        self.search_thread = threading.Thread(target=self._search_with_info, args=(depth, move_number))
        self.search_thread.start()

        self.timer_thread = threading.Timer(movetime, lambda: self.engine.set_stop(True)) if movetime else None
        self.timer_thread.start() if self.timer_thread else None

    def _search_with_info(self, max_depth, move_number):
        """
        Search with UCI info output.
        """
        self.best_move = None
        self.best_score = 0
        self.engine.set_stop(False)
        
        # Check opening book first
        if self.opening_book and self.opening_book.book_enabled:
            book_move_uci = self.opening_book.get_book_move(
                self.board, move_number, selection_mode="weighted"
            )
            
            if book_move_uci:
                book_move = self.board.convert_uci(book_move_uci)
                if book_move:
                    return book_move, 0
        
        self.engine.nodes_searched = 0
        self.best_move, self.best_score = self.engine.find_best_move_alphabeta(max_depth)
        self.timer_thread.cancel() if self.timer_thread else None

        self.search_thread.join()
        
        # Report best move
        if self.best_move:
            print(f"bestmove {self.best_move}")
        else:
            # No legal moves - shouldn't happen, but be safe
            legal_moves = self.board.generate_legal_moves()
            if legal_moves:
                print(f"bestmove {legal_moves[0]}")
            else:
                print("bestmove 0000")
        
        sys.stdout.flush()
    
    def setoption(self, args):
        """Handle 'setoption' command - configure engine options."""
        # Format: setoption name <name> value <value>
        if len(args) >= 4 and args[0] == 'name' and args[2] == 'value':
            option_name = args[1]
            option_value = ' '.join(args[3:])
            
            if option_name in self.options:
                # Convert value to appropriate type
                if isinstance(self.options[option_name], int):
                    self.options[option_name] = int(option_value)
                elif isinstance(self.options[option_name], bool):
                    self.options[option_name] = option_value.lower() == 'true'
                else:
                    self.options[option_name] = option_value
                
                # Reinitialize if needed
                if option_name in ['OwnBook', 'BookFile']:
                    self._init_engine()
    
    def run(self):
        """Main UCI loop - read commands and respond."""
        while True:
            try:
                line = input().strip()
                print(f"Received command: {line}")
                
                if not line:
                    continue
                
                parts = line.split()
                command = parts[0]
                args = parts[1:]
                
                if command == 'uci':
                    self.uci()
                
                elif command == 'isready':
                    self.isready()
                
                elif command == 'ucinewgame':
                    self.ucinewgame()
                
                elif command == 'position':
                    self.position(args)
                
                elif command == 'go':
                    self.go(args)
                
                elif command == 'setoption':
                    self.setoption(args)
                
                elif command == 'quit':
                    break
                
                elif command == 'stop':
                    self.engine.set_stop(True)

                elif command == 'status':
                    print(f"Currently searching: {self.search_thread.is_alive() if self.search_thread else False}")
                    print(f"Timer active: {self.timer_thread.is_alive() if self.timer_thread else False}")
                    sys.stdout.flush()
                
            except EOFError:
                break
            except Exception as e:
                # Log errors but don't crash
                print(f"# Error: {e}", file=sys.stderr)
                sys.stderr.flush()

def _set_board_from_moves(board, moves):
    """Helper generator to set board position from a list of UCI moves. Helps
    with testing."""
    for move_str in moves:
        move = board.convert_uci(move_str)
        if move:
            board.make_move(move)
        print(f"# Applied move: {move_str}")
        yield board


def main():
    """Entry point for UCI mode."""
    handler = UCIHandler()
    handler.run()


if __name__ == "__main__":
    main()
