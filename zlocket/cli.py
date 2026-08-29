"""Command-line interface for the safe workflow simulator."""

from __future__ import annotations

import argparse
import json
import sys
from threading import Lock
from typing import Sequence

from . import __version__
from .config import RunConfig
from .mock import MockAppCheckProvider, MockAuthAdapter, MockLocketApiAdapter, MockState
from .workflow import WorkflowRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zlocket",
        description=(
            "Offline simulator for the historical zLocket workflow. "
            "This build does not connect to Locket, Firebase, or token brokers."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", help="explicitly select offline mode")
    parser.add_argument("--environment", choices=("mock",), default="mock")
    parser.add_argument("--accounts", type=int, default=1)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="total simulated friend requests per mock account",
    )
    parser.add_argument("--target", default="test_receiver", dest="target_uid")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = RunConfig(
            environment=args.environment,
            accounts=args.accounts,
            threads=args.threads,
            repeat=args.repeat,
            target_uid=args.target_uid,
            seed=args.seed,
        )
    except ValueError as exc:
        parser.error(str(exc))

    state = MockState()
    output_lock = Lock()

    def event_sink(message: str) -> None:
        if args.json_output:
            return
        with output_lock:
            print(f"[DRY-RUN] {message}")

    if not args.json_output:
        print("zLocket workflow simulator")
        print("Mode: offline mock (network disabled by design)")
        print(
            f"Plan: {config.accounts} account(s) x {config.repeat} request(s) "
            f"using {min(config.threads, config.accounts)} worker(s)"
        )

    runner = WorkflowRunner(
        config=config,
        app_check_provider=MockAppCheckProvider(),
        auth=MockAuthAdapter(state),
        api=MockLocketApiAdapter(state),
        event_sink=event_sink,
    )
    summary = runner.run()

    if args.json_output:
        json.dump(summary.to_dict(), sys.stdout, ensure_ascii=False, sort_keys=True)
        sys.stdout.write("\n")
    else:
        print(
            "[DRY-RUN] Complete: "
            f"accounts={summary.accounts_created}, "
            f"profiles={summary.profiles_finalized}, "
            f"requests={summary.requests_accepted}/{summary.requests_attempted}, "
            f"duration={summary.duration_ms}ms"
        )
        print("[DRY-RUN] No external network requests were sent.")
    return 0
