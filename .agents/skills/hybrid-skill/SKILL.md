---
name: hybrid-skill
description: Use when the question needs both structured finance metrics from SQLite and policy evidence from documents, such as asking for a month or amount together with reimbursement rules, approval requirements, payment sign-off, attachment requirements, or budget procedures.
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
- `sql_answer`
- `rag_answer`
- `sql_evidence`
- `rag_evidence`

## Workflow

Follow this sequence:

1. Assume the orchestrator has already decomposed the original hybrid question into one SQL sub-question and one policy sub-question.
2. Receive the resulting SQL answer and RAG answer from the two skills.
3. Review the SQL answer and keep only the factual finance result grounded in SQL evidence.
4. Review the RAG answer and keep only the grounded policy statement from document evidence.
5. Combine the SQL answer and the policy answer into one concise response.
6. Produce evidence that includes both SQL and document support.

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
- Do not try to re-decompose the question inside this skill; decomposition happens upstream in the orchestrator.
- Do not say the whole hybrid question lacks evidence just because the document does not answer the SQL portion.
- Do not say the whole hybrid question lacks evidence just because SQL does not answer the policy portion.
- When the document contains a directly applicable policy rule, use it even if the SQL part of the question is unrelated to that rule.

## Progressive Disclosure

Start with this file. Inspect runtime files only when exact implementation details are needed.
