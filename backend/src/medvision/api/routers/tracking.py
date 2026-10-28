from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from medvision.api.dependencies import (
    get_create_tracking_session_service,
    get_start_tracking_service,
    get_tracking_catalog_service,
)
from medvision.api.schemas import (
    StartTrackingRequest,
    TrackingRunResponse,
    TrackingSessionResponse,
)
from medvision.application.commands import (
    CreateTrackingSessionCommand,
    StartTrackingCommand,
)
from medvision.application.services import (
    CreateTrackingSessionService,
    StartTrackingService,
    TrackingCatalogService,
)

router = APIRouter(prefix="/api/v1", tags=["tracking"])


@router.post(
    "/studies/{study_id}/tracking-sessions",
    response_model=TrackingSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tracking_session(
    study_id: UUID,
    service: Annotated[
        CreateTrackingSessionService,
        Depends(get_create_tracking_session_service),
    ],
) -> TrackingSessionResponse:
    result = service.execute(CreateTrackingSessionCommand(study_id=study_id))
    return TrackingSessionResponse.model_validate(result)


@router.get(
    "/studies/{study_id}/tracking-sessions",
    response_model=list[TrackingSessionResponse],
)
def list_tracking_sessions(
    study_id: UUID,
    service: Annotated[TrackingCatalogService, Depends(get_tracking_catalog_service)],
) -> list[TrackingSessionResponse]:
    return [
        TrackingSessionResponse.model_validate(session)
        for session in service.list_sessions(study_id)
    ]


@router.get(
    "/tracking-sessions/{session_id}",
    response_model=TrackingSessionResponse,
)
def get_tracking_session(
    session_id: UUID,
    service: Annotated[TrackingCatalogService, Depends(get_tracking_catalog_service)],
) -> TrackingSessionResponse:
    return TrackingSessionResponse.model_validate(service.get_session(session_id))


@router.post(
    "/tracking-sessions/{session_id}/runs",
    response_model=TrackingRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_tracking_run(
    session_id: UUID,
    request: StartTrackingRequest,
    service: Annotated[StartTrackingService, Depends(get_start_tracking_service)],
) -> TrackingRunResponse:
    result = service.execute(
        StartTrackingCommand(
            session_id=session_id,
            tracker_name=request.tracker_name,
            start_frame=request.start_frame,
            initial_bounding_box=request.initial_bounding_box.to_domain(),
            initial_source=request.initial_source,
        )
    )
    return TrackingRunResponse.model_validate(result)


@router.get(
    "/tracking-sessions/{session_id}/runs",
    response_model=list[TrackingRunResponse],
)
def list_tracking_runs(
    session_id: UUID,
    service: Annotated[TrackingCatalogService, Depends(get_tracking_catalog_service)],
) -> list[TrackingRunResponse]:
    return [
        TrackingRunResponse.model_validate(run)
        for run in service.list_runs(session_id)
    ]


@router.get(
    "/tracking-runs/{run_id}",
    response_model=TrackingRunResponse,
)
def get_tracking_run(
    run_id: UUID,
    service: Annotated[TrackingCatalogService, Depends(get_tracking_catalog_service)],
) -> TrackingRunResponse:
    return TrackingRunResponse.model_validate(service.get_run(run_id))
