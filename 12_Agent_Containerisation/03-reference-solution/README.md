# 03 — Reference Solution

The completed Flask API **with** a Dockerfile and `.dockerignore`.

Use this folder as the answer key after you finish Labs 2 and 3, or as a working
example if you get stuck.

## What's different from `02-flask-api/`

| File              | Added? | Purpose                                           |
|-------------------|--------|---------------------------------------------------|
| `Dockerfile`      | ✅     | Builds a container image for the Flask API       |
| `.dockerignore`   | ✅     | Keeps secrets, caches, and clutter out of image  |

All application code (`app.py`, `agent_core.py`, `sample_documents/`,
`requirements.txt`) is identical.

## Build the image

From inside this folder:

```powershell
docker build -t doc-agent:v1 .
```

## Run the container

```powershell
docker run --rm ^
  -p 5000:5000 ^
  --env-file .env ^
  --name doc-agent ^
  doc-agent:v1
```

> `--env-file .env` passes your Azure OpenAI credentials at runtime — they are
> never baked into the image.

## Test

```powershell
curl http://localhost:5000/health

curl -X POST http://localhost:5000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"What is the per diem for Bengaluru?\"}"
```

## Stop

Press `Ctrl+C` in the terminal running the container, or:

```powershell
docker stop doc-agent
```
