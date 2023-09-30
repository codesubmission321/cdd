# Copyright (c) 2016-2019 Renata Hodovan, Akos Kiss.
#
# Licensed under the BSD 3-Clause License
# <LICENSE.rst or https://opensource.org/licenses/BSD-3-Clause>.
# This file may not be copied, modified, or distributed except
# according to those terms.

class ResetableIterator:
    def __init__(self, list):
        self.list = list
        self.num = len(list)
        self.idx = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.idx >= self.num:
            raise StopIteration
        idx = self.idx
        self.idx += 1
        return self.list[idx]
    def reset(self):
      self.idx = 0


def forward(n):
    """
    Generator returning numbers from 0 to n - 1 increasing by 1.

    :param n: Upper bound of the interval.
    :return: Increasing numbers from 0 to n - 1.
    """
    l = list(range(n))
    iterator = ResetableIterator(l)
    return iterator

def backward(n):
    """
    Generator returning numbers from n - 1 to 0 decreasing by 1.

    :param n: Upper bound of the interval.
    :return: Decreasing numbers from n - 1 to 0.
    """
    l = list(range(n - 1, -1, -1))
    iterator = ResetableIterator(l)
    return iterator


def skip(n):
    """
    Do not return anything. Used to skip subset (or, less often, complement)
    checks.

    :param n: Anything. It won't ever be used. It's added only for consistency
        reasons.
    :return: None
    """
    l = list(range(0))
    iterator = ResetableIterator(l)
    return iterator


def random(n):
    """
    Returns numbers 0..n-1 in random order.

    :param n: Upper bound of the interval.
    :return: Numbers in random order from 0 to n - 1.
    """
    from random import shuffle

    lst = list(range(n))
    shuffle(lst)
    iterator = ResetableIterator(lst)
    return iterator
