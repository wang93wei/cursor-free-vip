import unittest
from unittest import mock
import sys
import os
import platform

# Temporarily add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock winreg for non-Windows platforms before utils is imported
# This is still useful if utils.py tries to import winreg conditionally
if platform.system() != 'Windows':
    sys.modules['winreg'] = mock.MagicMock()

import utils

class TestGetUserDocumentsPathSimplified(unittest.TestCase):
    @mock.patch('platform.system', return_value="Linux")
    @mock.patch('os.path.expanduser')
    @mock.patch('os.path.isdir')
    def test_linux_success(self, mock_isdir, mock_expanduser, mock_system):
        mock_expanduser.return_value = "/home/testuser/Documents"
        mock_isdir.return_value = True
        path = utils.get_user_documents_path()
        self.assertEqual(path, "/home/testuser/Documents")
        mock_expanduser.assert_called_once_with("~/Documents")
        mock_isdir.assert_called_with("/home/testuser/Documents")

    @mock.patch('platform.system', return_value="Darwin")
    @mock.patch('os.path.expanduser')
    @mock.patch('os.path.isdir')
    def test_macos_success(self, mock_isdir, mock_expanduser, mock_system):
        mock_expanduser.return_value = "/Users/testuser/Documents"
        mock_isdir.return_value = True
        path = utils.get_user_documents_path()
        self.assertEqual(path, "/Users/testuser/Documents")
        mock_expanduser.assert_called_once_with("~/Documents")
        mock_isdir.assert_called_with("/Users/testuser/Documents")

    @mock.patch('platform.system', return_value="Linux") # Could be any OS for this check
    @mock.patch('os.path.expanduser')
    @mock.patch('os.path.isdir', return_value=False) # Simulate path is not a directory
    def test_path_not_a_directory(self, mock_isdir, mock_expanduser, mock_system):
        mock_expanduser.return_value = "/some/nonexistent/path"
        path = utils.get_user_documents_path()
        self.assertIsNone(path)
        mock_isdir.assert_called_with("/some/nonexistent/path")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
