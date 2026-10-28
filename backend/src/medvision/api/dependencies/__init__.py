from typing import cast

from fastapi import Request

from medvision.application.services import (
    CreateStudyService,
    CreateTrackingSessionService,
    StartTrackingService,
    StudyCatalogService,
    TrackingCatalogService,
)


def get_create_study_service(request: Request) -> CreateStudyService:
    return cast(CreateStudyService, request.app.state.create_study_service)


def get_study_catalog_service(request: Request) -> StudyCatalogService:
    return cast(StudyCatalogService, request.app.state.study_catalog_service)


def get_create_tracking_session_service(request: Request) -> CreateTrackingSessionService:
    return cast(
        CreateTrackingSessionService,
        request.app.state.create_tracking_session_service,
    )


def get_start_tracking_service(request: Request) -> StartTrackingService:
    return cast(StartTrackingService, request.app.state.start_tracking_service)


def get_tracking_catalog_service(request: Request) -> TrackingCatalogService:
    return cast(TrackingCatalogService, request.app.state.tracking_catalog_service)
