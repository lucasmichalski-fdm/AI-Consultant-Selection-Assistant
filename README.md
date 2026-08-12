# AI-Consultant-Selection-Assistant

## Backend HTTP API (No Database)

The API is file-backed and reads from CSV + writes optional run artifacts to `outputs/*.json`.

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run API

```bash
python scripts/run_api.py
```

Server starts on `http://localhost:8000`.

### Endpoints

- `GET /health`
- `GET /roles`
- `POST /rank`
- `POST /rank/save`
- `GET /runs`
- `GET /runs/{request_id}`

### Example request

```bash
curl -X POST http://localhost:8000/rank \
	-H "Content-Type: application/json" \
	-d '{"role_id":"R-003","top_n":5,"retrieve_k":25,"save_output":true}'
```

## Frontend Live Mode

In `frontend/.env`, set:

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK_DATA=false
```