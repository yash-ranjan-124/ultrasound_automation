from io import BytesIO

import pytest

from medvision.domain.exceptions import StorageError
from medvision.infrastructure.storage import LocalFileStorageAdapter


def test_local_storage_save_open_exists_delete_and_nested_keys(tmp_path) -> None:
    storage = LocalFileStorageAdapter(tmp_path / "storage")
    key = "studies/example/source/image.png"
    storage.save(key, BytesIO(b"synthetic"))

    assert storage.exists(key)
    with storage.open(key) as source:
        assert source.read() == b"synthetic"
    assert storage.read(key) == b"synthetic"
    storage.delete(key)
    assert not storage.exists(key)


@pytest.mark.parametrize("key", ["../outside.txt", "/etc/passwd", "studies/../../outside"])
def test_storage_rejects_traversal_keys(tmp_path, key: str) -> None:
    storage = LocalFileStorageAdapter(tmp_path / "storage")
    with pytest.raises(StorageError):
        storage.save(key, BytesIO(b"no"))


def test_resolved_storage_path_stays_under_configured_root(tmp_path) -> None:
    storage = LocalFileStorageAdapter(tmp_path / "storage")
    path = storage.resolve_path("studies/123/source.mp4")
    assert path.is_relative_to((tmp_path / "storage").resolve())


def test_storage_rejects_symlink_escape(tmp_path) -> None:
    root = tmp_path / "storage"
    outside = tmp_path / "outside"
    outside.mkdir()
    root.mkdir()
    (root / "escape").symlink_to(outside, target_is_directory=True)
    storage = LocalFileStorageAdapter(root)

    with pytest.raises(StorageError):
        storage.save("escape/source.mp4", BytesIO(b"no"))
