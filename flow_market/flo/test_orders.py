from .config import Config
from .orders import OrderBook, Point
import unittest
import sys
import os


class TestOrderBook(unittest.TestCase):

    def test_get_y_left(self):
        order_book = OrderBook(Config())

        # combined_bids_points
        is_buy = True
        combined_points = [Point(0, 20), Point(
            0, 13), Point(0, 13), Point(0, 12), Point(0, 0)]
        self.assertEqual(order_book.get_y_left(
            combined_points, 2100, is_buy), 0)
        self.assertEqual(order_book.get_y_left(
            combined_points, 2000, is_buy), 0)
        self.assertEqual(order_book.get_y_left(
            combined_points, 1300, is_buy), 2)
        self.assertEqual(order_book.get_y_left(
            combined_points, 1100, is_buy), 3)
        self.assertEqual(order_book.get_y_left(
            combined_points, 0, is_buy), 4)

        # combined_asks_points
        is_buy = False
        combined_points = [Point(0, 0), Point(
            0, 12), Point(0, 13), Point(0, 13), Point(0, 20)]
        self.assertEqual(order_book.get_y_left(
            combined_points, 0, is_buy), 0)
        self.assertEqual(order_book.get_y_left(
            combined_points, 1100, is_buy), 0)
        self.assertEqual(order_book.get_y_left(
            combined_points, 1300, is_buy), 3)
        self.assertEqual(order_book.get_y_left(
            combined_points, 2000, is_buy), 4)
        self.assertEqual(order_book.get_y_left(
            combined_points, 2100, is_buy), 4)

    def test_get_x(self):
        order_book = OrderBook(Config())

        # Buy order
        p1, p2 = Point(2, 18), Point(4, 4)
        self.assertEqual(order_book.get_x(1800, p1, p2), 2)
        self.assertEqual(order_book.get_x(1100, p1, p2), 3)
        self.assertEqual(order_book.get_x(400, p1, p2), 4)

        p1, p2 = Point(2, 18), Point(2, 0)
        self.assertEqual(order_book.get_x(1800, p1, p2), 2)
        self.assertEqual(order_book.get_x(1100, p1, p2), 2)
        self.assertEqual(order_book.get_x(400, p1, p2), 2)

        # Sell order
        p1, p2 = Point(2, 2), Point(5, 17)
        self.assertEqual(order_book.get_x(200, p1, p2), 2)
        self.assertEqual(order_book.get_x(700, p1, p2), 3)
        self.assertEqual(order_book.get_x(1200, p1, p2), 4)
        self.assertEqual(order_book.get_x(1700, p1, p2), 5)

    def test_intersect_left(self):
        order_book = OrderBook(Config())
        order_book.combined_bids_points = [
            Point(0, 20),
            Point(0, 16),
            Point(2, 4),
            Point(2, 0)]
        order_book.combined_asks_points = [
            Point(0, 0),
            Point(0, 2),
            Point(2, 18),
            Point(2, 20)]

        y_cents = order_book.get_best_bid_in_cents()
        self.assertEqual(y_cents, 1000)


if __name__ == '__main__':
    unittest.main()
