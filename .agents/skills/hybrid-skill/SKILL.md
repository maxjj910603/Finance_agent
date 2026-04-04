---
name: hybrid-skill
description: Combine structured finance facts from SQL with grounded policy evidence from document retrieval.
---

# Hybrid Skill

Use this skill when a finance question requires both SQL facts and document policy context.

## When To Use

Use this skill for:
- a financial metric plus policy interpretation
- current numbers plus reimbursement or approval rules
- a decision-style answer that depends on both data and documents

Do not use this skill for:
- pure SQL questions
- pure RAG questions
- casual chat

## Inputs

Expect these inputs:
- `question`
- `sql_result`
- `rag_result`

## Workflow

Follow this sequence:

1. Read the user question and identify what must come from SQL versus what must come from documents.
2. For the structured-data side, follow the `sql-skill` workflow to obtain factual finance results.
3. For the document side, follow the `rag-skill` workflow to obtain grounded policy evidence.
4. Review the SQL result and extract the relevant factual finance values.
5. Review the RAG result and extract the relevant policy statements.
6. Combine both into one grounded answer.
7. Make the relationship between data facts and policy rules explicit.
8. Produce evidence that includes both SQL and document support.

## Output Contract

Produce these conceptual fields:
- `answer`
- `evidence`

Evidence must include:
- SQL query and SQL result summary
- document source and relevant snippets

## Guardrails

- Keep SQL facts and document rules clearly separated in reasoning.
- Do not invent policy rules from SQL.
- Do not invent metrics from documents.
- If one side lacks evidence, say so explicitly.

## Progressive Disclosure

Start with this file. Inspect runtime files only when exact implementation details are needed.
