#!/usr/bin/env python3
r"""Maya specific Unittest and helper objects."""

import os
import tempfile
import uuid
from maya import cmds


class MayaSettings:
    r"""Store maya test exeuction settings.

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
    temp_dir: str = os.path.join(
        tempfile.gettempdir(), 'mayaunittest', str(uuid.uuid4())
    )
    delete_files: bool = True
    buffer_output: bool = True
    file_new: bool = True


class ScriptEditorState(object):
    """Provides methods to suppress and restore script editor output.

    :Tags:
        notest, print-only
    """

    # Used to restore logging states in the script editor
    suppress_results: bool | None = False
    suppress_errors: bool | None = False
    suppress_warnings: bool | None = False
    suppress_info: bool | None = False

    @classmethod
    def suppressOutput(cls):
        """Hides all script editor output.

        :Tags:
            notest, print-only
        """
        if MayaSettings.buffer_output:
            cls.suppress_results = cmds.scriptEditorInfo(q=True, suppressResults=True)
            cls.suppress_errors = cmds.scriptEditorInfo(q=True, suppressErrors=True)
            cls.suppress_warnings = cmds.scriptEditorInfo(q=True, suppressWarnings=True)
            cls.suppress_info = cmds.scriptEditorInfo(q=True, suppressInfo=True)
            cmds.scriptEditorInfo(
                e=True,
                suppressResults=True,
                suppressInfo=True,
                suppressWarnings=True,
                suppressErrors=True,
            )

    @classmethod
    def restoreOutput(cls):
        """Restores the script editor output settings to their original values.

        :Tags:
            notest, print-only
        """
        if cls.suppress_info is not None:
            cmds.scriptEditorInfo(suppressInfo=cls.suppress_info)
        if cls.suppress_warnings is not None:
            cmds.scriptEditorInfo(suppressWarnings=cls.suppress_warnings)
        if cls.suppress_errors is not None:
            cmds.scriptEditorInfo(suppressErrors=cls.suppress_errors)
        if cls.suppress_results is not None:
            cmds.scriptEditorInfo(suppressResults=cls.suppress_results)

