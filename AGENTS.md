# AGENTS.md

## Project
Finance Agent

## Mission
Build a local runnable finance assistant MVP for question answering with four routes:
- `chat`
- `sql`
- `rag`
- `hybrid`

The system must return:
- final answer
- selected route
- evidence

## In Scope
- Natural language finance questions
- Local LLM route selection
- SQL querying over local finance data
- True RAG with embedding-based retrieval
- Local CLI demo

## Out of Scope
- Multi-agent orchestration
- ERP or accounting system integration
- Authentication, authorization, SSO
- Cloud deployment
- Non-MVP workflows

## Architecture
Use one orchestrator and three skills.

- `orchestrator`: receives the user question, asks the LLM to choose a route, dispatches execution, and normalizes output
- `sql_skill`: generates safe read-only SQL, executes it, and summarizes results
- `rag_skill`: chunks finance policy documents, retrieves grounded evidence, and drafts an answer
- `hybrid_skill`: combines SQL facts and RAG evidence into one answer

## Routing Contract
The LLM route decision must return strict JSON:

```json
{
  "route": "chat|rag|sql|hybrid",
  "reason": "short reason",
  "confidence": 0.0
}
```

Fallback rules:
- If route output is invalid or unavailable, default to `hybrid`.

## Skill Contracts

### `sql_skill`
- Input: `{ question, db_schema }`
- Output: `{ sql, rows, summary, evidence }`
- Constraint: SQL must be `SELECT` only.

### `rag_skill`
- Input: `{ question, retrieved_chunks }`
- Output: `{ answer, citations, evidence }`
- Constraint: retrieval must come from embedded document chunks.

### `hybrid_skill`
- Input: `{ question, sql_result, rag_result }`
- Output: `{ answer, evidence }`

## Answer Contract
Every response must include:
- `answer`
- `route`
- `evidence`

Evidence policy:
- Chat: no evidence required
- SQL: executed SQL plus result summary
- RAG: document filename plus retrieved chunk snippets
- Hybrid: both SQL and RAG evidence

## Guardrails
- Never fabricate citations or SQL results.
- If evidence is insufficient, state `insufficient evidence`.
- SQL execution is read-only.
- RAG retrieval must be embedding-based.
- Keep retrieval and answer generation grounded in local data only.

## Engineering Rules
- Keep modules small and single-purpose.
- Use explicit schemas for I/O contracts.
- Separate ingestion/indexing from query-time retrieval.
- Add tests for routing, SQL safety, retrieval, and orchestrator integration.

## MVP Acceptance Criteria
- Supports local CLI interaction.
- Correctly routes finance questions to `chat`, `sql`, `rag`, or `hybrid`.
- Can answer at least one question from SQLite, one from RAG, and one hybrid question.
- Builds or refreshes a vector index from the finance policy document.
- Returns traceable evidence in every non-chat answer.
