import unittest
from unittest.mock import patch, MagicMock, call
import main

class TestSEOOptimization(unittest.TestCase):

    # Existing tests ...

    def test_check_plugins(self):
        expected_plugins = {
            "lite_speed_cache": True,
            "short_pixel": True,
            "google_site_kit": True,
            "link_whisperer": True,
        }
        active_plugins = main.check_plugins()
        self.assertEqual(active_plugins, expected_plugins)

    @patch("main.openai.Completion.create")
    def test_assess_content(self, mock_openai_create):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(text="Readability: 85\nKeyword Density: 90\nMetadata Optimization: 80")]
        mock_openai_create.return_value = mock_response
        
        content = "<html></html>"
        assessment = main.assess_content(content)
        self.assertIn("Readability", assessment)
        self.assertIn("Keyword Density", assessment)
        self.assertIn("Metadata Optimization", assessment)

    @patch("main.openai.Completion.create")
    def test_rewrite_content(self, mock_openai_create):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(text="<html>Improved Content</html>")]
        mock_openai_create.return_value = mock_response
        
        content = "<html></html>"
        new_content = main.rewrite_content(content)
        self.assertEqual(new_content, "<html>Improved Content</html>")

    @patch("main.logging.info")
    def test_log_action(self, mock_logging_info):
        message = "This is a test message"
        main.log_action(message)
        self.assertEqual(mock_logging_info.call_count, 1)
        mock_logging_info.assert_called_with(message)

    @patch("main.openai.Completion.create")
    def test_repair_code(self, mock_openai_create):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(text="repaired script content")]
        mock_openai_create.return_value = mock_response
        
        script_content = "old script content"
        repaired_script = main.repair_code(script_content)
        self.assertEqual(repaired_script, "repaired script content")


if __name__ == '__main__':
    unittest.main()