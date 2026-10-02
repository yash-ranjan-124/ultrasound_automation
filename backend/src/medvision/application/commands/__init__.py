from dataclasses import dataclass
from typing import BinaryIO

from medvision.domain.enums import StudyModality


@dataclass(frozen=True)
class CreateStudyCommand:
    filename: str
    modality: StudyModality
    content_type: str | None
    content: BinaryIO
