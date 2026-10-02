import pytest

from medvision.config import Settings
from medvision.infrastructure.persistence import create_database_engine


def test_database_url_is_required_for_default_persistence() -> None:
    with pytest.raises(RuntimeError, match="DATABASE_URL is required"):
        create_database_engine(None)


def test_database_url_is_not_in_settings_repr() -> None:
    settings = Settings(database_url="postgresql://user:private-value@localhost/database")

    assert "private-value" not in repr(settings)
