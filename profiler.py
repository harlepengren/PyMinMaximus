import cProfile
import pstats

from board import Board
from search import SearchEngine

def run_profile():
    board = Board()
    board.from_fen("rnbqkbnr/pp2ppp1/2p4p/6B1/3Pp3/2N5/PPP2PPP/R2QKBNR w KQkq - 0 5")
    engine = SearchEngine(board)

    profiler = cProfile.Profile()
    profiler.enable()

    move, score = engine.find_best_move_alphabeta(6)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions