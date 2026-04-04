from __future__ import annotations

import argparse
import json
import sys

from app.orchestrator import Orchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Finance Agent CLI")
    parser.add_argument("--once", type=str, help="Run one question and exit", default=None)
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser


def print_pretty(result: dict) -> None:
    print("\n=== Finance Agent ===")
    print(f"Route: {result['route']}")
    print(f"Answer: {result['answer']}")
    if result["evidence"]:
        print("Evidence:")
        for item in result["evidence"]:
            print(f"- [{item['type']}] {item['source']} :: {item['detail']}")


def run_once(orchestrator: Orchestrator, question: str, as_json: bool) -> None:
    result = orchestrator.ask(question).to_dict()
    if as_json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        print_pretty(result)


def run_repl(orchestrator: Orchestrator, as_json: bool) -> None:
    if not sys.stdin.isatty():
        print("Interactive mode requires a real terminal. Use --once for non-interactive shells.")
        return

    print("Finance Agent CLI")
    print("Type your question. Use 'exit' to quit.\n")

    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            print("\nInput stream closed. Use --once in non-interactive environments.")
            return
        if question.lower() in {"exit", "quit"}:
            print("bye")
            return
        if not question:
            continue
        run_once(orchestrator, question, as_json)


def main() -> None:
    args = build_parser().parse_args()
    orchestrator = Orchestrator()

    if args.once:
        run_once(orchestrator, args.once, args.json)
        return

    run_repl(orchestrator, args.json)


if __name__ == "__main__":
    main()
