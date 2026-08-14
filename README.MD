# FarmMateNZ

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
