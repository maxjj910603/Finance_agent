# Finance Agent

Local runnable finance assistant MVP with four routes:
- `chat`
- `sql`
- `rag`
- `hybrid`

## What It Does

- Routes each question to one of the four modes with a strict JSON route contract.
- Answers from local SQLite data for structured finance questions.
- Answers from local embedded policy chunks for document-grounded questions.
- Combines SQL facts and RAG evidence for hybrid questions.
- Returns `answer`, `route`, and `evidence` on every request.

## Project Layout

- `app/orchestrator.py`: route selection and execution dispatch
- `app/skills/`: chat, SQL, RAG, and hybrid execution logic
- `app/services/db.py`: local SQLite setup and read-only querying
- `app/services/ingestion.py`: chunking and vector ingestion
- `app/services/retriever.py`: embedding-based retrieval
- `app/main.py`: local CLI entrypoint

## Requirements

- Python 3.11+
- Local Ollama server for generation and embeddings
- A model for text generation, default `qwen2.5:7b-instruct`
- An embedding model, default `qllama/bge-small-zh-v1.5:latest`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

One-shot mode:

```bash
python -m app.main --once "What is the highest net profit month?" --json
```

Interactive CLI:

```bash
python -m app.main
```

## Test

```bash
python -m unittest discover -s tests -v
```

## Notes

- If route JSON is invalid or unavailable, the orchestrator defaults to `hybrid`.
- SQL execution is read-only and constrained to `SELECT`.
- RAG retrieval is grounded in the local vector store only.
