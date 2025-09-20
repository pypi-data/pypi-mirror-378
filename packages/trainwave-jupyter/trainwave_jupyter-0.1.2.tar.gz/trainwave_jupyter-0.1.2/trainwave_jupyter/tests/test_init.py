from unittest.mock import MagicMock

from trainwave_jupyter import (
    _jupyter_labextension_paths,
    _jupyter_server_extension_points,
    _load_jupyter_server_extension,
)


class TestJupyterServerExtensionPoints:
    """Test the _jupyter_server_extension_points function"""

    def test_jupyter_server_extension_points(self):
        """Test that server extension points are returned correctly"""
        points = _jupyter_server_extension_points()

        assert isinstance(points, list)
        assert len(points) == 1
        assert points[0] == {"module": "trainwave_jupyter"}


class TestJupyterLabExtensionPaths:
    """Test the _jupyter_labextension_paths function"""

    def test_jupyter_labextension_paths(self):
        """Test that lab extension paths are returned correctly"""
        paths = _jupyter_labextension_paths()

        assert isinstance(paths, list)
        assert len(paths) == 1
        assert paths[0] == {"src": "labextension", "dest": "trainwave-jupyter"}


class TestLoadJupyterServerExtension:
    """Test the _load_jupyter_server_extension function"""

    def test_load_jupyter_server_extension(self):
        """Test that server extension loads without error"""
        # Mock the server app
        mock_server_app = MagicMock()
        mock_server_app.web_app = MagicMock()
        mock_server_app.web_app.settings = {"base_url": "/"}
        mock_server_app.log = MagicMock()

        # Should not raise any exceptions
        _load_jupyter_server_extension(mock_server_app)

        # Verify that the extension was registered
        mock_server_app.web_app.add_handlers.assert_called_once()
        mock_server_app.log.info.assert_called_once()
