# Finance Agent

Local runnable finance assistant MVP with four routes:
- `chat`
- `sql`
- `rag`
- `hybrid`

## What It Does

- Routes each question to one of the four modes with an internal strict JSON route contract between the orchestrator and the route-selection LLM.
- Answers from local SQLite data for structured finance questions.
- Answers from local embedded policy chunks for document-grounded questions.
- Decomposes hybrid questions into an SQL sub-question and a policy sub-question before combining the results.
- Returns `answer`, `route`, and `evidence` on every request.

## Project Layout

- `app/orchestrator.py`: route selection, hybrid question decomposition, and execution dispatch
- `app/schemas.py`: shared response, evidence, routing, and hybrid question data structures
- `app/skills/`: chat, SQL, RAG, and hybrid execution logic
- `app/services/llm_client.py`: route classification, hybrid decomposition, SQL drafting, and answer generation
- `app/services/db.py`: local SQLite setup and read-only querying
- `app/services/embeddings.py`: local embedding generation through Ollama
- `app/services/ingestion.py`: chunking and vector ingestion
- `app/services/retriever.py`: embedding-based retrieval
- `app/services/vector_store.py`: local vector storage and similarity query
- `app/services/skill_registry.py`: loads skill metadata and instructions from `.agents/skills/`
- `.agents/skills/`: skill descriptions and runtime instruction files for chat, SQL, RAG, and hybrid flows
- `app/main.py`: local CLI entrypoint

## Requirements

- Python 3.11+
- Local Ollama server for generation and embeddings
- A model for text generation, default `qwen2.5:7b-instruct`
- An embedding model, default `qllama/bge-small-zh-v1.5:latest`

Note:
- `requirements.txt` installs Python dependencies only.
- Ollama and the required local models must already be installed on the machine.

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

On first run:
- the app seeds the local SQLite database under `data/db/` if it does not exist yet
- the app builds the local vector index under `data/vector_store/` if it is empty

## Test

```bash
python -m unittest discover -s tests -v
```

## Notes

- On startup, the app seeds the local SQLite database if it is empty.
- On startup, the app builds the local vector index from root-level `.txt` documents if the vector store is empty.
- If route JSON is invalid or unavailable, the orchestrator defaults to `hybrid`.
- Hybrid questions are decomposed into `sql_question` and `policy_question` before the two skills run.
- SQL execution is read-only and constrained to `SELECT`.
- RAG retrieval is grounded in the local vector store only, using embedding retrieval with `top_k=3`.
- The current ingestion defaults are `chunk_size=150` and `chunk_overlap=30`.
- Runtime artifacts under `data/db/` and `data/vector_store/` are intentionally not committed; they are rebuilt locally when needed.
