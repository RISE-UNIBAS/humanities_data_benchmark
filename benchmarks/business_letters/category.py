""" category.py
===============
Category class. """

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Category:
    """ A category to be scored.

    :param used: whether the category is used, defaults to False
    :param tp: the number of true positives, defaults to 0
    :param fp: the number of false positives, defaults to 0
    :param fn: the number of false negatives, defaults to 0
    """

    used: bool = False
    tp: int = 0
    fp: int = 0
    fn: int = 0

    def get_precision(self) -> float:
        """ Get the precision. """

        try:
            return self.tp / (self.tp + self.fp)
        except ZeroDivisionError:
            return 0.0

    def get_recall(self) -> float:
        """ Get the recall. """

        try:
            return self.tp / (self.tp + self.fn)
        except ZeroDivisionError:
            return 0.0

    def get_f1(self) -> float:
        """ Get the F1 score. """

        precision = self.get_precision()
        recall = self.get_recall()
        try:
            return 2 * (precision * recall) / (precision + recall)
        except ZeroDivisionError:
            return 0.0

