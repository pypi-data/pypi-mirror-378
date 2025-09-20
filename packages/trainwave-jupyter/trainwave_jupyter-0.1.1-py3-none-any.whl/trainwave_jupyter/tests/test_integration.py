"""
Integration tests for the Trainwave JupyterLab extension
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from trainwave_jupyter.handlers import TrainwaveConfig
from trainwave_jupyter.io import create_tarball


class TestIntegration:
    """Integration tests for the complete extension workflow"""

    @pytest.mark.skip(reason="Integration test requires proper Jupyter server setup")
    @pytest.mark.asyncio
    async def test_authentication_flow_integration(self, jp_fetch):
        """Test the complete authentication flow from frontend to backend"""
        # Test creating an authentication session
        response = await jp_fetch(
            "trainwave-jupyter",
            "auth/create_session",
            method="POST",
            body=json.dumps({"name": "integration-test"}),
        )

        assert response.code == 200
        session_data = json.loads(response.body)
        assert "url" in session_data
        assert "token" in session_data
        assert session_data["url"].startswith("https://trainwave.ai")

        # Test checking session status
        token = session_data["token"]
        response = await jp_fetch(
            "trainwave-jupyter",
            "auth/session_status",
            method="POST",
            body=json.dumps({"token": token}),
        )

        assert response.code == 200
        status_data = json.loads(response.body)
        assert "status" in status_data
        assert status_data["status"] in ["NOT_COMPLETED", "SUCCESS", "NOT_FOUND"]

    @pytest.mark.skip(reason="Integration test requires proper Jupyter server setup")
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, jp_fetch):
        """Test error handling across the extension"""
        # Test invalid JSON
        response = await jp_fetch(
            "trainwave-jupyter",
            "auth/create_session",
            method="POST",
            body="invalid json",
        )

        assert response.code == 400
        error_data = json.loads(response.body)
        assert "error" in error_data
        assert "Invalid JSON" in error_data["error"]

        # Test missing token
        response = await jp_fetch(
            "trainwave-jupyter",
            "auth/session_status",
            method="POST",
            body=json.dumps({}),
        )

        assert response.code == 400
        error_data = json.loads(response.body)
        assert "error" in error_data
        assert "Missing token parameter" in error_data["error"]

        # Test unknown endpoint
        response = await jp_fetch(
            "trainwave-jupyter", "auth/unknown", method="POST", body=json.dumps({})
        )

        assert response.code == 404
        error_data = json.loads(response.body)
        assert "error" in error_data
        assert "Endpoint not found" in error_data["error"]

    def test_configuration_integration(self):
        """Test configuration loading and environment variable handling"""
        # Test with default configuration
        config = TrainwaveConfig()
        assert config.api_endpoint == "https://backend.trainwave.ai"
        assert config.use_mock is False

        # Test with environment variables
        with patch.dict(
            os.environ,
            {
                "TRAINWAVE_API_ENDPOINT": "https://custom.api.com",
                "TRAINWAVE_USE_MOCK": "true",
            },
        ):
            config = TrainwaveConfig()
            assert config.api_endpoint == "https://custom.api.com"
            assert config.use_mock is True

    def test_tarball_creation_integration(self):
        """Test tarball creation with real file system operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a realistic project structure
            project_files = {
                "main.py": "print('Hello, Trainwave!')",
                "requirements.txt": "numpy==1.21.0\ntorch==1.9.0",
                "data/train.csv": "feature1,feature2,label\n1,2,0\n3,4,1",
                "models/model.pkl": "binary_model_data",
                ".gitignore": "*.pyc\n__pycache__/\n*.log",
                "temp.log": "temporary log file",
                "config.json": '{"learning_rate": 0.001, "epochs": 100}',
            }

            # Create the file structure
            for file_path, content in project_files.items():
                full_path = Path(temp_dir) / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)

            # Test tarball creation with gitignore exclusion
            tarball = create_tarball(
                source_dir=Path(temp_dir),
                exclude_gitignore=True,
                exclude_regex=r"\.log$",
                show_progress_bar=False,
            )

            # Verify tarball contents
            import tarfile

            with tarfile.open(tarball.name, "r:gz") as tar:
                members = tar.getnames()

                # Should include main files
                assert "main.py" in members
                assert "requirements.txt" in members
                assert "data/train.csv" in members
                assert "models/model.pkl" in members
                assert "config.json" in members
                assert ".gitignore" in members

                # Should exclude files based on gitignore and regex
                assert "temp.log" not in members

            tarball.close()

    @pytest.mark.skip(reason="Integration test requires proper Jupyter server setup")
    @pytest.mark.asyncio
    async def test_mock_mode_integration(self, jp_fetch):
        """Test the extension in mock mode"""
        with patch.dict(os.environ, {"TRAINWAVE_USE_MOCK": "true"}):
            # Create session in mock mode
            response = await jp_fetch(
                "trainwave-jupyter",
                "auth/create_session",
                method="POST",
                body=json.dumps({"name": "mock-test"}),
            )

            assert response.code == 200
            session_data = json.loads(response.body)
            assert "url" in session_data
            assert "token" in session_data

            # Check status in mock mode
            token = session_data["token"]
            response = await jp_fetch(
                "trainwave-jupyter",
                "auth/session_status",
                method="POST",
                body=json.dumps({"token": token}),
            )

            assert response.code == 200
            status_data = json.loads(response.body)
            assert status_data["status"] == "NOT_COMPLETED"

    def test_file_operations_integration(self):
        """Test file operations with various file types and sizes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create files of different types and sizes
            test_files = {
                "small.txt": "x" * 100,  # 100 bytes
                "medium.py": "print('x')\n" * 1000,  # ~5KB
                "large.json": json.dumps({"data": ["x"] * 10000}),  # ~1MB
                "binary.bin": b"\x00" * 1000,  # 1KB binary
            }

            for filename, content in test_files.items():
                file_path = Path(temp_dir) / filename
                if isinstance(content, str):
                    file_path.write_text(content)
                else:
                    file_path.write_bytes(content)

            # Create tarball
            tarball = create_tarball(
                source_dir=Path(temp_dir),
                exclude_gitignore=False,
                exclude_regex=None,
                show_progress_bar=False,
            )

            # Verify all files are included
            import tarfile

            with tarfile.open(tarball.name, "r:gz") as tar:
                members = tar.getnames()
                for filename in test_files.keys():
                    assert filename in members

            tarball.close()

    @pytest.mark.skip(reason="Integration test requires proper Jupyter server setup")
    @pytest.mark.asyncio
    async def test_concurrent_requests_integration(self, jp_fetch):
        """Test handling of concurrent requests"""
        import asyncio

        # Create multiple concurrent session requests
        tasks = []
        for i in range(5):
            task = jp_fetch(
                "trainwave-jupyter",
                "auth/create_session",
                method="POST",
                body=json.dumps({"name": f"concurrent-test-{i}"}),
            )
            tasks.append(task)

        # Wait for all requests to complete
        responses = await asyncio.gather(*tasks)

        # Verify all requests succeeded
        for response in responses:
            assert response.code == 200
            session_data = json.loads(response.body)
            assert "url" in session_data
            assert "token" in session_data

    def test_memory_usage_integration(self):
        """Test memory usage with large file operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a large file (simulate with multiple smaller files)
            large_data = "x" * 10000  # 10KB per file
            for i in range(100):  # 100 files = ~1MB total
                file_path = Path(temp_dir) / f"large_file_{i:03d}.txt"
                file_path.write_text(large_data)

            # Create tarball and verify it works without memory issues
            tarball = create_tarball(
                source_dir=Path(temp_dir),
                exclude_gitignore=False,
                exclude_regex=None,
                show_progress_bar=False,
            )

            # Verify tarball was created successfully
            assert os.path.exists(tarball.name)
            assert os.path.getsize(tarball.name) > 0

            tarball.close()

    @pytest.mark.skip(reason="Integration test requires proper Jupyter server setup")
    @pytest.mark.asyncio
    async def test_api_fallback_integration(self, jp_fetch):
        """Test API fallback behavior when external API is unavailable"""
        # This test simulates the scenario where the external Trainwave API
        # is unavailable and the extension falls back to mock mode

        # First, test with mock mode disabled (should fallback to mock on API failure)
        with patch.dict(os.environ, {"TRAINWAVE_USE_MOCK": "false"}):
            # Mock aiohttp to simulate API failure
            with patch("aiohttp.ClientSession") as mock_session:
                mock_session.side_effect = Exception("API unavailable")

                response = await jp_fetch(
                    "trainwave-jupyter",
                    "auth/create_session",
                    method="POST",
                    body=json.dumps({"name": "fallback-test"}),
                )

                # Should still succeed due to fallback
                assert response.code == 200
                session_data = json.loads(response.body)
                assert "url" in session_data
                assert "token" in session_data

    def test_unicode_handling_integration(self):
        """Test handling of Unicode characters in file names and content"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create files with Unicode names and content
            unicode_files = {
                "测试文件.txt": "这是中文内容",
                "файл_тест.py": "print('Привет, мир!')",
                "ファイル.json": '{"message": "こんにちは世界"}',
                "test_émojis.txt": "Hello 🌍 World! 🚀",
            }

            for filename, content in unicode_files.items():
                file_path = Path(temp_dir) / filename
                file_path.write_text(content, encoding="utf-8")

            # Create tarball
            tarball = create_tarball(
                source_dir=Path(temp_dir),
                exclude_gitignore=False,
                exclude_regex=None,
                show_progress_bar=False,
            )

            # Verify Unicode files are handled correctly
            import tarfile

            with tarfile.open(tarball.name, "r:gz") as tar:
                members = tar.getnames()
                for filename in unicode_files.keys():
                    assert filename in members

                # Verify content is preserved
                for member in tar.getmembers():
                    if member.name in unicode_files:
                        content = tar.extractfile(member).read().decode("utf-8")
                        assert content == unicode_files[member.name]

            tarball.close()
