# Copyright (c) 2016-2020 Renata Hodovan, Akos Kiss.
#
# Licensed under the BSD 3-Clause License
# <LICENSE.rst or https://opensource.org/licenses/BSD-3-Clause>.
# This file may not be copied, modified, or distributed except
# according to those terms.

import itertools
import logging
import random
import time

from .outcome_cache import OutcomeCache

logger = logging.getLogger(__name__)

def split_list(input_list, chunk_size):
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]

def flatten(l):
    return [item for sublist in l for item in sublist]

class AbstractDD(object):
    """
    Abstract super-class of the parallel and non-parallel DD classes.
    """

    # Test outcomes.
    PASS = 'PASS'
    FAIL = 'FAIL'

    def __init__(self, test, split, cache=None, id_prefix=(), other_config={}):
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
        self.onepass = other_config["onepass"]
        self.start_from_n = other_config["start_from_n"]
        self.delete_history = []


    def __call__(self, config):
        """
        Return a 1-minimal failing subset of the initial configuration.

        :param config: The initial configuration that will be reduced.
        :return: 1-minimal failing configuration.
        """
        #print("enter picire/abstract_dd.py:__call__()")
        self.original_config = config[:]
        self.original_config_size = len(self.original_config)
        self.original_config_idx = list(range(self.original_config_size))
        current_config_idx = self.original_config_idx[:]
        if (self.start_from_n):
            subsets = split_list(self.original_config_idx, self.start_from_n)
        else:
            subsets = [self.original_config_idx]
        complement_offset = 0

        for run in itertools.count():
            logger.info('Run #%d', run)
            logger.info('\tConfig size: %d', len(current_config_idx))
            #assert self._test_config(config, ('r%d' % run, 'assert')) == self.FAIL

            # Minimization ends if the configuration is already reduced to a single unit.
            if len(current_config_idx) < 2:
                logger.info('\tGranularity: %d', len(subsets))
                logger.debug('\tConfig: %r', subsets)
                logger.info("\t Final result: %d/%d" % (len(flatten(subsets)), self.original_config_size))
                logger.info('\tDone')
                return self.idx2config(current_config_idx)

            if len(subsets) < 2:
                assert len(subsets) == 1
                subsets = self._split(subsets)

            logger.info('\tGranularity: %d', len(subsets))
            logger.debug('\tConfig: %r', subsets)

            next_subsets, complement_offset = self._reduce_config(run, subsets, complement_offset)

            if next_subsets is not None:
                # Interesting configuration is found, start new iteration.
                subsets = next_subsets
                current_config_idx = [c for s in subsets for c in s]

                #logger.info('\tReduced')

            elif len(subsets) < len(current_config_idx):
                # No interesting configuration is found but it is still not the finest splitting, start new iteration.
                next_subsets = self._split(subsets)
                complement_offset = (complement_offset * len(next_subsets)) / len(subsets)
                subsets = next_subsets

                logger.info('\tIncreased granularity')

            else:
                # Minimization ends if no interesting configuration was found by the finest splitting.
                logger.info("\t Final result: %d/%d" % (len(flatten(subsets)), len(self.original_config)))
                logger.info('\tDone')
                return self.idx2config(current_config_idx)

    def _reduce_config(self, run, subsets, complement_offset):
        """
        Perform the reduce task of ddmin. To be overridden by subclasses.

        :param run: The index of the current iteration.
        :param subsets: List of sets that the current configuration is split to.
        :param complement_offset: A compensation offset needed to calculate the
            index of the first unchecked complement (optimization purpose only).
        :return: Tuple: (list of subsets composing the failing config or None,
            next complement_offset).
        """
        raise NotImplementedError()

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

    def _test_config(self, config_idx, config_unique_id):
        """
        Test a single configuration and save the result in cache.

        :param config: The current configuration to test.
        :param config_id: Unique ID that will be used to save tests to easily
            identifiable directories.
        :return: PASS or FAIL
        """
        config_unique_id = self._id_prefix + config_unique_id

        logger.debug('\t[ %s ]: test...', self._pretty_config_id(config_unique_id))
        tstart = time.time()
        config = self.idx2config(config_idx)
        outcome = self._test(config, config_unique_id)
        logger.info("execution time of this test: " + str(time.time() - tstart) + "s")
        logger.debug('\t[ %s ]: test = %r', self._pretty_config_id(config_unique_id), outcome)

        if 'assert' not in config_unique_id:
            self._cache.add(config_idx, outcome)

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
    
    def idx2config(self, indices):
        new_indices = indices[:]
        new_indices.sort()
        config = []
        for i in indices:
            config.append(self.original_config[i])
        return config
