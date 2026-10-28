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
from medvision.api.routers.tracking import router as tracking_router
from medvision.application.services import (
    CreateStudyService,
    CreateTrackingSessionService,
    StartTrackingService,
    StudyCatalogService,
    StudyTypeResolver,
    TrackingCatalogService,
)
from medvision.config import Settings
from medvision.domain.exceptions import (
    InvalidBoundingBoxError,
    InvalidTrackingStartError,
    InvalidTrackingStudyError,
    MetadataExtractionError,
    StorageError,
    StudyNotFoundError,
    TrackerInitializationError,
    TrackerUnavailableError,
    TrackingRunNotFoundError,
    TrackingSessionNotFoundError,
    UnsupportedStudyTypeError,
    UnsupportedTrackerError,
)
from medvision.domain.ports import (
    StudyRepository,
    TrackerFactory,
    TrackingRunRepository,
    TrackingSessionRepository,
    VideoReaderFactory,
)
from medvision.infrastructure.imaging import (
    LocalStudyMetadataReader,
    OpenCVVideoReaderFactory,
)
from medvision.infrastructure.persistence import (
    InMemoryTrackingRunRepository,
    InMemoryTrackingSessionRepository,
    SqlAlchemyStudyRepository,
    create_database_engine,
)
from medvision.infrastructure.storage import LocalFileStorageAdapter
from medvision.infrastructure.tracking import TrackerRegistry


def create_app(
    settings: Settings | None = None,
    repository: StudyRepository | None = None,
    tracking_sessions: TrackingSessionRepository | None = None,
    tracking_runs: TrackingRunRepository | None = None,
    video_reader_factory: VideoReaderFactory | None = None,
    tracker_factory: TrackerFactory | None = None,
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
    session_repository = tracking_sessions or InMemoryTrackingSessionRepository()
    run_repository = tracking_runs or InMemoryTrackingRunRepository()
    readers = video_reader_factory or OpenCVVideoReaderFactory(storage)
    trackers = tracker_factory or TrackerRegistry()

    application.state.create_study_service = CreateStudyService(
        storage=storage,
        repository=active_repository,
        metadata_reader=LocalStudyMetadataReader(),
        resolver=StudyTypeResolver(),
    )
    application.state.study_catalog_service = StudyCatalogService(active_repository)
    application.state.create_tracking_session_service = CreateTrackingSessionService(
        studies=active_repository,
        sessions=session_repository,
    )
    application.state.start_tracking_service = StartTrackingService(
        studies=active_repository,
        sessions=session_repository,
        runs=run_repository,
        video_readers=readers,
        trackers=trackers,
    )
    application.state.tracking_catalog_service = TrackingCatalogService(
        studies=active_repository,
        sessions=session_repository,
        runs=run_repository,
    )

    application.include_router(health_router)
    application.include_router(studies_router)
    application.include_router(tracking_router)

    def error_response(status_code: int, code: str, message: str) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={"error": {"code": code, "message": message, "details": {}}},
        )

    @application.exception_handler(UnsupportedStudyTypeError)
    async def unsupported_study_error(
        _request: Request, _exc: UnsupportedStudyTypeError
    ) -> JSONResponse:
        return error_response(
            400,
            "UNSUPPORTED_STUDY_TYPE",
            "The uploaded file type is not supported.",
        )

    @application.exception_handler(StudyNotFoundError)
    async def study_not_found_error(_request: Request, _exc: StudyNotFoundError) -> JSONResponse:
        return error_response(
            404,
            "STUDY_NOT_FOUND",
            "The requested imaging study does not exist.",
        )

    @application.exception_handler(TrackingSessionNotFoundError)
    async def tracking_session_not_found_error(
        _request: Request, _exc: TrackingSessionNotFoundError
    ) -> JSONResponse:
        return error_response(
            404,
            "TRACKING_SESSION_NOT_FOUND",
            "The requested tracking session does not exist.",
        )

    @application.exception_handler(TrackingRunNotFoundError)
    async def tracking_run_not_found_error(
        _request: Request, _exc: TrackingRunNotFoundError
    ) -> JSONResponse:
        return error_response(
            404,
            "TRACKING_RUN_NOT_FOUND",
            "The requested tracking run does not exist.",
        )

    @application.exception_handler(InvalidBoundingBoxError)
    async def invalid_bounding_box_error(
        _request: Request, _exc: InvalidBoundingBoxError
    ) -> JSONResponse:
        return error_response(
            400,
            "INVALID_BOUNDING_BOX",
            "The supplied bounding box is outside normalized image bounds.",
        )

    @application.exception_handler(InvalidTrackingStudyError)
    async def invalid_tracking_study_error(
        _request: Request, _exc: InvalidTrackingStudyError
    ) -> JSONResponse:
        return error_response(
            400,
            "INVALID_TRACKING_STUDY",
            "Tracking is supported only for video studies.",
        )

    @application.exception_handler(InvalidTrackingStartError)
    async def invalid_tracking_start_error(
        _request: Request, _exc: InvalidTrackingStartError
    ) -> JSONResponse:
        return error_response(
            400,
            "INVALID_TRACKING_START",
            "The requested tracking start frame is invalid.",
        )

    @application.exception_handler(UnsupportedTrackerError)
    async def unsupported_tracker_error(
        _request: Request, _exc: UnsupportedTrackerError
    ) -> JSONResponse:
        return error_response(
            400,
            "UNSUPPORTED_TRACKER",
            "The requested tracker is not supported.",
        )

    @application.exception_handler(TrackerUnavailableError)
    async def tracker_unavailable_error(
        _request: Request, _exc: TrackerUnavailableError
    ) -> JSONResponse:
        return error_response(
            503,
            "TRACKER_UNAVAILABLE",
            "The requested tracker is unavailable in this runtime.",
        )

    @application.exception_handler(TrackerInitializationError)
    async def tracker_initialization_error(
        _request: Request, _exc: TrackerInitializationError
    ) -> JSONResponse:
        return error_response(
            400,
            "TRACKER_INITIALIZATION_FAILED",
            "The tracker could not initialize from the supplied region.",
        )

    @application.exception_handler(MetadataExtractionError)
    async def invalid_study_error(_request: Request, _exc: MetadataExtractionError) -> JSONResponse:
        return error_response(
            400,
            "INVALID_STUDY_FILE",
            "The uploaded file could not be read as the declared imaging type.",
        )

    @application.exception_handler(StorageError)
    async def storage_error(_request: Request, _exc: StorageError) -> JSONResponse:
        return error_response(
            500,
            "STORAGE_ERROR",
            "Unable to store the uploaded imaging study.",
        )

    @application.exception_handler(HTTPException)
    async def http_error(_request: Request, exc: HTTPException) -> JSONResponse:
        return error_response(exc.status_code, "HTTP_ERROR", str(exc.detail))

    @application.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, _exc: RequestValidationError) -> JSONResponse:
        return error_response(422, "INVALID_REQUEST", "Invalid request.")

    @application.exception_handler(Exception)
    async def unexpected_error(_request: Request, _exc: Exception) -> JSONResponse:
        return error_response(500, "INTERNAL_ERROR", "Unexpected error.")

    return application


app = create_app()
