from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, DateTime, String, Text, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class StudyRecord(Base):
    __tablename__ = "medvision_studies"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    study_type: Mapped[str] = mapped_column(String(16), nullable=False)
    modality: Mapped[str] = mapped_column(String(24), nullable=False)
    storage_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    study_metadata: Mapped[dict[str, object]] = mapped_column("metadata", JSON, nullable=False)
