# FarmMateNZ
FarmMateNZ is a local development project with a Vue/Vite frontend, a FastAPI backend, and a local DynamoDB development database.

This README documents the project setup and verified development flow as of 16 August 2026.

# 1. Project Structure
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

# 2. Prerequisites

Install the following:

Python 3.12 or compatible Python version
Docker Desktop
Task
Node.js and npm
Git

Check installations:
python3 --version
docker --version
task --version
node --version
npm --version
The project documentation specifies Python 3.12. The current development environment has also been successfully tested with Python 3.13.3.

# 3. Clone the Repository
git clone <repository-url>
cd FarmMateNZ
If the repository is already cloned:
cd FarmMateNZ
git pull origin main

# 4. Backend Python Environment

The project uses a local virtual environment called .venv.

Create the environment:
python3 -m venv .venv
Install dependencies:
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r backend/requirements.txt
Or use the Taskfile:
task setup

Verify:
.venv/bin/python --version
Check that boto3 is installed:
.venv/bin/python -c "import boto3; print(boto3.__version__)"
Use .venv/bin/python for project commands. This ensures that the correct project dependencies are used.

# 5. Start DynamoDB Local

FarmMateNZ uses DynamoDB Local for development.

The configuration is located at:
docker/docker-compose.yml
Start DynamoDB:
task dev:services
This starts:
Container: farmmatenz-dynamodb-local
Port:      8000
Endpoint:  http://localhost:8000
Check that it is running:
docker ps
You should see:
farmmatenz-dynamodb-local

Alternative Docker command
You can also start it directly:
docker compose -f docker/docker-compose.yml up -d

# 6. Create and Seed DynamoDB

After DynamoDB Local is running:
task py:DynamoDB
This runs:
.venv/bin/python db/init_dynamodb.py
The current development setup creates a placeholder table:
Farms
and inserts three sample records.
Expected output:
Created table 'Farms'.
Seeded 3 item(s) into 'Farms'.
Current sample data
farm-001  Sunnyside Dairy    Waikato        120 hectares
farm-002  Green Valley Farm  Canterbury      85 hectares
farm-003  Coastal Pastures   Bay of Plenty    60 hectares

The Farms table is currently a placeholder. The final data model will be implemented when the project's database schema is finalized.

# 8. FastAPI Backend

The FastAPI application is located at:
backend/app/main.py
Start FastAPI:
.venv/bin/uvicorn backend.app.main:app --reload --port 8001
The API will be available at:
http://127.0.0.1:8001

# 9. Frontend

The frontend uses Vue/Vite.
Go to the frontend directory:
cd frontend
Install dependencies:
npm install
Start the development server:
npm run dev
Vite will display the local URL, normally:
http://localhost:5173



 # following insturciton was added by Linden only for dynamodb setup. I have included this things above too

## Prerequisites

- [Python 3.12](https://www.python.org/downloads/)
- [Task](https://taskfile.dev/#/installation)
- [Docker](https://docs.docker.com/get-docker/) (required to run DynamoDB locally)

## Installing Dependencies

Once the prerequisites are installed, `cd` into the project's root directory and run `task setup` to install the required packages.

```bash
# Navigate to the root directory
cd /path/to/project

# Use the Taskfile to install dependencies
task setup
```

## DynamoDB

The Taskfile has two commands that need to be run, in order, to bring up the development environment with DynamoDB.

```bash
# Starts DynamoDB Local in Docker. Pulls the image on first run if it isn't installed yet.
task dev:services

# Generates the tables and seeds simulation data in the DB.
task py:DynamoDB
```

DynamoDB Local is then reachable at `http://localhost:8000`. The table schema is currently just a
`Farms` placeholder (see [`db/init_dynamodb.py`](db/init_dynamodb.py)) — swap in the real data model
once it's decided.

To stop DynamoDB Local when you're done:

```bash
task dev:services:down
```

### Verifying the data

To confirm the DB actually got seeded, run [`db/query_farms.py`](db/query_farms.py), which scans and
prints every item in the `Farms` table:

```bash
.venv/bin/python db/query_farms.py
```

Use `.venv/bin/python` (not plain `python`) — that's the virtualenv `task setup` created, and it's
the one with `boto3` installed.
