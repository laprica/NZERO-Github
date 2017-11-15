"""This module is to provide a custom formatter that will enalbe logging """
"""messages in different formats with one logger."""

import logging
import time



class myFormatter(logging.Formatter):
    default_fmt = logging.Formatter(fmt='%(asctime)s.%(msecs)03d, %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    warn_fmt = logging.Formatter('%(message)s')

    def format(self, record):
        if record.levelno == logging.INFO:
            return self.default_fmt.format(record)
        else:
            return self.warn_fmt.format(record)
