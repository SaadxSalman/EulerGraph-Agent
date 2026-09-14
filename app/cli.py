import argparse
import asyncio
import json
from pathlib import Path

from .config import get_settings
from .graph import EulerGraph
from .ingest import document_from_file, split_sections


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="eulergraph", description="Operate the EulerGraph-Agent local mathematical knowledge system.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    ask = subparsers.add_parser("ask", help="Run a query through the reasoning graph")
    ask.add_argument("query")
    ask.add_argument("--mode", choices=("auto", "proof", "compute", "explain"), default="auto")
    ingest = subparsers.add_parser("ingest", help="Index a Markdown, text, or LaTeX file")
    ingest.add_argument("path", type=Path)
    ingest.add_argument("--author", default="Imported document")
    ingest.add_argument("--kind", default="reference")
    ingest.add_argument("--chunk-size", type=int, default=2400)
    subparsers.add_parser("stats", help="Print local corpus statistics")
    return parser


def main() -> None:
    from .models import SolveRequest

    args = build_parser().parse_args()
    engine = EulerGraph(get_settings())
    if args.command == "ask":
        result = asyncio.run(engine.solve(SolveRequest(query=args.query, mode=args.mode)))
        print(json.dumps(result.model_dump(mode="json"), indent=2))
    elif args.command == "ingest":
        source = document_from_file(args.path, args.author, args.kind)
        indexed = [engine.retriever.ingest(chunk) for chunk in split_sections(source, args.chunk_size)]
        print(json.dumps({"indexed": len(indexed), "ids": [item.id for item in indexed]}, indent=2))
    else:
        print(json.dumps(engine.retriever.stats().model_dump(), indent=2))


if __name__ == "__main__":
    main()
