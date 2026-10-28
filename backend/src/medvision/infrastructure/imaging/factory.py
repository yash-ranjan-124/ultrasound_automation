from dataclasses import dataclass

from medvision.domain.ports import StoragePort, VideoReaderPort
from medvision.infrastructure.imaging.video import OpenCVVideoReader


@dataclass(frozen=True)
class OpenCVVideoReaderFactory:
    storage: StoragePort

    def create(self) -> VideoReaderPort:
        return OpenCVVideoReader(self.storage)
