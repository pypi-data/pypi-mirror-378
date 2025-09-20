import io
import os
import re
import tarfile
import tempfile
import typing
from contextlib import nullcontext
from pathlib import Path

import pathspec
from loguru import logger
from tqdm import tqdm

WARN_FILE_SIZE = 50 * 1024 * 1024  # 100 MB


def get_all_files_in_dir(directory):
    return [
        os.path.join(root, file)
        for root, dirs, files in os.walk(directory)
        for file in files
    ]


def create_tarball(
    source_dir: Path,
    exclude_gitignore: bool,
    exclude_regex: str | None,
    show_progress_bar: bool = True,
    in_memory_files: list[tuple[str, io.BytesIO]] | None = None,
) -> typing.IO[typing.Any]:
    if in_memory_files is None:
        in_memory_files = []
    temp = tempfile.NamedTemporaryFile(suffix=".tar")
    spec = None

    if exclude_gitignore and (source_dir / ".gitignore").exists():
        with open(source_dir / ".gitignore") as gitignore:
            spec_src = gitignore.read()
        spec = pathspec.PathSpec.from_lines(
            pathspec.patterns.gitwildmatch.GitWildMatchPattern, spec_src.splitlines()
        )

    files = set(get_all_files_in_dir(source_dir))
    if spec is not None:
        files -= set(spec.match_files(files))

    # Run exclude regex
    if exclude_regex is not None:
        files = {file for file in files if not re.search(exclude_regex, file)}

    total_size = sum(os.path.getsize(file) for file in files)
    progress_bar = (
        tqdm(total=total_size, unit="B", unit_scale=True, desc="Creating archive")
        if show_progress_bar
        else nullcontext()
    )
    with tarfile.open(temp.name, "w:gz") as tar:
        with progress_bar:
            for file in files:
                if os.path.getsize(file) > WARN_FILE_SIZE:
                    logger.warning(
                        f"{file} is larger than {WARN_FILE_SIZE / (1024 * 1024)}MB"
                    )
                arcname = os.path.relpath(file, source_dir)
                tar.add(file, arcname=arcname)
                if show_progress_bar:
                    progress_bar.update(os.path.getsize(file))

            for file_name, content in in_memory_files:
                info = tarfile.TarInfo(file_name)
                info.size = len(content.getvalue())
                tar.addfile(info, content)

    return temp
