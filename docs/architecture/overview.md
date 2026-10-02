# Foundation architecture

The browser app is a React/Vite client of a versioned FastAPI backend. Backend dependencies flow inward:

`api -> application -> domain <- infrastructure`

`domain` contains immutable research entities, normalized bounding boxes, enums, and ports with no framework imports. `application` will orchestrate the later requested workflows. `infrastructure` will hold persistence, storage, imaging, tracker and model adapters. The imported desktop prototype remains at repository root as a reference and is not loaded by the browser server.

Study ingestion now includes a versioned upload/list/detail API, a framework-independent creation/catalog service, local file storage, an in-memory repository, and allowlisted metadata readers for video, image, NIfTI, and DICOM sources. Uploaded files live beneath generated study IDs; original filenames are returned only as metadata. Metadata is process-local and is lost on API restart. PostgreSQL tables/migrations, viewers, tracking, inference, model adapters, and export remain future phases. No authentication or clinical diagnosis capabilities are planned.