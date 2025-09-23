r"""unittest_cases.py

Library for handy unittest custom / inherited types, and decorators.
"""

import unittest
from functools import wraps
import logging
import sys
import os

HAS_MAYA = True
try:
    from maya import cmds
except:
    HAS_MAYA = False


class BaseTestCase(unittest.TestCase):
    r"""
    :Tags:
        notest, already-tested
    """
    stdout = sys.stdout

    def setUp(self):
        r"""Run before tests.

        Disables warning logs and below, if UTW_BLOCK_PRINTS environment set also block
        python print messages.

        :Tags:
            notest, print-only
        """
        if os.environ.get('UTW_BLOCK_PRINTS', False):
            sys.stdout = open(os.devnull, 'w')
        logging.disable(logging.WARNING)

    def tearDown(self):
        r"""Run after testss.

        Re-enable logging and get prints back (if blocked above)

        :Tags:
            notest, print-only
        """
        sys.stdout = self.stdout
        logging.disable(logging.NOTSET)

    def assertListAlmostEqual(
        self, first, second, places=5, msg=None, delta=None
    ) -> None:
        """Asserts that a list of floating point values is almost equal.

        unittest has assertAlmostEqual and assertListEqual but no assertListAlmostEqual.

        Args:
            first: `types`. First list to check.
            second: `types`. Second list to check against.
            places: `uint`. Default 5. Precision to compare `first` with `second`.
            msg: `str`. Default None. Message to pass into
              `TestCase.assertEqual` method.
            delta: `float`. Default None. Acceptable delta differente, passed
              to `TestCase.assertAlmostEqual`

        Returns:
            `None`

        :Tags:
            notest
        """
        self.assertEqual(len(first), len(second), msg)
        for a, b in zip(first, second):
            self.assertAlmostEqual(a, b, places, msg, delta)


def MISSINGTEST(func):
    r"""Decorator for functions without a test case.

    Args:
        func: `func`. Function to be decorated

    Returns:
        `func`: Decorated function.

    :Tags:
        notest, decorator.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        r"""

        :Tags:
            notest, wrapper
        """
        _=(args,kwargs)
        raise RuntimeError('MISSING EXAMPLE TEST!')

    return wrapper


if HAS_MAYA:
    from .maya_unittest import MayaSettings
    class MayaTestCase(BaseTestCase):
        r"""Base test case for Maya

        :Tags:
            notest, already-tested

        Examples::

            from maya import cmds
            from utwrite.unittest_cases import MayaTestCase
            from utwrite.maya_unittest import MayaSettings

            # Create a sample Maya test case class
            class T(MayaTestCase):
                def test_sample(self):
                    self.assertEqual(1,1)

            # Load it into a test suite
            import unittest
            suite = unittest.TestLoader().loadTestsFromTestCase(T)

            # Create a cube
            cube= cmds.polyCube()[0]
            cmds.objExists(cube)
            # Result: True #

            # Run the suite, cube is gone by cmds.file(new=1,f=1)
            unittest.TextTestRunner().run(suite)
            cmds.objExists(cube)
            # Result: False #

            # Create the cube again
            cube= cmds.polyCube()[0]
            cmds.objExists(cube)
            # Result: True #
            suite = unittest.TestLoader().loadTestsFromTestCase(T)

            # MayaSettings for no new scene between tests
            MayaSettings.file_new = False

            # Run the suite
            unittest.TextTestRunner().run(suite)

            # See cube still present
            cmds.objExists(cube)
            # Result: True #

        """
        # Disable color management, performance hit
        cmds.optionVar(stringValue=('colorManagementPolicyFileName', ''))

        @classmethod
        def tearDownClass(cls) -> None:
            r"""Call after every test finishes.

            :Tags:
                notest, already-tested
            """
            super().tearDownClass()
            if MayaSettings.file_new:
                cmds.file(new=1,f=1)

