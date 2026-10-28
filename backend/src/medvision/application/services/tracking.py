from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

from medvision.application.commands import (
    CreateTrackingSessionCommand,
    StartTrackingCommand,
)
from medvision.application.dto import TrackingRunDTO, TrackingSessionDTO
from medvision.domain.entities import (
    FrameObservation,
    TrackingRun,
    TrackingSession,
)
from medvision.domain.enums import JobStatus, ObservationSource, StudyType
from medvision.domain.exceptions import (
    InvalidTrackingStartError,
    InvalidTrackingStudyError,
    StudyNotFoundError,
    TrackingSessionNotFoundError,
)
from medvision.domain.ports import (
    StudyRepository,
    TrackerFactory,
    TrackingRunRepository,
    TrackingSessionRepository,
    VideoReaderFactory,
)


@dataclass
class CreateTrackingSessionService:
    studies: StudyRepository
    sessions: TrackingSessionRepository
    id_factory: Callable[[], UUID] = uuid4
    clock: Callable[[], datetime] = lambda: datetime.now(UTC)

    def execute(self, command: CreateTrackingSessionCommand) -> TrackingSessionDTO:
        study = self.studies.get_by_id(command.study_id)
        if study is None:
            raise StudyNotFoundError(command.study_id)
        if study.study_type is not StudyType.VIDEO:
            raise InvalidTrackingStudyError("Tracking requires a video imaging study")

        session = TrackingSession(
            id=self.id_factory(),
            study_id=study.id,
            created_at=self.clock(),
        )
        self.sessions.save(session)
        return TrackingSessionDTO.from_entity(session)


@dataclass
class StartTrackingService:
    studies: StudyRepository
    sessions: TrackingSessionRepository
    runs: TrackingRunRepository
    video_readers: VideoReaderFactory
    trackers: TrackerFactory
    id_factory: Callable[[], UUID] = uuid4
    clock: Callable[[], datetime] = lambda: datetime.now(UTC)

    def execute(self, command: StartTrackingCommand) -> TrackingRunDTO:
        session = self.sessions.get_by_id(command.session_id)
        if session is None:
            raise TrackingSessionNotFoundError(command.session_id)

        study = self.studies.get_by_id(session.study_id)
        if study is None:
            raise StudyNotFoundError(session.study_id)
        if study.study_type is not StudyType.VIDEO:
            raise InvalidTrackingStudyError("Tracking requires a video imaging study")

        reader = self.video_readers.create()
        tracker = None
        run: TrackingRun | None = None
        observations: list[FrameObservation] = []

        try:
            tracker = self.trackers.create(command.tracker_name)
            reader.open(study.storage_key, study.filename)
            metadata = reader.get_metadata()
            if command.start_frame < 0 or command.start_frame >= metadata.frame_count:
                raise InvalidTrackingStartError(
                    f"Start frame {command.start_frame} is outside video range"
                )

            initial_frame = reader.read_frame(command.start_frame)
            now = self.clock()
            run = TrackingRun(
                id=self.id_factory(),
                session_id=session.id,
                tracker_name=tracker.name,
                start_frame=command.start_frame,
                status=JobStatus.RUNNING,
                observations=(),
                created_at=now,
            )
            self.runs.save(run)

            tracker.initialize(initial_frame, command.initial_bounding_box)
            observations.append(
                FrameObservation(
                    frame_number=command.start_frame,
                    bounding_box=command.initial_bounding_box,
                    source=command.initial_source,
                    confidence=None,
                )
            )

            next_frame = command.start_frame + 1
            if next_frame < metadata.frame_count:
                for frame in reader.iter_frames(next_frame):
                    result = tracker.track(frame)
                    if not result.success or result.bounding_box is None:
                        failed = replace(
                            run,
                            status=JobStatus.FAILED,
                            observations=tuple(observations),
                            completed_at=self.clock(),
                            error_message=f"Tracker lost target at frame {frame.frame_number}",
                        )
                        self.runs.save(failed)
                        return TrackingRunDTO.from_entity(failed)

                    observations.append(
                        FrameObservation(
                            frame_number=frame.frame_number,
                            bounding_box=result.bounding_box,
                            source=ObservationSource.AUTO_TRACKED,
                            confidence=result.confidence,
                        )
                    )

            completed = replace(
                run,
                status=JobStatus.COMPLETED,
                observations=tuple(observations),
                completed_at=self.clock(),
                error_message=None,
            )
            self.runs.save(completed)
            return TrackingRunDTO.from_entity(completed)
        except Exception as exc:
            if run is not None:
                failed = replace(
                    run,
                    status=JobStatus.FAILED,
                    observations=tuple(observations),
                    completed_at=self.clock(),
                    error_message=str(exc)[:512],
                )
                self.runs.save(failed)
            raise
        finally:
            if tracker is not None:
                tracker.reset()
            reader.close()
