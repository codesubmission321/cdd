# Copyright (c) 2016-2020 Renata Hodovan, Akos Kiss.
#
# Licensed under the BSD 3-Clause License
# <LICENSE.rst or https://opensource.org/licenses/BSD-3-Clause>.
# This file may not be copied, modified, or distributed except
# according to those terms.

import logging
import random
import ast
import collections
import time
import traceback
from .outcome_cache import OutcomeCache, ContentCache
import copy
import os
import uuid
from collections import defaultdict

logger = logging.getLogger(__name__)
random_filename = "%s.txt" % uuid.uuid4()

def divide_by_two(num):
    results = []
    while num > 1:
        num = num // 2
        results.append(num)
    return results

def compute_recommended_size():
    if (not os.path.exists(random_filename)):
        return None
    size_success_counts = defaultdict(int)
    size_total_counts = defaultdict(int)

    with open(random_filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            size, state = line.strip().split(':')
            size = int(size)
            size_total_counts[size] += 1
            if state == 'success':
                size_success_counts[size] += 1
    if (len(lines) < 100):
        return None
    size_success_rates = {}
    for size, total_count in size_total_counts.items():
        success_rate = 1.0 * size_success_counts[size] / total_count
        size_success_rates[size] = success_rate

    sorted_sizes = sorted(size_success_rates.items(), key=lambda x: x[1], reverse=True)

    normalized_success_expectation = []
    total_success_expectation = sum([size * rate for size, rate in sorted_sizes])
    
    accumulated_success_expectation = 0
    selected_sizes = []
    for size, success_expectation in sorted_sizes:
        normalized_success_expectation = success_expectation / total_success_expectation
        accumulated_success_expectation += normalized_success_expectation
        selected_sizes.append(size)
        if accumulated_success_expectation >= 0.95:
            break

    return selected_sizes

def update_file(size, state):
    with open(random_filename, "a") as f:
        f.write("%d:%s\n" % (size, state))

class AbstractFastDD(object):
    """
    Abstract super-class of the parallel and non-parallel DD classes.
    """

    # Test outcomes.
    PASS = 'PASS'
    FAIL = 'FAIL'

    def __init__(self, test, split, cache=None, id_prefix=(), onepass=False):
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
        self.p = collections.OrderedDict()
        self.memory = {}
        self.testHistory = []
        self.passconfig = []
        logger.info(random_filename)

    def __call__(self, config):
        """
        Return a 1-minimal failing subset of the initial configuration.
        :param config: The initial configuration that will be reduced.
        :return: 1-minimal failing configuration.
        """
        tstart = time.time()
        self.original_config = config[:]
        self.original_config_id = list(range(len(config)))
        run = 0
        self.passconfig = self.original_config
        partition_size_list = compute_recommended_size()
        if (partition_size_list is None):
            partition_size_list = divide_by_two(len(self.passconfig))

        for partition_size in partition_size_list:
            if (partition_size > len(self.passconfig)):
                continue
            idx = 0
            while (idx + partition_size <= len(self.passconfig)):
                logger.info('Run #%d', run)
                run = run + 1
                config_id = ('r%d' % run, )
                logger.info('\tConfig size: %d' % len(self.passconfig))
                logger.info("\tSelected deletion size: %d" % partition_size)
                config2test = self.passconfig[0:idx] + self.passconfig[idx+partition_size:]
                deleted_config = self.passconfig[idx:idx+partition_size]
                self.printIdx(deleted_config, "Try deleting")
                outcome = self._test_config(config2test,config_id)
                if outcome == self.FAIL:
                    idx = idx + partition_size
                    update_file(partition_size, "fail")
                else:
                    self.printIdx(deleted_config, "Deleted")
                    self.passconfig = config2test
                    update_file(partition_size, "success")
        
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

    def _lookup_history(self, config):
        if self.memory.has_key(str(config)):
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
