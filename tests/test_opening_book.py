import unittest
from opening_book import OpeningBook
from board import Board

class TestOpeningBook(unittest.TestCase):
    def test_opening_book(self):
        book = OpeningBook('books/kasparov.bin')
        self.assertIsNotNone(book)

        board = Board()
        self.assertTrue(book.is_in_book())

        self.assertTrue(len(book.get_book_moves_info(board)) == 3)

if __name__ == "__main__":
    unittest.main()