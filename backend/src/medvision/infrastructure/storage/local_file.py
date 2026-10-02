from os import replace
from pathlib import Path, PurePosixPath
from shutil import copyfileobj
from tempfile import NamedTemporaryFile
from typing import BinaryIO

from medvision.domain.exceptions import StorageError


class LocalFileStorageAdapter:
    def __init__(self, storage_root: Path) -> None:
        self._root = storage_root.expanduser().resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def resolve_path(self, key: str) -> Path:
        if not key or "\x00" in key:
            raise StorageError("Invalid storage key")
        normalized = key.replace("\\", "/")
        relative = PurePosixPath(normalized)
        if relative.is_absolute() or ".." in relative.parts:
            raise StorageError("Storage key escapes the configured storage root")
        path = (self._root / Path(*relative.parts)).resolve()
        try:
            path.relative_to(self._root)
        except ValueError as exc:
            raise StorageError("Storage key escapes the configured storage root") from exc
        return path

    def save(self, key: str, content: BinaryIO) -> None:
        path = self.resolve_path(key)
        temporary_path: Path | None = None
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            content.seek(0)
            with NamedTemporaryFile(
                dir=path.parent, prefix=".upload-", delete=False
            ) as destination:
                temporary_path = Path(destination.name)
                copyfileobj(content, destination)
                destination.flush()
            replace(temporary_path, path)
        except OSError as exc:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise StorageError("Unable to save uploaded study") from exc

    def open(self, key: str) -> BinaryIO:
        path = self.resolve_path(key)
        try:
            return path.open("rb")
        except OSError as exc:
            raise StorageError("Unable to open stored study") from exc

    def read(self, key: str) -> bytes:
        with self.open(key) as source:
            return source.read()

    def delete(self, key: str) -> None:
        path = self.resolve_path(key)
        try:
            path.unlink(missing_ok=True)
            self._remove_empty_parents(path.parent)
        except OSError as exc:
            raise StorageError("Unable to remove stored study") from exc

    def exists(self, key: str) -> bool:
        return self.resolve_path(key).is_file()

    def _remove_empty_parents(self, directory: Path) -> None:
        while directory != self._root:
            try:
                directory.rmdir()
            except OSError:
                return
            directory = directory.parent
