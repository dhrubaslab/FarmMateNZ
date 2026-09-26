# FarmMateNZ

FarmMateNZ is a local development project with a Vue/Vite frontend, a FastAPI backend, and a local DynamoDB development database.

## Project structure

```
FarmMateNZ/
├── backend/
│   ├── app/
│   │   └── main.py
│   └── requirements.txt
├── db/
│   ├── init_dynamodb.py
│   └── query_farms.py
├── docker/
│   └── docker-compose.yml
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
├── Taskfile.yml
└── README.MD
```

## Prerequisites

- [Python 3.12](https://www.python.org/downloads/) (3.13.3 also tested and working)
- [Docker Desktop](https://docs.docker.com/get-docker/) — required to run DynamoDB locally
- [Task](https://taskfile.dev/#/installation)
- Node.js and npm
- Git

Verify installs:

```bash
python3 --version
docker --version
task --version
node --version
npm --version
```

## 1. Clone the repo

```bash
git clone <repository-url>
cd FarmMateNZ
```

Already cloned? Just pull the latest:

```bash
git pull origin main
```

## 2. Set up the Python environment

The project uses a local virtualenv at `.venv`. Easiest way:

```bash
task setup
```

Or manually:

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r backend/requirements.txt
```

Verify:

```bash
.venv/bin/python --version
.venv/bin/python -c "import boto3; print(boto3.__version__)"
```

Always use `.venv/bin/python` for project commands — it's the interpreter with the right dependencies installed.

## 3. Start DynamoDB Local

```bash
task dev:services
```

This starts the `farmmatenz-dynamodb-local` container, exposed at `http://localhost:8000`.

Confirm it's running:

```bash
docker ps
```

Alternative, without Task:

```bash
docker compose -f docker/docker-compose.yml up -d
```

To stop it later:

```bash
task dev:services:down
```

## 4. Create and seed the database

```bash
task py:DynamoDB
```

This runs `db/init_dynamodb.py`, which creates a placeholder `Farms` table and seeds sample records:

| Farm ID  | Name              | Region        | Size (ha) |
|----------|-------------------|---------------|-----------|
| farm-001 | Sunnyside Dairy   | Waikato       | 120       |
| farm-002 | Green Valley Farm | Canterbury    | 85        |
| farm-003 | Coastal Pastures  | Bay of Plenty | 60        |

> The `Farms` table is a placeholder — the real schema will replace it once finalized.

**Verify seeding worked:**

```bash
.venv/bin/python db/query_farms.py
```

This scans and prints every item in the `Farms` table.

## 5. Start the backend (FastAPI)

```bash
.venv/bin/uvicorn backend.app.main:app --reload --port 8001
```

API available at: `http://127.0.0.1:8001`

## 6. Start the frontend (Vue/Vite)

```bash
cd frontend
npm install
npm run dev
```

Vite will print the local URL — normally `http://localhost:5173`.
