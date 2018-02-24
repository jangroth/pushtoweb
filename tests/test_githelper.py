import tempfile
import unittest

import os

from code.cloneintobucket import GitHelper


class GitHelperTest(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp('', 'test_')

    def test_should_install_local_git(self):
        git = self._get_Git()

        self.assertIsNotNone(os.environ['GIT_EXEC_PATH'])
        self.assertIsNotNone(os.environ['GIT_TEMPLATE_DIR'])

    # def test_should_run_local_git_command(self):
    #     git = self._get_Git()
    #
    #     git_version = git.run_command('--version')
    #
    #     print(git_version)
    #     self.assertTrue(git_version.find('2.4.3') > 0)


    def _get_Git(self):
        git = GitHelper(self.temp_dir)
        git.GIT_BINARY_TAR = os.path.join(os.path.dirname(__file__), '..' , 'code' , git.GIT_BINARY_TAR)
        git.install()
        return git