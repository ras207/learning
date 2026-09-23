from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .approval import build_approval_requests
from .approvers import DEFAULT_APPROVERS_PATH, add_approver, dump_approvers, load_approvers
from .backends.local_git import LocalGitBackend
from .coordinator import TransactionCoordinator
from .errors import ValidationRejected
from .passkey import PasskeyApprovalVerifier, build_authorization


def _load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _approval_command(args) -> int:
    if args.command == "request-approval":
        page_url = args.page_url or load_approvers(Path(args.approvers))["approval_page_url"]
        requests = build_approval_requests(_load_json(args.transaction), page_url=page_url)
        print(json.dumps(requests, indent=2, sort_keys=True))
        return 0
    if args.command == "attach-approval":
        context_path = Path(args.context)
        context = _load_json(args.context)
        if context.get("trust_mode") != "passkey":
            raise ValidationRejected("Context must use trust_mode 'passkey'")
        issued_at = _utc_now().isoformat().replace("+00:00", "Z")
        auth, entry = build_authorization(_load_json(args.transaction), args.approval, load_approvers(Path(args.approvers)),
                                          issued_at=issued_at)
        others = [a for a in context["human_authorizations"] if a["authorization_id"] != auth["authorization_id"]]
        context["human_authorizations"] = [*others, auth]
        context_path.write_text(json.dumps(context, indent=2) + "\n", encoding="utf-8")
        print(f"Valid approval from {entry['approver']} ({entry['fingerprint']}) for {auth['authorization_id']}")
        return 0
    path = Path(args.approvers)
    updated, entry = add_approver(load_approvers(path), args.record, added_at=_utc_now().date().isoformat())
    path.write_text(dump_approvers(updated), encoding="utf-8")
    print(json.dumps({k: entry[k] for k in ("approver", "fingerprint", "credential_id")}, indent=2))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="ideation-tools", description="Deterministic ideation transaction coordinator")
    sub = parser.add_subparsers(dest="command", required=True)

    apply_p = sub.add_parser("apply", help="Validate, stage, commit and verify one normalized transaction")
    apply_p.add_argument("--repo", required=True)
    apply_p.add_argument("--transaction", required=True)
    apply_p.add_argument("--context", required=True)
    apply_p.add_argument("--dry-run", action="store_true")
    apply_p.add_argument("--approvers", default=str(DEFAULT_APPROVERS_PATH))

    rec_p = sub.add_parser("reconcile", help="Reconcile an indeterminate transaction from Git metadata")
    rec_p.add_argument("--repo", required=True)
    rec_p.add_argument("--transaction-id", required=True)
    rec_p.add_argument("--transaction-hash", required=True)
    rec_p.add_argument("--context", required=True)
    rec_p.add_argument("--approvers", default=str(DEFAULT_APPROVERS_PATH))

    req_p = sub.add_parser("request-approval", help="Build human approval requests for a transaction")
    req_p.add_argument("--transaction", required=True)
    req_p.add_argument("--page-url", help="Approval page URL (default: approval_page_url in the approvers file)")
    req_p.add_argument("--approvers", default=str(DEFAULT_APPROVERS_PATH))

    att_p = sub.add_parser("attach-approval", help="Verify an approval code from the approval page and add it to a context")
    att_p.add_argument("--transaction", required=True)
    att_p.add_argument("--context", required=True)
    att_p.add_argument("--approval", required=True, help="Approval code copied from the approval page")
    att_p.add_argument("--approvers", default=str(DEFAULT_APPROVERS_PATH))

    add_p = sub.add_parser("add-approver", help="Add a phone registered on the approval page to the approvers file")
    add_p.add_argument("--record", required=True, help="Registration code copied from the approval page")
    add_p.add_argument("--approvers", default=str(DEFAULT_APPROVERS_PATH))

    args = parser.parse_args(argv)
    try:
        if args.command in {"request-approval", "attach-approval", "add-approver"}:
            return _approval_command(args)
        # The CLI only ever accepts passkey-verified human approvals.
        verifier = PasskeyApprovalVerifier(Path(args.approvers))
        coordinator = TransactionCoordinator(LocalGitBackend(args.repo), context_verifier=verifier)
        if args.command == "apply":
            result = coordinator.execute(_load_json(args.transaction), _load_json(args.context), dry_run=args.dry_run)
        else:
            result = coordinator.reconcile(
                transaction_id=args.transaction_id,
                transaction_hash=args.transaction_hash,
                context=_load_json(args.context),
            )
    except ValidationRejected as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] in {"validated", "applied"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
