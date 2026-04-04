---
name: sql-skill
description: Generate, validate, and explain read-only SQLite queries for finance questions over the monthly_finance dataset.
---

# SQL Skill

Use this skill for structured finance questions that can be answered from the local SQLite dataset.

## When To Use

Use this skill when the user asks for:
- revenue, expense, or net profit values
- monthly comparisons or trends from the finance table
- totals, counts, averages, highest, or lowest values from structured data
- factual answers that can be derived from SQL alone

Do not use this skill for:
- policy-only questions
- reimbursement rules or budget rules grounded in documents
- casual chat

## Inputs

Expect these inputs:
- `question`
- `db_schema`

The relevant structured source is the local `monthly_finance` table.

## Workflow

Follow this sequence:

1. Read the user question and identify the required metric, time range, and aggregation.
2. Use the provided schema to generate exactly one SQLite `SELECT` statement.
3. Validate that the SQL is read-only and references only valid schema fields.
4. Execute the query against the local SQLite database.
5. Summarize the rows into a concise factual answer.
6. Produce evidence that includes the executed SQL and a short result summary.

## Output Contract

Produce these conceptual fields:
- `sql`
- `rows`
- `summary`
- `evidence`

Evidence must include:
- the executed SQL
- a result summary grounded in the returned rows

## Guardrails

- Generate exactly one `SELECT` statement.
- Never use `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`, `PRAGMA`, or multi-statement SQL.
- Keep answers grounded in actual query results.
- If the question cannot be answered from the schema, state that clearly instead of inventing tables or columns.

## Progressive Disclosure

Start with this file. Inspect runtime files only when exact implementation details are needed.
