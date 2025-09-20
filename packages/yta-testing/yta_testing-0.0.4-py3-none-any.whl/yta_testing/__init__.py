"""
The Youtube Autonomous Testing Module.
"""
import os
import pytest


TEST_FILES_PATH = 'test_files'
"""
The relative path to the test files
folder. This is the one we should use
in all our projects.
"""

def assert_exception_is_raised(
    function: callable,
    exception_type: any = Exception
):
    """
    Call this method providing some code defined
    as a function to validate that it is raising
    an exception when called (send the function,
    not the call).

    The 'exception_type' can be an Exception, a
    TypeError, a ValueError, etc.

    Define `def f(): return 1 / 0` and call
    `check_exception_is_raised(f)` to validate
    it is working.
    """
    with pytest.raises(exception_type) as e_info:
        function()

def float_approx_to_compare(float):
    """
    Compare float values with 
    approximation due to the decimal
    differences we can have.

    Then, you can compare floats by
    using:

    - `assert fa == float_approx_to_compare(fb)`
    """
    return pytest.approx(float, rel = 1e-5, abs = 1e-8)

class TestFilesHandler:
    """
    Class to easily handle the files we
    create when testing the projects.
    
    This class must be instantiated before
    the tests are executed, and the 
    '.delete_new_files()' method must be
    called when all the tests have finished.
    """

    @property
    def files(
        self
    ) -> list[str]:
        """
        The files that are currently in the
        'test_files' folder.
        """
        return set(os.listdir(self._test_files_path))

    def __init__(
        self,
        test_files_path: str = TEST_FILES_PATH
    ):
        self._test_files_path: str = test_files_path
        """
        The relative path to the test files
        folder.
        """
        self._initial_files: list[str] = self.files
        """
        The files that were available when the
        class was instantiated (before executing
        the tests).
        """

    def delete_new_files(
        self
    ) -> list[str]:
        """
        Delete all the new files found and return
        a list containing the names of the files
        that have been deleted.
        """
        files_removed = []

        for f in self.files - self._initial_files:
            path = os.path.join(self._test_files_path, f)
            if os.path.isfile(path):
                os.remove(path)
                files_removed.append(path)

        return files_removed