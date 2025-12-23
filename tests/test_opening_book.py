import unittest
from opening_book import OpeningBook
from board import Board

class TestOpeningBook(unittest.TestCase):
    def setUp(self):
        self.book = OpeningBook('books/kasparov.bin')
        self.board = Board()

    def test_opening_book(self):
        self.assertIsNotNone(self.book)

        self.assertTrue(self.book.is_in_book(self.board))

        self.assertTrue(len(self.book.get_book_moves_info(self.board)) == 3)

    def test_get_move(self):
        move = self.book.get_book_move(self.board,1,"best")
        self.assertEqual(move,'e2e4')

if __name__ == "__main__":
    unittest.main()