from tempfile import SpooledTemporaryFile
from typing import Annotated, BinaryIO, cast
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from medvision.api.dependencies import get_create_study_service, get_study_catalog_service
from medvision.api.schemas import StudyResponse
from medvision.application.commands import CreateStudyCommand
from medvision.application.services import CreateStudyService, StudyCatalogService
from medvision.domain.enums import StudyModality

router = APIRouter(prefix="/api/v1/studies", tags=["studies"])
CHUNK_SIZE = 1024 * 1024
SPOOL_MEMORY_LIMIT = 8 * 1024 * 1024


@router.post("", response_model=StudyResponse, status_code=status.HTTP_201_CREATED)
async def create_study(
    file: Annotated[UploadFile, File()],
    modality: Annotated[StudyModality, Form()],
    service: Annotated[CreateStudyService, Depends(get_create_study_service)],
) -> StudyResponse:
    try:
        with SpooledTemporaryFile(max_size=SPOOL_MEMORY_LIMIT, mode="w+b") as content:
            while chunk := await file.read(CHUNK_SIZE):
                content.write(chunk)
            content.seek(0)
            command = CreateStudyCommand(
                filename=file.filename or "",
                modality=modality,
                content_type=file.content_type,
                content=cast(BinaryIO, content),
            )
            study = service.execute(command)
        return StudyResponse.model_validate(study)
    finally:
        await file.close()


@router.get("", response_model=list[StudyResponse])
def list_studies(
    service: Annotated[StudyCatalogService, Depends(get_study_catalog_service)],
) -> list[StudyResponse]:
    return [StudyResponse.model_validate(study) for study in service.list()]


@router.get("/{study_id}", response_model=StudyResponse)
def get_study(
    study_id: UUID,
    service: Annotated[StudyCatalogService, Depends(get_study_catalog_service)],
) -> StudyResponse:
    return StudyResponse.model_validate(service.get(study_id))
