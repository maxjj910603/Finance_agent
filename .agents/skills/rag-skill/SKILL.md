---
name: rag-skill
description: Retrieve and summarize finance policy evidence from embedded document chunks stored in the local vector database.
---

# RAG Skill

Use this skill for finance policy, reimbursement, approval, or budget-rule questions that should be answered from local documents.

## Scope

Use this skill for:
- chunk-based retrieval from embedded policy documents
- grounded summarization from retrieved chunks
- document evidence generation

Do not use this skill for:
- pure SQL questions
- casual chat
- freeform unsupported advice

## Data Source

The finance RAG source is the local policy document corpus embedded into the vector database.

## Rules

- Retrieval must be embedding-based.
- Answers must stay grounded in retrieved chunks.
- If evidence is weak, say `insufficient evidence`.
- Cite document names or chunk-derived snippets in evidence.

## Output Contract

Produce these conceptual fields:
- `answer`
- `citations`
- `evidence`

## Progressive Disclosure

Start with this file. Inspect runtime files only when exact implementation details are needed.
