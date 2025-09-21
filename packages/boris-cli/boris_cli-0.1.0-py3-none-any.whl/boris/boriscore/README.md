# CodeChat Studio – Backend (FastAPI)

> **Single‑source‑of‑truth:** SQLite

---

## ✨ What is CodeChat Studio?

CodeChat Studio is an AI‑assisted coding playground.  The backend is a **FastAPI** application that exposes a REST/JSON API, persists projects in SQLite, and serves the built React SPA from the same process.  The agent layer (`CodeWriter`) calls OpenAI under the hood to reason about and generate code.

---

## 🗺️ Project Structure

```
app/
 ├── backend/
 │   ├── main.py            # FastAPI entry‑point
 │   ├── models/            # Pydantic request/response DTOs
 │   ├── repository/        # SQLite access layer (ProjectRepo)
 │   ├── code_structurer/   # CodeProject & ProjectNode abstractions
 │   ├── agent/             # Reasoning pipeline, toolboxes
 │   └── prompts/
 │       └── prompts.py
 │
 ├── frontend/              # React app (built & served statically)
 │   └── build/             # Created by `npm run build`
 │
 └── assets/
     ├── projects.sqlite3   # Production DB (auto‑created)
     └── sql/
         └── project_schema.sql
```

---

## ⚙️ Tech Stack & Key Packages

| Purpose                                  | Package                                                    |
| ---------------------------------------- | ---------------------------------------------------------- |
| Web framework                            | **fastapi**                                                |
| ASGI server (dev)                        | **uvicorn**                                                |
| Runtime type enforcement & serialization | **pydantic** (indirect via FastAPI)                        |
| CORS                                     | **fastapi.middleware.cors**                                |
| Database                                 | Built‑in **sqlite3** driver + thin **ProjectRepo** wrapper |
| Static file serving                      | **starlette.staticfiles**                                  |
| Logging                                  | **logging** stdlib                                         |
| UUIDs                                    | **uuid** stdlib                                            |
| Date handling                            | **datetime** stdlib                                        |
| Agent / LLM                              | **openai** (imported inside `CodeWriter`)                  |

> All dependencies are pinned in `pyproject.toml` / `requirements.txt`.

---

## 🔑 Authentication (Mock)

* Stateless bearer token, **not secure for production**.
* Endpoints:

  * `POST /api/auth/register` – `{username, password}` → 201
  * `POST /api/auth/login` – exchanges credentials for `access_token`.
    The token is `token-{username}` and stored in memory (cleared on restart).
* Clients must send `Authorization: Bearer <token>`.

---

## 📚 API Reference

### Projects

| Method       | Path                           | Body / Query                                              | Response         | Notes                                                                     |
| ------------ | ------------------------------ | --------------------------------------------------------- | ---------------- | ------------------------------------------------------------------------- |
| GET          | `/api/projects`                | –                                                         | `ProjectDTO[]`   | List user projects                                                        |
| POST         | `/api/projects?name=`          | –                                                         | `ProjectDTO`     | Create empty project                                                      |
| POST         | `/api/projects/import`         | **multipart/form‑data**: JSON export produced by *export* | `ProjectDTO`     | Re‑imports a CodeChat JSON dump                                           |
| **NEW** POST | `/api/projects/upload_project` | **multipart/form‑data**: `folder=<file.zip>`              | `ProjectDTO`     | *Mock*. Accepts a zipped folder, creates a project using the archive name |
| GET          | `/api/projects/{id}/tree`      | –                                                         | `ProjectNodeDTO` | Whole project tree                                                        |
| DELETE       | `/api/projects/{id}`           | –                                                         | 204              | Remove project                                                            |

### Chat

| Method | Path        | Body                            | Response            |                                                 |
| ------ | ----------- | ------------------------------- | ------------------- | ----------------------------------------------- |
| POST   | `/api/chat` | `{history[], project_id, user}` | `{answer, project}` | Forwards conversation to the LLM + updates tree |

### Misc

* `GET /api/health` → `{status:"ok"}` – readiness probe.

---

## 🏗️ Database

* **SQLite** file at `assets/projects.sqlite3` (auto‑created on first run).
* Schema is applied from `assets/sql/project_schema.sql`.
* ORM‑less; `ProjectRepo` does direct SQL and returns dict rows.
* Backups are cheap: copy the `.sqlite3` file.

---

## 🚀 Local Development

```bash
# 1. Python ≥ 3.10
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. (Optional) build frontend
cd app/frontend
npm install && npm run build
cd ../..

# 3. Run the backend (reload on save)
uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000

# Visit http://localhost:8000/docs for interactive OpenAPI
```

### Environment Variables

| Name              | Purpose                        | Default |
| ----------------- | ------------------------------ | ------- |
| `PORT`            | Uvicorn port                   | `8000`  |
| `ALLOWED_ORIGINS` | CORS allow‑list (comma‑sep)    | `*`     |
| `LOG_LEVEL`       | Root log level                 | `INFO`  |
| `OPENAI_API_KEY`  | Needed if you enable the agent | –       |

Add them via an `.env` file or your container orchestrator.

---

## 🐳 Docker

> The repository includes a sample `Dockerfile` (Alpine‑based).  Adjust as needed.

```dockerfile
FROM python:3.11-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# build React (if not pre‑built)
RUN apk add --no-cache npm && \
    cd app/frontend && npm install && npm run build && cd ../..
EXPOSE 8000
CMD ["uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build & run:

```bash
docker build -t codechat-backend .
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... codechat-backend
```

---

## 🏢 Production Deployment

* Use **Gunicorn** with **UvicornWorker** for multi‑worker concurrency:

  ```bash
  gunicorn app.backend.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000}
  ```
* Place the SQLite file on fast SSD; or switch to Postgres by replacing `ProjectRepo`.
* Terminate TLS & serve the React build via an external reverse proxy (Nginx, Caddy, Traefik).
* Tighten CORS and replace mock auth with OAuth2 / JWT before going live.

---

## 📝 Testing

```bash
pytest -q
```

Unit tests cover repository ops and the upload‑project mock.

---

## 🛣️ Roadmap

* Replace mock auth with JWT & refresh tokens
* Implement real folder unarchiving → tree building in `/upload_project`
* Switch DB driver to SQLModel for stricter types
* CI pipeline (lint, test, Docker build)

---

## 📄 License

MIT – see `LICENSE` file.
