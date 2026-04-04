---
name: hybrid-skill
description: Combine structured finance facts from SQL with grounded policy evidence from document retrieval.
---

# Hybrid Skill

Use this skill when a finance question requires both SQL facts and document policy context.

## Scope

Use this skill for:
- combining SQL results with document evidence
- reconciling metrics with policy rules
- producing one final grounded answer

Do not use this skill for:
- pure SQL questions
- pure RAG questions
- casual chat

## Rules

- Keep SQL facts and document rules clearly separated in reasoning.
- Do not invent policy rules from SQL.
- Do not invent metrics from documents.
- If one side lacks evidence, say so explicitly.

## Output Contract

Produce these conceptual fields:
- `answer`
- `evidence`

## Progressive Disclosure

Start with this file. Inspect runtime files only when exact implementation details are needed.
