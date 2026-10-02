from typing import cast

from fastapi import Request

from medvision.application.services import CreateStudyService, StudyCatalogService


def get_create_study_service(request: Request) -> CreateStudyService:
    return cast(CreateStudyService, request.app.state.create_study_service)


def get_study_catalog_service(request: Request) -> StudyCatalogService:
    return cast(StudyCatalogService, request.app.state.study_catalog_service)
