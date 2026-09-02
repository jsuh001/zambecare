import argparse
import json
from datetime import datetime
from pathlib import Path

from zambecare_ingestion.config import Settings
from zambecare_ingestion.loaders.oracle import OracleLoader
from zambecare_ingestion.pipeline import run_file, run_postgres


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="ZambeCare Phase 3 ingestion")
    subparsers = result.add_subparsers(dest="command", required=True)
    for command in ("fhir", "facility-csv"):
        item = subparsers.add_parser(command)
        item.add_argument("--file", type=Path, required=True)
        item.add_argument("--validate-only", action="store_true")
    postgres = subparsers.add_parser("postgres-patient")
    postgres.add_argument("--start", type=datetime.fromisoformat, required=True)
    postgres.add_argument("--end", type=datetime.fromisoformat)
    postgres.add_argument("--validate-only", action="store_true")
    subparsers.add_parser("oracle-check")
    return result


def main() -> None:
    args = parser().parse_args()
    needs_settings = args.command == "postgres-patient" or not args.validate_only
    settings = Settings() if needs_settings else None
    if args.command == "oracle-check":
        output = [OracleLoader(settings).healthcheck()]
    elif args.command == "postgres-patient":
        output = run_postgres(settings, args.start, args.end, args.validate_only)
    else:
        output = run_file(args.file, args.command, settings, args.validate_only)
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
