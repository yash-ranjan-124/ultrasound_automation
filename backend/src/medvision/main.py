from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.exceptions import HTTPException

from medvision.api.routers.health import router as health_router
from medvision.api.routers.studies import router as studies_router
from medvision.application.services import (
    CreateStudyService,
    StudyCatalogService,
    StudyTypeResolver,
)
from medvision.config import Settings
from medvision.domain.exceptions import (
    MetadataExtractionError,
    StorageError,
    StudyNotFoundError,
    UnsupportedStudyTypeError,
)
from medvision.domain.ports import StudyRepository
from medvision.infrastructure.imaging import LocalStudyMetadataReader
from medvision.infrastructure.persistence import (
    SqlAlchemyStudyRepository,
    create_database_engine,
)
from medvision.infrastructure.storage import LocalFileStorageAdapter


def create_app(
    settings: Settings | None = None,
    repository: StudyRepository | None = None,
) -> FastAPI:
    active_settings = settings or Settings()
    engine: Engine | None = None
    active_repository = repository
    if active_repository is None:
        engine = create_database_engine(active_settings.database_url)
        active_repository = SqlAlchemyStudyRepository(sessionmaker(engine, class_=Session))

    @asynccontextmanager
    async def lifespan(_application: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            if engine is not None:
                engine.dispose()

    application = FastAPI(
        title="MedVision AI Lab",
        description="Research use only; not for clinical diagnosis.",
        lifespan=lifespan,
    )
    storage = LocalFileStorageAdapter(active_settings.storage_root)
    application.state.create_study_service = CreateStudyService(
        storage=storage,
        repository=active_repository,
        metadata_reader=LocalStudyMetadataReader(storage),
        resolver=StudyTypeResolver(),
    )
    application.state.study_catalog_service = StudyCatalogService(active_repository)
    application.include_router(health_router)
    application.include_router(studies_router)

    @application.exception_handler(UnsupportedStudyTypeError)
    async def unsupported_study_error(
        _request: Request, exc: UnsupportedStudyTypeError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "UNSUPPORTED_STUDY_TYPE",
                    "message": "The uploaded file type is not supported.",
                    "details": {},
                }
            },
        )

    @application.exception_handler(StudyNotFoundError)
    async def study_not_found_error(_request: Request, _exc: StudyNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "STUDY_NOT_FOUND",
                    "message": "The requested imaging study does not exist.",
                    "details": {},
                }
            },
        )

    @application.exception_handler(MetadataExtractionError)
    async def invalid_study_error(_request: Request, _exc: MetadataExtractionError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "INVALID_STUDY_FILE",
                    "message": "The uploaded file could not be read as the declared imaging type.",
                    "details": {},
                }
            },
        )

    @application.exception_handler(StorageError)
    async def storage_error(_request: Request, _exc: StorageError) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "STORAGE_ERROR",
                    "message": "Unable to store the uploaded imaging study.",
                    "details": {},
                }
            },
        )

    @application.exception_handler(HTTPException)
    async def http_error(_request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": "HTTP_ERROR", "message": str(exc.detail), "details": {}}},
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, _exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {"code": "INVALID_REQUEST", "message": "Invalid request.", "details": {}}
            },
        )

    @application.exception_handler(Exception)
    async def unexpected_error(_request: Request, _exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": {"code": "INTERNAL_ERROR", "message": "Unexpected error.", "details": {}}
            },
        )

    return application


app = create_app()
