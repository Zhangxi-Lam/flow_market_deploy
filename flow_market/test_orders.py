from .config import Config
from .orders import OrderBook
import unittest
import sys
import os


class TestOrderBook(unittest.TestCase):

    def test_get_left(self):
        order_book = OrderBook(Config())

        # combined_bids_points
        is_buy = True
        combined_points = [{'y': 20}, {'y': 13},
                           {'y': 13}, {'y': 12}, {'y': 0}]
        self.assertEqual(order_book.get_left(
            combined_points, 21, is_buy), 0)
        self.assertEqual(order_book.get_left(
            combined_points, 20, is_buy), 0)
        self.assertEqual(order_book.get_left(
            combined_points, 13, is_buy), 2)
        self.assertEqual(order_book.get_left(
            combined_points, 11, is_buy), 3)
        self.assertEqual(order_book.get_left(
            combined_points, 0, is_buy), 4)

        # combined_asks_points
        is_buy = False
        combined_points = [{'y': 0}, {'y': 12},
                           {'y': 13}, {'y': 13}, {'y': 20}]
        self.assertEqual(order_book.get_left(
            combined_points, 0, is_buy), 0)
        self.assertEqual(order_book.get_left(
            combined_points, 11, is_buy), 0)
        self.assertEqual(order_book.get_left(
            combined_points, 13, is_buy), 3)
        self.assertEqual(order_book.get_left(
            combined_points, 20, is_buy), 4)
        self.assertEqual(order_book.get_left(
            combined_points, 21, is_buy), 4)

    def test_get_rate(self):
        order_book = OrderBook(Config())

        # Buy order
        p1, p2 = {'y': 10, 'x': 0}, {'y': 4, 'x': 3}
        self.assertEqual(order_book.get_rate(10, p1, p2), 0)
        self.assertEqual(order_book.get_rate(8, p1, p2), 1)
        self.assertEqual(order_book.get_rate(6, p1, p2), 2)
        self.assertEqual(order_book.get_rate(4, p1, p2), 3)

        p1, p2 = {'y': 18, 'x': 2}, {'y': 4, 'x': 4}
        self.assertEqual(order_book.get_rate(18, p1, p2), 2)
        self.assertEqual(order_book.get_rate(11, p1, p2), 3)
        self.assertEqual(order_book.get_rate(4, p1, p2), 4)

        # Sell order
        p1, p2 = {'y': 2, 'x': 2}, {'y': 17, 'x': 5}
        self.assertEqual(order_book.get_rate(2, p1, p2), 2)
        self.assertEqual(order_book.get_rate(7, p1, p2), 3)
        self.assertEqual(order_book.get_rate(12, p1, p2), 4)
        self.assertEqual(order_book.get_rate(17, p1, p2), 5)


if __name__ == '__main__':
    unittest.main()
