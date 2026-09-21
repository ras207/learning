from __future__ import annotations

import argparse
import json
from pathlib import Path

from .backends.local_git import LocalGitBackend
from .coordinator import TransactionCoordinator


def _load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="ideation-tools", description="Deterministic ideation transaction coordinator")
    sub = parser.add_subparsers(dest="command", required=True)

    apply_p = sub.add_parser("apply", help="Validate, stage, commit and verify one normalized transaction")
    apply_p.add_argument("--repo", required=True)
    apply_p.add_argument("--transaction", required=True)
    apply_p.add_argument("--context", required=True)
    apply_p.add_argument("--dry-run", action="store_true")

    rec_p = sub.add_parser("reconcile", help="Reconcile an indeterminate transaction from Git metadata")
    rec_p.add_argument("--repo", required=True)
    rec_p.add_argument("--transaction-id", required=True)
    rec_p.add_argument("--transaction-hash", required=True)
    rec_p.add_argument("--context", required=True)

    args = parser.parse_args(argv)
    coordinator = TransactionCoordinator(LocalGitBackend(args.repo))
    if args.command == "apply":
        result = coordinator.execute(_load_json(args.transaction), _load_json(args.context), dry_run=args.dry_run)
    else:
        result = coordinator.reconcile(
            transaction_id=args.transaction_id,
            transaction_hash=args.transaction_hash,
            context=_load_json(args.context),
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] in {"validated", "applied"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
