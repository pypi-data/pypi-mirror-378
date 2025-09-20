import os
import tarfile
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from trainwave_jupyter.io import create_tarball, get_all_files_in_dir


class TestGetAllFilesInDir:
    """Test the get_all_files_in_dir function"""

    def test_empty_directory(self):
        """Test with empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            files = get_all_files_in_dir(temp_dir)
            assert files == []

    def test_single_file(self):
        """Test with single file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test content")

            files = get_all_files_in_dir(temp_dir)
            assert len(files) == 1
            assert files[0] == test_file

    def test_nested_files(self):
        """Test with nested directory structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested structure
            subdir = os.path.join(temp_dir, "subdir")
            os.makedirs(subdir)

            file1 = os.path.join(temp_dir, "file1.txt")
            file2 = os.path.join(subdir, "file2.txt")

            with open(file1, "w") as f:
                f.write("content1")
            with open(file2, "w") as f:
                f.write("content2")

            files = get_all_files_in_dir(temp_dir)
            assert len(files) == 2
            assert file1 in files
            assert file2 in files

    def test_multiple_files_same_level(self):
        """Test with multiple files at same level"""
        with tempfile.TemporaryDirectory() as temp_dir:
            files_to_create = ["file1.txt", "file2.py", "file3.json"]
            created_files = []

            for filename in files_to_create:
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, "w") as f:
                    f.write(f"content for {filename}")
                created_files.append(filepath)

            files = get_all_files_in_dir(temp_dir)
            assert len(files) == 3
            for created_file in created_files:
                assert created_file in files


class TestCreateTarball:
    """Test the create_tarball function"""

    def test_basic_tarball_creation(self):
        """Test basic tarball creation without exclusions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1 = os.path.join(temp_dir, "file1.txt")
            file2 = os.path.join(temp_dir, "file2.py")

            with open(file1, "w") as f:
                f.write("content1")
            with open(file2, "w") as f:
                f.write("content2")

            # Create tarball
            tarball = create_tarball(
                source_dir=Path(temp_dir),
                exclude_gitignore=False,
                exclude_regex=None,
                show_progress_bar=False,
            )

            # Verify tarball was created
            assert os.path.exists(tarball.name)

            # Verify contents
            with tarfile.open(tarball.name, "r:gz") as tar:
                members = tar.getnames()
                assert "file1.txt" in members
                assert "file2.py" in members

    def test_tarball_with_gitignore_exclusion(self):
        """Test tarball creation with .gitignore exclusions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1 = os.path.join(temp_dir, "file1.txt")
            file2 = os.path.join(temp_dir, "file2.py")
            ignored_file = os.path.join(temp_dir, "ignored.txt")

            with open(file1, "w") as f:
                f.write("content1")
            with open(file2, "w") as f:
                f.write("content2")
            with open(ignored_file, "w") as f:
                f.write("ignored content")

            # Create .gitignore file
            gitignore_path = os.path.join(temp_dir, ".gitignore")
            with open(gitignore_path, "w") as f:
                f.write("ignored.txt\n*.py")

            # Create tarball with gitignore exclusion
            tarball = create_tarball(
                source_dir=Path(temp_dir),
                exclude_gitignore=True,
                exclude_regex=None,
                show_progress_bar=False,
            )

            # Verify contents
            with tarfile.open(tarball.name, "r:gz") as tar:
                members = tar.getnames()
                assert "file1.txt" in members
                assert "file2.py" not in members  # Excluded by gitignore
                assert "ignored.txt" not in members  # Excluded by gitignore
                assert ".gitignore" in members

    def test_tarball_with_regex_exclusion(self):
        """Test tarball creation with regex exclusions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1 = os.path.join(temp_dir, "file1.txt")
            file2 = os.path.join(temp_dir, "file2.py")
            temp_file = os.path.join(temp_dir, "temp.log")

            with open(file1, "w") as f:
                f.write("content1")
            with open(file2, "w") as f:
                f.write("content2")
            with open(temp_file, "w") as f:
                f.write("temp content")

            # Create tarball with regex exclusion
            tarball = create_tarball(
                source_dir=Path(temp_dir),
                exclude_gitignore=False,
                exclude_regex=r"\.(log|tmp)$",
                show_progress_bar=False,
            )

            # Verify contents
            with tarfile.open(tarball.name, "r:gz") as tar:
                members = tar.getnames()
                assert "file1.txt" in members
                assert "file2.py" in members
                assert "temp.log" not in members  # Excluded by regex

    def test_tarball_with_both_exclusions(self):
        """Test tarball creation with both gitignore and regex exclusions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1 = os.path.join(temp_dir, "file1.txt")
            file2 = os.path.join(temp_dir, "file2.py")
            ignored_file = os.path.join(temp_dir, "ignored.txt")
            temp_file = os.path.join(temp_dir, "temp.log")

            with open(file1, "w") as f:
                f.write("content1")
            with open(file2, "w") as f:
                f.write("content2")
            with open(ignored_file, "w") as f:
                f.write("ignored content")
            with open(temp_file, "w") as f:
                f.write("temp content")

            # Create .gitignore file
            gitignore_path = os.path.join(temp_dir, ".gitignore")
            with open(gitignore_path, "w") as f:
                f.write("ignored.txt")

            # Create tarball with both exclusions
            tarball = create_tarball(
                source_dir=Path(temp_dir),
                exclude_gitignore=True,
                exclude_regex=r"\.log$",
                show_progress_bar=False,
            )

            # Verify contents
            with tarfile.open(tarball.name, "r:gz") as tar:
                members = tar.getnames()
                assert "file1.txt" in members
                assert "file2.py" in members
                assert "ignored.txt" not in members  # Excluded by gitignore
                assert "temp.log" not in members  # Excluded by regex

    def test_tarball_without_gitignore_file(self):
        """Test tarball creation when .gitignore doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1 = os.path.join(temp_dir, "file1.txt")
            file2 = os.path.join(temp_dir, "file2.py")

            with open(file1, "w") as f:
                f.write("content1")
            with open(file2, "w") as f:
                f.write("content2")

            # Create tarball with gitignore exclusion but no .gitignore file
            tarball = create_tarball(
                source_dir=Path(temp_dir),
                exclude_gitignore=True,
                exclude_regex=None,
                show_progress_bar=False,
            )

            # Verify contents (should include all files)
            with tarfile.open(tarball.name, "r:gz") as tar:
                members = tar.getnames()
                assert "file1.txt" in members
                assert "file2.py" in members

    def test_tarball_with_large_file_warning(self):
        """Test tarball creation with large file warning"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a large file (simulate with mock)
            large_file = os.path.join(temp_dir, "large_file.txt")
            with open(large_file, "w") as f:
                f.write("x" * 1000)  # Small content for test

            # Mock os.path.getsize to return large size
            with patch("os.path.getsize") as mock_getsize:
                mock_getsize.return_value = 100 * 1024 * 1024  # 100MB

                with patch("trainwave_jupyter.io.logger") as mock_logger:
                    create_tarball(
                        source_dir=Path(temp_dir),
                        exclude_gitignore=False,
                        exclude_regex=None,
                        show_progress_bar=False,
                    )

                    # Verify warning was logged
                    mock_logger.warning.assert_called()
                    warning_call = mock_logger.warning.call_args[0][0]
                    assert "larger than" in warning_call

    def test_tarball_progress_bar(self):
        """Test tarball creation with progress bar"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1 = os.path.join(temp_dir, "file1.txt")
            with open(file1, "w") as f:
                f.write("content1")

            # Mock tqdm to avoid actual progress bar in tests
            with patch("trainwave_jupyter.io.tqdm") as mock_tqdm:
                mock_progress = MagicMock()
                mock_tqdm.return_value.__enter__.return_value = mock_progress
                mock_tqdm.return_value.__exit__.return_value = None

                create_tarball(
                    source_dir=Path(temp_dir),
                    exclude_gitignore=False,
                    exclude_regex=None,
                    show_progress_bar=True,
                )

                # Verify tqdm was called
                mock_tqdm.assert_called_once()
                # The progress bar is created and used, which is the main functionality
                # The update calls depend on the internal implementation details

    def test_tarball_without_progress_bar(self):
        """Test tarball creation without progress bar"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1 = os.path.join(temp_dir, "file1.txt")
            with open(file1, "w") as f:
                f.write("content1")

            # Mock tqdm to ensure it's not called
            with patch("trainwave_jupyter.io.tqdm") as mock_tqdm:
                create_tarball(
                    source_dir=Path(temp_dir),
                    exclude_gitignore=False,
                    exclude_regex=None,
                    show_progress_bar=False,
                )

                # Verify tqdm was not called
                mock_tqdm.assert_not_called()

    def test_tarball_arcname_correctness(self):
        """Test that files are added with correct arcnames (relative paths)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested structure
            subdir = os.path.join(temp_dir, "subdir")
            os.makedirs(subdir)

            file1 = os.path.join(temp_dir, "file1.txt")
            file2 = os.path.join(subdir, "file2.txt")

            with open(file1, "w") as f:
                f.write("content1")
            with open(file2, "w") as f:
                f.write("content2")

            tarball = create_tarball(
                source_dir=Path(temp_dir),
                exclude_gitignore=False,
                exclude_regex=None,
                show_progress_bar=False,
            )

            # Verify arcnames are correct
            with tarfile.open(tarball.name, "r:gz") as tar:
                members = tar.getnames()
                assert "file1.txt" in members
                assert "subdir/file2.txt" in members

    def test_tarball_compression(self):
        """Test that tarball is properly compressed"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            file1 = os.path.join(temp_dir, "file1.txt")
            with open(file1, "w") as f:
                f.write("content1")

            tarball = create_tarball(
                source_dir=Path(temp_dir),
                exclude_gitignore=False,
                exclude_regex=None,
                show_progress_bar=False,
            )

            # Verify it's a gzipped tar file
            with tarfile.open(tarball.name, "r:gz") as tar:
                # If this doesn't raise an exception, it's properly compressed
                members = tar.getnames()
                assert "file1.txt" in members

    def test_tarball_cleanup(self):
        """Test that temporary file is properly created and can be cleaned up"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            file1 = os.path.join(temp_dir, "file1.txt")
            with open(file1, "w") as f:
                f.write("content1")

            tarball = create_tarball(
                source_dir=Path(temp_dir),
                exclude_gitignore=False,
                exclude_regex=None,
                show_progress_bar=False,
            )

            # Verify file exists
            assert os.path.exists(tarball.name)

            # Clean up
            tarball.close()

            # Verify file is cleaned up
            assert not os.path.exists(tarball.name)
