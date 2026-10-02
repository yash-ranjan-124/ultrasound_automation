import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    storage_root: Path = Path(os.getenv("STORAGE_ROOT", "data/storage"))
    database_url: str | None = field(default_factory=lambda: os.getenv("DATABASE_URL"), repr=False)
