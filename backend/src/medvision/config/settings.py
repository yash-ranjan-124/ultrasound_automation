import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    storage_root: Path = Path(os.getenv("STORAGE_ROOT", "data/storage"))
