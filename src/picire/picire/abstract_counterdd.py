# Copyright (c) 2016-2020 Renata Hodovan, Akos Kiss.
#
# Licensed under the BSD 3-Clause License
# <LICENSE.rst or https://opensource.org/licenses/BSD-3-Clause>.
# This file may not be copied, modified, or distributed except
# according to those terms.

import logging
import collections
import time
from .outcome_cache import OutcomeCache, ContentCache
import math
import sys
logger = logging.getLogger(__name__)


class AbstractCounterDD(object):
    """
    Abstract super-class of the parallel and non-parallel DD classes.
    """

    # Test outcomes.
    PASS = 'PASS'
    FAIL = 'FAIL'

    def __init__(self, test, split, cache=None, id_prefix=(), init_probability=0.1):
        """
        Initialise an abstract DD class. Not to be called directly, only by
        super calls in subclass initializers.
        :param test: A callable tester object.
        :param split: Splitter method to break a configuration up to n parts.
        :param cache: Cache object to use.
        :param id_prefix: Tuple to prepend to config IDs during tests.
        """
        self._test = test
        self._split = split
        self._cache = cache or OutcomeCache()
        self._id_prefix = id_prefix
        self.counter = collections.OrderedDict()
        self.init_probability = init_probability
        self.memory = {}
        self.testHistory = []
        self.passconfig = []
        self.initialCounter = 0

    def __call__(self, config):
        """
        Return a 1-minimal failing subset of the initial configuration.
        :param config: The initial configuration that will be reduced.
        :return: 1-minimal failing configuration.
        """
        
        tstart = time.time()
        self.original_config = config[:]
        self.index = 0
        self.next_size = True
        for c in config:
            self.counter[c] = self.initialCounter
        
        run = 0
        self.passconfig = config
        while not self._test_done():
            logger.info('Run #%d', run)
            logger.info('\tConfig size: %d', len(self.passconfig))
            
            # select a subsequence for testing
            deleteconfig = self.sample()

            config2test = self._minus(self.passconfig, deleteconfig)
            self.printIdx(deleteconfig, "Try deleting")
            config_id = ('r%d' % run, )

            outcome = None
            if (type(self._cache) is ContentCache):
                outcome = self._lookup_history(config2test)
            if outcome is None:
                outcome = self._test_config(config2test, config_id)
            # FAIL means current variant cannot satisify the property
            if outcome == self.FAIL:
                for key in self.counter.keys():
                    if key in deleteconfig:
                        self.counter[key] = self.counter[key] + 1
                self.testHistory.append(deleteconfig)
                if len(deleteconfig) == 1:
                    # assign the counter to maxsize and never consider this element
                    self.counter[deleteconfig[0]] = -1
            else:
                for key in self.counter.keys():
                    if key in deleteconfig:
                        self.counter[key] = -1
                # print successfully deleted idx
                self.printIdx(deleteconfig, "Deleted")
                self.passconfig = config2test
            
            run += 1

            if (type(self._cache) is ContentCache):
                self.memory[str(config2test)] = outcome
        logger.info("Final size: %d/%d" % (len(self.passconfig), len(config)))
        logger.info("Execution time at this level: %f s" % (time.time() - tstart))
        return self.passconfig

    def printIdx(self, deleteconfig, info):
        indices = []
        for item in deleteconfig:
            idx = self.original_config.index(item)
            indices.append(idx)
        indices.sort()
        logger.info("\t%s: %r" % (info, indices))

    def _processElementToPreserve(toBePreserve):
        raise NotImplementedError()

    def _process(self, config, outcome):
        raise NotImplementedError()
    
    def compute_size(self, counter):
        size = round(-1 / math.log(1 - self.init_probability, math.e))
        i = 0
        while i < counter:
            size = math.floor(size * (1 - pow(math.e, -1)))
            i = i + 1
        size = min(size, len(self.counter))
        size = max(size, 1)
        return size
    
    def count_available_element(self):
        num_available_element = 0
        for counter in self.counter.values():
            if counter is not -1:
                num_available_element = num_available_element + 1
        return num_available_element
    
    def increase_all_counters(self):
        for key in self.counter.keys():
            if self.counter[key] is not -1:
                self.counter[key] = self.counter[key] + 1

    def find_min_counter(self):
        current_min = sys.maxsize
        for key in self.counter.keys():
            if self.counter[key] is not -1 and self.counter[key] < current_min:
                current_min = self.counter[key]
        return current_min
    
    def sample(self):
        config2test = []
        self.counter = collections.OrderedDict(sorted(self.counter.items(), key=lambda item:item[1]))
        keylist = list(self.counter.keys())

        counter_min = self.find_min_counter()
        size_current = self.compute_size(counter_min)
        num_available_element = self.count_available_element()
        
        while size_current >= num_available_element:
            self.increase_all_counters()
            counter_min = self.find_min_counter()
            size_current = self.compute_size(counter_min)
            if size_current == 1:
                break

        i = 0
        for key in keylist:
            # if counter == -1, skip the element
            if self.counter[key] is -1:
                continue
            config2test.append(key)
            i = i + 1
            if i >= size_current:
                break

        logger.info("\tSelected deletion size: " + str(len(config2test)))
        return config2test

    def _test_done(self):
        all_decided = True
        for value in self.counter.values():
            if value != -1:
                all_decided = False
        if all_decided:
            logger.info("Iteration needs to stop because all elements are decided.")
            return True
        else:
            return False

    def _lookup_history(self, config):
        if str(config) in self.memory:
            return self.memory[str(config)]
        return None


    def _lookup_cache(self, config, config_id):
        """
        Perform a cache lookup if caching is enabled.
        :param config: The configuration we are looking for.
        :param config_id: The ID describing the configuration (only for debug
            message).
        :return: None if outcome is not found for config in cache or if caching
            is disabled, PASS or FAIL otherwise.
        """
        cached_result = self._cache.lookup(config)
        if cached_result is not None:
            logger.debug('\t[ %s ]: cache = %r', self._pretty_config_id(self._id_prefix + config_id), cached_result)

        return cached_result

    def _test_config(self, config, config_id):
        """
        Test a single configuration and save the result in cache.
        :param config: The current configuration to test.
        :param config_id: Unique ID that will be used to save tests to easily
            identifiable directories.
        :return: PASS or FAIL
        """
        config_id = self._id_prefix + config_id

        logger.debug('\t[ %s ]: test...', self._pretty_config_id(config_id))
        outcome = self._test(config, config_id)
        logger.debug('\t[ %s ]: test = %r', self._pretty_config_id(config_id), outcome)

        if 'assert' not in config_id:
            self._cache.add(config, outcome)

        return outcome

    @staticmethod
    def _pretty_config_id(config_id):
        """
        Create beautified identifier for the current task from the argument.
        The argument is typically a tuple in the form of ('rN', 'DM'), where N
        is the index of the current iteration, D is direction of reduce (either
        s(ubset) or c(omplement)), and M is the index of the current test in the
        iteration. Alternatively, argument can also be in the form of
        (rN, 'assert') for double checking the input at the start of an
        iteration.
        :param config_id: Config ID tuple.
        :return: Concatenating the arguments with slashes, e.g., "rN / DM".
        """
        return ' / '.join(str(i) for i in config_id)

    @staticmethod
    def _minus(c1, c2):
        """
        Return a list of all elements of C1 that are not in C2.
        """
        c2 = set(c2)
        return [c for c in c1 if c not in c2]
    
    @staticmethod
    def _aInb(c1,c2):
        for i in c1:
            if i not in c2:
                return False
        return True

    @staticmethod
    def _intersect(c1,c2):
        for i in c1:
            if i in c2:
                return True
        return False
