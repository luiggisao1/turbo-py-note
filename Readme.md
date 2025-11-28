# turbo-py-note

A small Django project that implements a notes API with authentication. This README documents the project, how I approached adding tests for the `authentication` and `notes` apps, key design and technical decisions, and which AI tools were used during development.

---

## Project summary

This repository contains a Django application (project name: `turbo_py_note`) split into two primary apps:

- `authentication` — handles user registration, login and token-based authentication (or other auth flows depending on implementation).
- `notes` — exposes CRUD endpoints for note resources protected by authentication.

The goal of recent work was to add unit tests for both apps and to make those tests easy to generate and iterate on using an AI-assisted workflow.

## Quick start

Prerequisites
- Python 3.11+ (project indicates use of Python 3.13 cache files; adapt as needed)
- pip (or a virtualenv tool)
- PostgreSQL (the project expects a PostgreSQL database; a `docker-compose.yml` is included to run a local Postgres instance)

Set up a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run migrations and start the development server:

```bash
python manage.py migrate
python manage.py runserver
```

Run tests:

```bash
python manage.py test
```

## Using Docker (PostgreSQL)

This repository includes `docker-compose.yml` to run a local PostgreSQL instance (service name: `db`).

- starts the `db` service via Docker Compose,
- waits for PostgreSQL to become ready,
- runs Django migrations on the host environment.

Usage (from the project root):

```bash
docker compose up -d
```

After that you can run the Django development server locally (it will connect to the Postgres instance exposed on `localhost:5432`):

```bash
python manage.py runserver
```

## Development process
The implementation followed a clear, iterative process that emphasized authentication and data integrity first, and finally test coverage:
1. **Authentication first**: I started by implementing user registration and login endpoints in the `authentication` app. This included models, serializers, and views to handle user creation and token issuance.
2. **Notes CRUD**: Next, I implemented the `notes` app with models, serializers, and views to allow authenticated users to create, read, update, and delete notes.
3. **Testing**: Finally, I focused on adding unit tests for both apps. This involved writing tests for authentication flows (registration, login, token validation) and CRUD operations on notes, ensuring that only authenticated users could access their own notes.


## Key design & technical decisions
- **Django REST Framework**: I chose Django REST Framework (DRF) for building the API due to its robust features for serialization, authentication, and viewsets, which streamline API development.
- **Token-based authentication**: I implemented token-based authentication to secure the API endpoints, allowing
users to authenticate via tokens for each request.
- **Modular app structure**: By separating authentication and notes into distinct apps, I maintained a clean and modular codebase that is easier to manage and extend.
- **AI-assisted testing**: I leveraged AI tools to help generate and iterate on unit tests quickly, allowing for a more efficient testing process and better coverage.

## AI tools used and how I used them

- I used an AI coding assistant (copilot) to help generate the initial test scaffolding and iterate on tests quickly. The AI was used to:
  - Generate unit test templates for typical flows (user creation, login, permission checks, CRUD for notes).
  - Suggest helper functions and fixtures to reduce repetition in tests.
  - Propose edge-case tests (e.g., unauthorized access, invalid payloads).

- The AI output was reviewed and adapted to match the project's existing conventions and models/serializers. Tests were validated by running the Django test runner and making small corrections where necessary.

- Additionally, the AI agent suggested ideas and phrasing for this README itself (structure, headings, and wording), which I reviewed and adjusted.
