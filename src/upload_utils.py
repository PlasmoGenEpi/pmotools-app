"""Helpers for reading uploaded files, including zipped or tarred folders."""

import tarfile
import zipfile
from io import BytesIO
from pathlib import PurePosixPath

ARCHIVE_SUFFIXES = (".zip", ".tar.gz", ".tgz", ".tar")


def is_archive(file_name):
    return file_name.lower().endswith(ARCHIVE_SUFFIXES)


def _is_hidden(file_name):
    return PurePosixPath(file_name).name.startswith(".") or "__MACOSX" in file_name


def _archive_members(file_name, data):
    if file_name.lower().endswith(".zip"):
        with zipfile.ZipFile(BytesIO(data)) as archive:
            for info in archive.infolist():
                if not info.is_dir():
                    yield info.filename, archive.read(info)
    else:
        with tarfile.open(fileobj=BytesIO(data)) as archive:
            for member in archive.getmembers():
                if member.isfile():
                    yield member.name, archive.extractfile(member).read()


def iter_uploaded_files(files):
    """Yield (file name, bytes) for each uploaded file, expanding zip and tar
    archives into their member files and skipping hidden files such as
    .DS_Store and __MACOSX entries."""
    for file in files:
        data = file.getvalue()
        if is_archive(file.name):
            for name, member_data in _archive_members(file.name, data):
                if not _is_hidden(name):
                    yield name, member_data
        elif not _is_hidden(file.name):
            yield file.name, data
