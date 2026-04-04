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
- `sql_question`
- `policy_question`
- `sql_result`
- `rag_result`

## Workflow

Follow this sequence:

1. Read the user question and identify what must come from SQL versus what must come from documents.
2. Split the hybrid question into one SQL sub-question and one policy sub-question.
3. For the structured-data side, follow the `sql-skill` workflow to obtain factual finance results for the SQL sub-question.
4. For the document side, follow the `rag-skill` workflow to obtain grounded policy evidence for the policy sub-question.
5. Review the SQL result and extract the relevant factual finance values.
6. Review the RAG result and extract the relevant policy statements.
7. Answer the SQL sub-question from SQL evidence and the policy sub-question from document evidence.
8. Keep the SQL answer and the policy answer clearly separated before combining them into one response.
9. Make the relationship between data facts and policy rules explicit.
10. Produce evidence that includes both SQL and document support.

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
- Always decompose a hybrid question before running SQL and RAG.
- Do not say the whole hybrid question lacks evidence just because the document does not answer the SQL portion.
- Do not say the whole hybrid question lacks evidence just because SQL does not answer the policy portion.
- When the document contains a directly applicable policy rule, use it even if the SQL part of the question is unrelated to that rule.

## Progressive Disclosure

Start with this file. Inspect runtime files only when exact implementation details are needed.
