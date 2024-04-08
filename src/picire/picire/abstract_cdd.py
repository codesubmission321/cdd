# Copyright (c) 2016-2020 Renata Hodovan, Akos Kiss.
#
# Licensed under the BSD 3-Clause License
# <LICENSE.rst or https://opensource.org/licenses/BSD-3-Clause>.
# This file may not be copied, modified, or distributed except
# according to those terms.

import logging
import collections
import time
import math
import sys
import copy
from . import utils
from datetime import datetime

logger = logging.getLogger(__name__)


class AbstractCDD(object):
    """
    Abstract super-class of the CDD class.
    """

    # Test outcomes.
    PASS = 'PASS'
    FAIL = 'FAIL'

    def __init__(self, test, split, id_prefix=(), other_config={}):
        self._test = test
        self._split = split
        self._id_prefix = id_prefix
        self.init_probability = other_config["init_probability"]
        self.dd = other_config["dd"]
        self.threshold = 0.8

    def __call__(self, config):
        
        tstart = time.time()
        self.original_config = config[:]

        # initialize based on the specificed sample startegy
        if (self.dd == "cdd"):
            # initialize counters
            self.counters = [0 for _ in range(len(config))]
            self.sample = self.sample_by_counter
            self.update_when_fail = self.update_when_fail_cdd
            self.update_when_success = self.update_when_success_cdd
            self._test_done = self._test_done_cdd

        elif (self.dd == "probdd"):
            # initialize probabilities
            self.probabilities = [self.init_probability for _ in range(len(config))]
            self.sample = self.sample_by_probability
            self.update_when_fail = self.update_when_fail_probdd
            self.update_when_success = self.update_when_success_probdd
            self._test_done = self._test_done_probdd

        else:
            raise ValueError("dd should be either cdd or probdd")

        # initialize current best config idx, all true
        self.current_best_config_idx = [True for _ in range(len(config))]
        
        run = 0
        while not self._test_done():
            logger.info('Run #%d', run)
            logger.info('\tConfig size: %d', self.get_current_config_size())
            
            # select a subsequence for testing
            config_idx_to_delete = self.sample()
            log_to_print = utils.generate_log(config_idx_to_delete, "Try deleting", print_idx=True, threshold=30)
            logger.info(log_to_print)
            config_log_id = ('r%d' % run, )

            outcome = self._test_config(config_idx_to_delete, config_log_id)
            # FAIL means current variant cannot satisify the property
            
            # if the subset cannot be deleted
            if (outcome == self.FAIL):
                self.update_when_fail(config_idx_to_delete)
            
            # if the subset can be deleted
            else:
                self.update_when_success(config_idx_to_delete)
                log_to_print = utils.generate_log(config_idx_to_delete, "Deleted", print_idx=True, threshold=30)
                logger.info(log_to_print)
            
            run += 1

        logger.info("Final size: %d/%d" % (self.get_current_config_size(), len(config)))
        logger.info("Execution time at this level: %f s" % (time.time() - tstart))
        return self.map_idx_to_config(self.current_best_config_idx)
    
    def get_current_config_size(self):
        return sum(self.current_best_config_idx)

    def _processElementToPreserve(toBePreserve):
        raise NotImplementedError()

    def _process(self, config, outcome):
        raise NotImplementedError()
    
    # directly compute the size of next subset based on the counter
    def compute_size(self, counter):
        size = round(-1 / math.log(1 - self.init_probability, math.e))
        i = 0
        while i < counter:
            logger.info("i=%d, counter=%d, size=%d" % (i, counter, size))
            size = math.floor(size * (1 - pow(math.e, -1)))
            i = i + 1
        size = min(size, len(self.counters))
        size = max(size, 1)
        return size

    # increase all counters by 1
    def increase_all_counters(self):
        for idx in range(len(self.counters)):
            if (self.counters[idx] != -1):
                self.counters[idx] = self.counters[idx] + 1

    # find out the minimal counter among all available elements
    def find_min_counter(self):
        current_min = sys.maxsize
        for counter in self.counters:
            if (counter != -1 and current_min > counter):
                current_min = counter
        return current_min
    
    # how cdd compute the next subset to delete
    def sample_by_counter(self):
        
        # filter out those removed elements (counter is -1)
        available_idx_with_counter = [(idx, counter) for idx, counter in enumerate(self.counters) if counter != -1]

        # sort idx by counter
        sorted_available_idx_with_counter = sorted(available_idx_with_counter, key=lambda x: x[1])

        # extract sorted idx
        sorted_available_idx = [idx for idx, _ in sorted_available_idx_with_counter]

        counter_min = self.find_min_counter()
        current_size = self.compute_size(counter_min)
        current_config_size = self.get_current_config_size()
        
        while current_size >= current_config_size:
            self.increase_all_counters()
            counter_min = self.find_min_counter()
            current_size = self.compute_size(counter_min)
            if (current_size == 1):
                break

        config_idx_to_delete = sorted_available_idx[:current_size]
        logger.info("\tSelected deletion size (cdd): " + str(len(config_idx_to_delete)))
        return config_idx_to_delete
    
    # how probdd compute the next subset to delete
    def sample_by_probability(self):

        # filter out those removed elements (probability is -1)
        available_idx_with_probability = [(idx, probability) for idx, probability in enumerate(self.probabilities) if probability != -1]

        # sort idx by probability
        sorted_available_idx_with_probability = sorted(available_idx_with_probability, key=lambda x: x[1])

        # extract sorted idx
        sorted_available_idx = [idx for idx, _ in sorted_available_idx_with_probability]

        current_size = 0
        accumulated_probability = 1
        current_gain = 1
        last_gain = 0
        while current_size < len(sorted_available_idx):
            current_size = current_size + 1

            current_idx = sorted_available_idx[current_size - 1]
            accumulated_probability = accumulated_probability * (1 - self.probabilities[current_idx])

            current_gain = accumulated_probability * current_size

            # find out the size with max gain and stop
            if (current_gain < last_gain):
                break
            last_gain = current_gain

        config_idx_to_delete = sorted_available_idx[:current_size]

        logger.info("\tSelected deletion size (probdd): " + str(len(config_idx_to_delete)))
        return config_idx_to_delete

    # Given a subset failed to be deleted,
    # compute the ratio to increase the probability of each element in this subset
    def compute_ratio(self, config_idx_to_delete):
        accumulated_probability = 1
        for idx in config_idx_to_delete:
            accumulated_probability = accumulated_probability * (1 - self.probabilities[idx])

        ratio = 1 / (1 - accumulated_probability)
        return ratio

    def update_when_fail_cdd(self, config_idx_to_delete):
        for idx in config_idx_to_delete:
            self.counters[idx] = self.counters[idx] + 1
        if (len(config_idx_to_delete) == 1):
            # assign the counter to maxsize and never consider this element
            self.counters[config_idx_to_delete[0]] = -1

    def update_when_fail_probdd(self, config_idx_to_delete):
        ratio = self.compute_ratio(config_idx_to_delete)

        for idx in config_idx_to_delete:
            self.probabilities[idx] = self.probabilities[idx] * ratio
            if (self.probabilities[idx] > self.threshold):
                self.probabilities[idx] = -1

        if (len(config_idx_to_delete) == 1):
            # never consider this element
            self.probabilities[config_idx_to_delete[0]] = -1

    def update_when_success_cdd(self, config_idx_to_delete):
        for idx in config_idx_to_delete:
            self.counters[idx] = -1
            self.current_best_config_idx[idx] = False

    def update_when_success_probdd(self, config_idx_to_delete):
        for idx in config_idx_to_delete:
            self.probabilities[idx] = -1
            self.current_best_config_idx[idx] = False

    def _test_done_cdd(self):
        all_decided = True
        for counter in self.counters:
            if (counter != -1):
                all_decided = False
        if (all_decided == True):
            logger.info("Iteration needs to stop because all elements are decided.")
            return True
        else:
            return False
        
    def _test_done_probdd(self):
        all_decided = True
        for probability in self.probabilities:
            if (probability != -1):
                all_decided = False
        if (all_decided == True):
            logger.info("Iteration needs to stop because all elements are decided.")
            return True
        else:
            return False

    def map_idx_to_config(self, config_idx):
        new_config = []
        for idx, availability in enumerate(config_idx):
            if (availability == True):
                new_config.append(self.original_config[idx])
        
        return new_config

    def _test_config(self, config_idx_to_delete, config_log_id):
        config_log_id = self._id_prefix + config_log_id
        logger.debug('\t[ %s ]: test...', self._pretty_config_id(config_log_id))

        # compute new config idx
        logger.info("before deep copy")
        new_config_idx = self.current_best_config_idx[:]
        logger.info("after deep copy")
        for idx in config_idx_to_delete:
            new_config_idx[idx] = False
        logger.info("exclude elements in config_idx_to_delete")

        new_config = self.map_idx_to_config(new_config_idx)
        logger.info("after mapping")
        tstart = time.time()
        outcome = self._test(new_config, config_log_id)
        logger.info("execution time of this test: " + str(time.time() - tstart) + "s")

        logger.debug('\t[ %s ]: test = %r', self._pretty_config_id(config_log_id), outcome)

        return outcome

    @staticmethod
    def _pretty_config_id(config_id):
        return ' / '.join(str(i) for i in config_id)