"""
.. module:: Logger
   :synopsis: Log and store code informations on disk.

"""
import logging
import time
import sys


class Log(object):
    """Manager for logging and logfiles.

    Logger can be used to save important runtime code informations
    to disk instead of built-in function 'print'. Along with any
    print-like formatted string, the logger stores full time stamp
    and calling class name.

    The default filename of a log file is ``logs.log``. This will be
    placed in the same directory of the calling file.

    Two levels of logging are currently available:
     * INFO: to be used for general logging. Equivalent to numerical 20.
     * DEBUG: to be used for debug phase logging only. Equivalent to numerical 10.

    The level of logging will be stored on disk before the info string.

    Common usage for Log class is to make it a superclass of the class
    to log. Than the logger will be available inside self.logger attribute.

    Logger is fully integrated to the :class:`.Timer` class in order to log
    performance of a desired method or routine.

    Notes
    -----
    Unlike most of the Python logging modules, our implementation can be
    fully used inside parallelized code.

    See Also
    --------
    .Timer : Manages performance monitoring and logging.

    Examples
    --------
    >>> from prlib.array import CArray
    >>> from prlib.utils import Log

    >>> log = Log()
    >>> log.logger.info("{:}".format(CArray([1,2,3])))  # doctest: +SKIP
     .. - Log - INFO - CArray([1 2 3])

    """

    def __init__(self):
        # Initializing and setting up logger with default logging level (INFO)
        self.logger = None
        self.set_logger()

    def __getstate__(self):
        """Return Log instance before pickling."""
        state = dict(self.__dict__)
        # We now remove the store logger (will be restored after)
        del state['logger']
        return state

    def __setstate__(self, state):
        """Reset Log instance after pickling."""
        self.__dict__.update(state)
        # We now reinitialize logger
        self.set_logger()

    def _add_handler(self, formatter, handler):
        """Adds handler and specifies a formatter."""
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def set_logger(self, debug=False):
        """Prepare the logger and set the logging level.

        Two levels of logging are currently available:
         * INFO: to be used for general logging. Equivalent to numerical 20.
         * DEBUG: to be used for debug phase logging only. Equivalent to numerical 10.

        The level of logging will be stored on disk before the info string.

        Parameters
        ----------
        debug : bool, optional
            If True, logging level will be set to DEBUG, otherwise to INFO.

        Returns
        -------
        logger : Log
            Logger set up using input logging level.

        """
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(type(self).__name__)

        # Make sure no handler is saved when set_logger is called
        self.logger.handlers = []
        handler = logging.FileHandler('logs.log')
        self._add_handler(formatter, handler)
        handler = logging.StreamHandler(sys.stdout)
        self._add_handler(formatter, handler)

        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        return self

    def timed(self):
        """Starts a timed codeblock.

        Returns an instance of context manager :class:`.Timer`.
        Performance data will be stored inside the calling logger.

        Examples
        --------
        >>> from prlib.array import CArray
        >>> from prlib.utils import Log

        >>> log = Log()
        >>> with log.timed():
        ...    ** wonderful code **  # doctest: +SKIP

        """
        return Timer(self)


class Timer(object):
    """Context manager for performance logging

    The code inside the specific context will be timed and
    performance data printed and/or logged.

    This class fully integrates with :class:`.Log` in order to
    store to disk performance data. When no logger is specified,
    data is printed on the console output.

    Times are always stored in milliseconds (ms).

    Parameters
    ----------
    log : Log or None, optional
        Instance of :class:`.Log` class to be used as
        performance logger. If a logger is specified,
        timer data will not be printed on console.

    See Also
    --------
    .Log : Log and store runtime informations on disk.

    Examples
    --------
    >>> from prlib.array import CArray
    >>> from prlib.utils import Timer

    >>> with Timer() as t:
    ...     a = CArray([1,2,3])  # doctest: +SKIP
    Elapsed time: 0.0820159912109 ms

    >>> from prlib.utils import Log
    >>> with Timer(Log()) as t:
    ...     a = CArray([1,2,3])  # doctest: +SKIP
     .. - Log - INFO - Entering timed block...
     .. - Log - INFO - Elapsed time: 0.725030899048 ms

    """

    def __init__(self, log=None):
        # We store a shallow copy of the input logger
        self.logger = None if log is None else log.logger
        # Getting logging level for input logger
        self.log_level = None if self.logger is None else self.logger.getEffectiveLevel()

    @property
    def step(self):
        """Return time elapsed from timer start (milliseconds)."""
        return (time.time() - self.start) * 1000  # Interval as milliseconds

    def __enter__(self):
        """Called upon before entering a 'with' block."""
        self.start = time.time()
        # Logging timer start if needed
        if self.logger is not None:
            self.logger.log(self.log_level, "Entering timed block...")
        return self  # This allow using of 'as' statement (e.g.: with self.timer() as t)

    def __exit__(self, type, value, traceback):
        """Called upon before exit from 'with' block."""
        self.end = time.time()
        self.interval = (self.end - self.start) * 1000  # Interval as milliseconds
        # Logging timer end if needed
        if self.logger is not None:
            self.logger.log(self.log_level, "Elapsed time: " + str(self.interval) + " ms")
        else:
            print("Elapsed time: {:} ms".format(self.interval))


# # # # # # # # # # # # # # # # # #
# # # # # # # UNITTESTS # # # # # #
import unittest


class TestLogging(unittest.TestCase, Log):

    def setUp(self):
        # Setting a testing logger
        self.set_logger()

    def test_timed_nologging(self):

        # Calling class Timer directly
        timer = Timer()  # Does nothing... Use as context manager!

        # Test for predefined interval
        with timer as t:
            time.sleep(2)
            self.assertGreaterEqual(t.step, 2000)
        self.assertGreaterEqual(t.interval, 2000)

    def test_timed_logging(self):

        from prlib.array import CArray

        timer = self.timed()  # Does nothing... Use as context manager!

        # Test for predefined interval
        with timer as t:
            time.sleep(2)
            self.assertGreaterEqual(t.step, 2000)
        self.assertGreaterEqual(t.interval, 2000)

        # Testing logging of method run time
        with self.timed():
            a = CArray.arange(-5, 100, 0.1).transpose()
            a.sort()

        # Test for predefined interval with error
        with self.assertRaises(TypeError):
            with self.timed() as t:
                time.sleep('test')
        self.logger.info("Interval " + str(t.interval) + " should have been logged anyway")

        # Testing timing with logging as DEBUG level
        self.set_logger(debug=True)
        with self.timed() as t:
            a = CArray.arange(-5, 100, 0.1).transpose()
            a.sort()
            self.assertEqual(t.log_level, logging.DEBUG)
        self.set_logger()  # Going back to INFO level


if __name__ == '__main__':
    unittest.main()
