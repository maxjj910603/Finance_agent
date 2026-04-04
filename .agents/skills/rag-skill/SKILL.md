---
name: rag-skill
description: Use for document-grounded finance policy questions such as reimbursement rules, payment applications, approval thresholds, sign-off requirements, required attachments, what is allowed, what is forbidden, and budget or procurement procedures from local policy documents.
---

# RAG Skill

Use this skill for finance policy, reimbursement, approval, or budget-rule questions that should be answered from local documents.

## When To Use

Use this skill for:
- reimbursement rules
- budget approval requirements
- policy interpretation
- document-grounded finance procedures

Do not use this skill for:
- pure SQL questions
- casual chat
- freeform unsupported advice

## Inputs

Expect these inputs:
- `question`
- retrieved chunk candidates from the vector store

The relevant source is the local finance policy document corpus embedded in the vector database.

## Workflow

Follow this sequence:

1. Read the user question and identify the relevant finance policy topic.
2. Convert the question into an embedding using the configured embedding model.
3. Query the vector store for the top relevant chunks.
4. Inspect the retrieved chunks and determine whether they are sufficient to support an answer.
5. If a retrieved chunk directly states the answer, use that rule, amount, deadline, or approver list directly.
6. Draft a concise answer that stays grounded in the retrieved text.
7. Produce evidence that cites the document source and the relevant chunk snippets.

## Output Contract

Produce these conceptual fields:
- `answer`
- `citations`
- `evidence`

Evidence should include:
- document source
- chunk-based snippets or metadata

## Guardrails

- Retrieval must be embedding-based.
- Answers must stay grounded in retrieved chunks.
- If evidence is weak, say `insufficient evidence`.
- Do not say `insufficient evidence` when a retrieved chunk already contains a directly applicable rule.
- For approval, reimbursement, deadline, allowance, threshold, and procurement questions, extract the exact rule from the retrieved text.
- Cite document names or chunk-derived snippets in evidence.

## Progressive Disclosure

Start with this file. Inspect runtime files only when exact implementation details are needed.
