import cProfile
import pstats
from io import StringIO

from board import Board
from search import SearchEngine

board = Board()
board.from_fen("rnbqkbnr/pp2ppp1/2p4p/6B1/3Pp3/2N5/PPP2PPP/R2QKBNR w KQkq - 0 5")
engine = SearchEngine(board)

profiler = cProfile.Profile()
profiler.enable()

move, score = engine.find_best_move_alphabeta(5)  # depth 5 for faster profiling

profiler.disable()

# Print to string so we can see it all
s = StringIO()
stats = pstats.Stats(profiler, stream=s)
stats.sort_stats('cumulative')
stats.print_stats(30)
print(s.getvalue())