---
name: sql-skill
description: Generate, validate, and explain read-only SQLite queries for finance questions over the monthly_finance dataset.
---

# SQL Skill

Use this skill for structured finance questions that can be answered from the local SQLite dataset.

## Scope

Use this skill for:
- generating a read-only SQLite query
- validating SQL safety
- summarizing query results
- producing SQL evidence

Do not use this skill for:
- document-only questions
- casual chat
- schema or data modification

## Data Source

The finance SQL source is the local `monthly_finance` table. Schema and seed details belong to the runtime implementation.

## Rules

- Generate exactly one `SELECT` statement.
- Never use `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`, or multi-statement SQL.
- Keep answers grounded in actual query results.
- If the question cannot be answered from the schema, say so rather than inventing columns or tables.

## Output Contract

Produce these conceptual fields:
- `sql`
- `rows`
- `summary`
- `evidence`

## Progressive Disclosure

Start with this file. Inspect runtime files only when exact implementation details are needed.
