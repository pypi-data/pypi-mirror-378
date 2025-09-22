import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from sfn_blueprint import SFNStreamlitView
class TestSFNStreamlitView(unittest.TestCase):

    @patch('streamlit.title')
    def test_display_title(self, mock_title):
        view = SFNStreamlitView(title="Test Title")
        view.display_title()
        mock_title.assert_called_once_with("Test Title")

    @patch('streamlit.info')
    @patch('streamlit.success')
    @patch('streamlit.error')
    @patch('streamlit.warning')
    @patch('streamlit.write')
    def test_show_message(self, mock_write, mock_warning, mock_error, mock_success, mock_info):
        view = SFNStreamlitView()

        # Test info message
        view.show_message("Info Message", message_type="info")
        mock_info.assert_called_once_with("Info Message")

        # Test success message
        view.show_message("Success Message", message_type="success")
        mock_success.assert_called_once_with("Success Message")

        # Test error message
        view.show_message("Error Message", message_type="error")
        mock_error.assert_called_once_with("Error Message")

        # Test warning message
        view.show_message("Warning Message", message_type="warning")
        mock_warning.assert_called_once_with("Warning Message")

    @patch('streamlit.header')
    def test_display_header(self, mock_header):
        view = SFNStreamlitView()
        view.display_header("Header Text")
        mock_header.assert_called_once_with("Header Text")

    @patch('streamlit.subheader')
    def test_display_subheader(self, mock_subheader):
        view = SFNStreamlitView()
        view.display_subheader("Subheader Text")
        mock_subheader.assert_called_once_with("Subheader Text")

    @patch('streamlit.markdown')
    def test_display_markdown(self, mock_markdown):
        view = SFNStreamlitView()
        view.display_markdown("Markdown Text")
        mock_markdown.assert_called_once_with("Markdown Text")

    @patch('streamlit.columns')
    def test_create_columns(self, mock_columns):
        view = SFNStreamlitView()
        view.create_columns(3)
        mock_columns.assert_called_once_with(3)

    @patch('streamlit.file_uploader')
    def test_file_uploader(self, mock_file_uploader):
        view = SFNStreamlitView()
        view.file_uploader("Upload a file", accepted_types=["csv", "xlsx"])
        mock_file_uploader.assert_called_once_with("Upload a file", type=["csv", "xlsx"])

    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.mkdir')
    def test_save_uploaded_file(self, mock_mkdir, mock_open_file):
        # Create an instance of the SFNStreamlitView
        view = SFNStreamlitView()

        # Mock the uploaded file
        mock_file = MagicMock()
        mock_file.name = "test.csv"
        mock_file.getbuffer.return_value = b"file content"

        # Call the method to test
        file_path = view.save_uploaded_file(mock_file)

        # Assert the file path is as expected
        self.assertEqual(file_path, 'temp_files/test.csv')

        # Check that the directory was created
        mock_mkdir.assert_called_once_with(exist_ok=True)

        # Check that the open method was called with the correct file path and mode
        mock_open_file.assert_called_once_with(Path('temp_files/test.csv'), 'wb')

        # Ensure the file content was written
        mock_open_file().write.assert_called_once_with(b"file content")

    @patch('os.remove')
    @patch('os.path.exists', return_value=True)
    def test_delete_uploaded_file(self, mock_exists, mock_remove):
        view = SFNStreamlitView()
        result = view.delete_uploaded_file("test.csv")
        self.assertTrue(result)
        mock_remove.assert_called_once_with("test.csv")

    def test_delete_uploaded_file_file_not_exist(self):
        # Create an instance of FileManager
        view = SFNStreamlitView()

        # Mocking os.path.exists for file not existing
        with patch('os.path.exists', return_value=False):
            with patch.object(view, 'show_message') as mock_show_message:
                result = view.delete_uploaded_file('nonexistent_file.txt')
                mock_show_message.assert_called_once_with('File nonexistent_file.txt does not exist.', 'error')
                assert result is False

    def test_delete_uploaded_file_exception(self):
        # Create an instance of FileManager
        view = SFNStreamlitView()

        # Mocking os.path.exists to return True but simulate an exception when os.remove is called
        with patch('os.path.exists', return_value=True):
            with patch('os.remove', side_effect=Exception('Mocked delete error')):
                with patch.object(view, 'show_message') as mock_show_message:
                    result = view.delete_uploaded_file(file_path='/mock_file.txt')
                    mock_show_message.assert_called_once_with('Error deleting file: Mocked delete error', 'error')
                    assert result is False

    @patch('streamlit.progress')
    def test_load_progress_bar(self, mock_progress):
        view = SFNStreamlitView()
        view.load_progress_bar(0.5)
        mock_progress.assert_called_once_with(0.5)

    @patch('streamlit.container')
    def test_create_container(self, mock_container):
        view = SFNStreamlitView()
        view.create_container()
        mock_container.assert_called_once()

    @patch('streamlit.button')
    def test_display_button(self, mock_button):
        view = SFNStreamlitView()
        view.display_button("Click Me")
        mock_button.assert_called_once_with("Click Me", key=None)

    @patch('streamlit.radio')
    def test_radio_select(self, mock_radio):
        view = SFNStreamlitView()
        view.radio_select("Select option", options=["Option 1", "Option 2"])
        mock_radio.assert_called_once_with("Select option", ["Option 1", "Option 2"], key=None)

    @patch('streamlit.dataframe')
    def test_display_dataframe(self, mock_dataframe):
        view = SFNStreamlitView()
        data = MagicMock()
        view.display_dataframe(data)
        mock_dataframe.assert_called_once_with(data)

    @patch('streamlit.spinner')
    def test_display_spinner(self, mock_spinner):
        view = SFNStreamlitView()
        with view.display_spinner("Loading..."):
            pass
        mock_spinner.assert_called_once_with("Loading...")

    @patch('streamlit.selectbox')
    def test_select_box(self, mock_selectbox):
        view = SFNStreamlitView()
        view.select_box("Select an option", options=["A", "B"])
        mock_selectbox.assert_called_once_with("Select an option", ["A", "B"], key=None)

    @patch('streamlit.download_button')
    def test_create_download_button(self, mock_download_button):
        view = SFNStreamlitView()
        data = b"some binary data"
        view.create_download_button("Download", data, "test.csv", "text/csv")
        mock_download_button.assert_called_once_with(
            label="Download", data=data, file_name="test.csv", mime="text/csv"
        )

    @patch('streamlit.stop')
    def test_stop_execution(self, mock_stop):
        view = SFNStreamlitView()
        view.stop_execution()
        mock_stop.assert_called_once()

    @patch('streamlit.rerun')
    def test_rerun_script(self, mock_rerun):
        view = SFNStreamlitView()
        view.rerun_script()
        mock_rerun.assert_called_once()

    @patch('streamlit.empty')
    def test_make_empty(self, mock_empty):
        view = SFNStreamlitView()
        view.make_empty()
        mock_empty.assert_called_once()

    @patch('streamlit.delta_generator.DeltaGenerator.text')
    def test_update_text(self, mock_text):
        view = SFNStreamlitView()
        mock_text_element = MagicMock()
        view.update_text(mock_text_element, "New text")
        mock_text_element.text.assert_called_once_with("New text")

    @patch('streamlit.progress')
    def test_update_progress(self, mock_progress):
        view = SFNStreamlitView()
        progress_bar = MagicMock()
        view.update_progress(progress_bar, 0.75)
        progress_bar.progress.assert_called_once_with(0.75)
    
    @patch('streamlit.progress')
    @patch('streamlit.empty')
    def test_create_progress_container(self, mock_empty, mock_progress):
        view = SFNStreamlitView()
        progress_bar, status_text = view.create_progress_container()

        # Check if the progress bar was created with an initial value of 0.0
        mock_progress.assert_called_once_with(0.0)
        # Check if an empty container was created
        mock_empty.assert_called_once()