# Foundation architecture

The browser app is a React/Vite client of a versioned FastAPI backend. Backend dependencies flow inward:

`api -> application -> domain <- infrastructure`

`domain` contains immutable research entities, normalized bounding boxes, enums, and ports with no framework imports. `application` will orchestrate the later requested workflows. `infrastructure` will hold persistence, storage, imaging, tracker and model adapters. The imported desktop prototype remains at repository root as a reference and is not loaded by the browser server.

The first phase intentionally has no imaging endpoints, tables, migrations, model adapters, or patient data. A health endpoint does not imply those workflows are ready. Structured metadata will use PostgreSQL and large files will use file/object storage in their implementation phases. Model adapters will be swappable through domain/application ports. No authentication or clinical diagnosis capabilities are planned.