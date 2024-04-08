# Copyright (c) 2016-2021 Renata Hodovan, Akos Kiss.
#
# Licensed under the BSD 3-Clause License
# <LICENSE.rst or https://opensource.org/licenses/BSD-3-Clause>.
# This file may not be copied, modified, or distributed except
# according to those terms.

import logging

from . import config_iterators
from . import config_splitters
from .abstract_cdd import AbstractCDD

logger = logging.getLogger(__name__)


class CDD(AbstractCDD):

    def __init__(self, test, cache=None, id_prefix=(),
                 split=config_splitters.zeller,
                 subset_first=True, subset_iterator=config_iterators.forward,
                 complement_iterator=config_iterators.forward, **other_config):
        """
        Initialize a ProbDD object.
        :param test: A callable tester object.
        :param cache: Cache object to use.
        :param id_prefix: Tuple to prepend to config IDs during tests.
        :param split: Splitter method to break a configuration up to n parts.
        :param subset_first: Boolean value denoting whether the reduce has to
            start with the subset-based approach or not.
        :param subset_iterator: Reference to a generator function that provides
            config indices in an arbitrary order.
        :param complement_iterator: Reference to a generator function that
            provides config indices in an arbitrary order.
        """
        AbstractCDD.__init__(self, test, split, id_prefix=id_prefix, other_config=other_config)

    def _processElementToPreserve(self,toBePreserve):
        tmp = []
        for history in self.testHistory:
            if self._intersect(toBePreserve, history):
                cha = self._minus(history, toBePreserve)
            else:
                tmp.append(history)
        self.testHistory = tmp
        for elm in toBePreserve:
            self.counter[elm] = -1

    def _process(self,config,outcome):
        tmp=[]
        toBePreserve=[]
        if outcome==self.PASS:
            for history in self.testHistory:
                if self._intersect(config,history):
                    cha=self._minus(history,config)
                    if len(cha)==1:
                        if not(cha[0] in toBePreserve):
                            toBePreserve.append(cha[0])
                    else:
                        tmp.append(cha)
                else:
                    tmp.append(history)
            self.testHistory=tmp
            self._processElementToPreserve(toBePreserve)
        elif outcome==self.FAIL:
            self._processElementToPreserve(config)
