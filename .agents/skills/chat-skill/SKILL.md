---
name: chat-skill
description: Use only for greetings, casual conversation, or general non-finance small talk. Do not use for finance data, reimbursement rules, payment applications, approval thresholds, sign-off, required attachments, or policy questions.
---

# Chat Skill

Use this skill for casual conversation, greetings, or general assistant-style interaction.

## When To Use

Use this skill when the user:
- says hello
- asks a general conversational question
- is not asking for finance table results or policy interpretation

Do not use this skill for:
- structured finance questions
- document-grounded finance policy questions
- hybrid questions that need data and policy together

## Inputs

Expect these inputs:
- `question`

## Workflow

Follow this sequence:

1. Read the user message.
2. Decide whether it is general conversation rather than a finance task.
3. Answer directly in Traditional Chinese.
4. Keep the reply concise and helpful.

## Output Contract

Produce these conceptual fields:
- `answer`
- `evidence`

For chat, evidence should normally be empty.

## Guardrails

- Do not invent SQL results or policy claims.
- Do not mention routing or internal tools unless the user asks.
- Keep the response brief and natural.

## Progressive Disclosure

Start with this file. Inspect runtime files only when exact implementation details are needed.
