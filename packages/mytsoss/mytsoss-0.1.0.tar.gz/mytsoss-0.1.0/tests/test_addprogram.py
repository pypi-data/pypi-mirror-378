import unittest
from unittest.mock import patch, MagicMock
from mytsoss.commands.addprogram import AddProgramCommand

class TestAddProgramCommand(unittest.TestCase):

    @patch('mytsoss.commands.addprogram.download_and_execute')
    def test_addprogram_valid_url(self, mock_download_and_execute):
        command = AddProgramCommand()
        mock_download_and_execute.return_value = True
        
        response = command.handle_command("-addprogram", "http://example.com/file.exe")
        
        self.assertTrue(response)
        mock_download_and_execute.assert_called_once_with("http://example.com/file.exe")

    @patch('mytsoss.commands.addprogram.download_and_execute')
    def test_addprogram_invalid_url(self, mock_download_and_execute):
        command = AddProgramCommand()
        mock_download_and_execute.side_effect = Exception("Invalid URL")
        
        with self.assertRaises(Exception):
            command.handle_command("-addprogram", "invalid_url")

    @patch('mytsoss.commands.addprogram.download_and_execute')
    def test_addprogram_no_url(self, mock_download_and_execute):
        command = AddProgramCommand()
        
        response = command.handle_command("-addprogram", "")
        
        self.assertFalse(response)
        mock_download_and_execute.assert_not_called()

if __name__ == '__main__':
    unittest.main()