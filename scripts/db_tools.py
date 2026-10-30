"""Database maintenance helpers for local PostgreSQL / Supabase environments.

These commands use the *maintenance* connections from backend/.env (never the
runtime connection) and never print connection strings or personal data.

  apply-migration FILE   Apply one SQL migration to the runtime database
                         (LMS_MIGRATION_DATABASE_URL).
  create-test-db         Drop and recreate the isolated test database named in
                         LMS_TEST_DATABASE_URL, apply every migration in order and
                         stamp the isolation marker.  Refuses unsafe targets.
  drop-test-db           Drop the isolated test database.
  inventory              Read-only inventory of programs/applications with an
                         ownership classification (no personal data).
  cleanup-test-programs  Remove ONLY programs confirmed to be test-owned fixtures
                         (and their test applications/audit events).  Dry run
                         unless --apply is given.

Run from the repository root:
  uv run --project backend python scripts/db_tools.py <command> [options]
"""

# pyright: reportMissingImports=false
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

REPO_ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = REPO_ROOT / "supabase" / "migrations"
sys.path.insert(0, str(REPO_ROOT / "backend" / "tests" / "support"))

from database_target import (
    TEST_DATABASE_MARKER,
    UnsafeTestTargetError,
    load_environment,
    resolve_target,
)

# --- ownership rules for synthetic fixtures created by the earlier test suite ----------
TEST_SLUG = re.compile(
    r"^test-(denied|retry-flow|closure-replay|concurrent|rollback)-[0-9a-f]{6}"
    r"(-(draft|disabled|future|expired))?$"
)
TEST_TITLES = {
    "Draft Program",
    "Disabled Program",
    "Future Window Program",
    "Expired Window Program",
    "Open Test Program",
    "Camp To Close",
    "Concurrent Test Program",
    "Rollback Test Program",
}
TEST_REFERENCE_PREFIXES = ("APP-TEST-", "APP-ROLLBACK-")


def _migration_files() -> list[Path]:
    return sorted(MIGRATIONS.glob("*.sql"))


def _runtime_maintenance_url() -> str:
    url = load_environment().get("LMS_MIGRATION_DATABASE_URL", "").strip()
    if not url:
        raise SystemExit(
            "LMS_MIGRATION_DATABASE_URL is not configured in backend/.env."
        )
    return url


def _describe(url: str) -> str:
    info = psycopg.conninfo.conninfo_to_dict(url)
    return f"{info.get('host')}:{info.get('port')}/{info.get('dbname')} as {info.get('user')}"


def cmd_apply_migration(args: argparse.Namespace) -> None:
    path = Path(args.file)
    if not path.is_absolute():
        path = REPO_ROOT / path
    url = _runtime_maintenance_url()
    print(f"Applying {path.name} to {_describe(url)}")
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute(path.read_text(encoding="utf-8"))  # type: ignore[arg-type]
    print("Applied.")


def _test_target():  # type: ignore[no-untyped-def]
    try:
        target = resolve_target(load_environment())
    except UnsafeTestTargetError as error:
        raise SystemExit(f"Refusing: {error}") from error
    if target is None:
        raise SystemExit(
            "LMS_TEST_DATABASE_URL / LMS_TEST_MAINTENANCE_DATABASE_URL not set."
        )
    return target


def cmd_create_test_db(_: argparse.Namespace) -> None:
    target = _test_target()
    print(
        f"Recreating isolated test database {target.database!r} on {target.host}:{target.port}"
    )
    with psycopg.connect(
        target.maintenance_url_for("postgres"), autocommit=True
    ) as admin:
        admin.execute(
            sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(
                sql.Identifier(target.database)
            )
        )
        # UTF8 on template0: the local Windows cluster defaults to WIN1252, but Supabase and
        # the migrations are UTF-8.  The test database must be able to hold any program text.
        admin.execute(
            sql.SQL(
                "CREATE DATABASE {} ENCODING 'UTF8' TEMPLATE template0 LC_COLLATE 'C' LC_CTYPE 'C'"
            ).format(sql.Identifier(target.database))
        )
        admin.execute(
            sql.SQL("COMMENT ON DATABASE {} IS {}").format(
                sql.Identifier(target.database), sql.Literal(TEST_DATABASE_MARKER)
            )
        )
    with psycopg.connect(
        target.maintenance_url_for(target.database), autocommit=True
    ) as conn:
        for migration in _migration_files():
            print(f"  applying {migration.name}")
            conn.execute(migration.read_text(encoding="utf-8"))  # type: ignore[arg-type]
    print("Test database ready.")


def cmd_drop_test_db(_: argparse.Namespace) -> None:
    target = _test_target()
    with psycopg.connect(
        target.maintenance_url_for("postgres"), autocommit=True
    ) as admin:
        admin.execute(
            sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(
                sql.Identifier(target.database)
            )
        )
    print(f"Dropped {target.database!r}.")


def _classify(programs: list[dict], app_refs: dict) -> list[dict]:  # type: ignore[type-arg]
    """Label each program; only fully-recognised synthetic fixtures are 'test-owned'."""
    results = []
    for program in programs:
        refs = app_refs.get(program["id"], [])
        recognised = (
            bool(TEST_SLUG.fullmatch(program["slug"]))
            and program["title"] in TEST_TITLES
        )
        synthetic_content = (
            program["summary"] == "Summary" and program["description"] == "Desc"
        )
        apps_all_test = all(ref.startswith(TEST_REFERENCE_PREFIXES) for ref in refs)
        if recognised and synthetic_content and apps_all_test:
            owner = "test-owned"
        elif recognised:
            owner = "uncertain (looks like a fixture but content/applications differ)"
        else:
            owner = "retain (business or seed record)"
        results.append({**program, "applications": len(refs), "owner": owner})
    return results


def _load_programs(conn: psycopg.Connection):  # type: ignore[no-untyped-def,type-arg]
    conn.row_factory = dict_row
    programs = conn.execute(
        "SELECT id, slug, title, status, pathway, applications_enabled, summary, description, "
        "created_at FROM lms.programs ORDER BY created_at, id"
    ).fetchall()
    app_refs: dict = {}  # type: ignore[type-arg]
    for row in conn.execute(
        "SELECT program_id, reference FROM lms.enrolment_applications"
    ):
        app_refs.setdefault(row["program_id"], []).append(row["reference"])
    return _classify(programs, app_refs)


def cmd_inventory(args: argparse.Namespace) -> None:
    url = _runtime_maintenance_url()
    print(f"# Database inventory for {_describe(url)}\n")
    with psycopg.connect(url, autocommit=True) as conn:
        rows = _load_programs(conn)
        audit = conn.execute(
            "SELECT count(*) AS n FROM lms.application_audit_events"
        ).fetchone()
    published = sum(1 for r in rows if r["status"] == "published")
    print(f"Programs: {len(rows)} total, {published} published")
    print(
        f"Applications: {sum(r['applications'] for r in rows)}; audit events: {audit['n']}\n"
    )
    by_owner: dict[str, int] = {}
    for row in rows:
        by_owner[row["owner"]] = by_owner.get(row["owner"], 0) + 1
    for owner, count in sorted(by_owner.items()):
        print(f"- {owner}: {count}")
    if args.list:
        print(
            "\n| created | status | apps | owner | slug |\n| --- | --- | --- | --- | --- |"
        )
        for row in rows:
            print(
                f"| {row['created_at']:%Y-%m-%d %H:%M} | {row['status']} | {row['applications']} "
                f"| {row['owner']} | `{row['slug']}` |"
            )


def cmd_cleanup(args: argparse.Namespace) -> None:
    url = _runtime_maintenance_url()
    print(f"Target: {_describe(url)}  mode: {'APPLY' if args.apply else 'dry run'}")
    with psycopg.connect(url) as conn:  # one transaction: all-or-nothing
        owned = [r for r in _load_programs(conn) if r["owner"] == "test-owned"]
        ids = [r["id"] for r in owned]
        print(f"Confirmed test-owned programs: {len(ids)}")
        if not ids:
            return
        apps = conn.execute(
            "SELECT count(*) AS n FROM lms.enrolment_applications WHERE program_id = ANY(%s)",
            (ids,),
        ).fetchone()
        events = conn.execute(
            "SELECT count(*) AS n FROM lms.application_audit_events e "
            "JOIN lms.enrolment_applications a ON a.id = e.application_id "
            "WHERE a.program_id = ANY(%s)",
            (ids,),
        ).fetchone()
        print(f"  with {apps['n']} test applications and {events['n']} audit events")
        if not args.apply:
            print("Dry run only; re-run with --apply to delete.")
            conn.rollback()
            return
        conn.execute(
            "DELETE FROM lms.application_audit_events WHERE application_id IN "
            "(SELECT id FROM lms.enrolment_applications WHERE program_id = ANY(%s))",
            (ids,),
        )
        conn.execute(
            "DELETE FROM lms.enrolment_applications WHERE program_id = ANY(%s)", (ids,)
        )
        deleted = conn.execute("DELETE FROM lms.programs WHERE id = ANY(%s)", (ids,))
        if deleted.rowcount != len(ids):
            conn.rollback()
            raise SystemExit("Unexpected deletion count; rolled back.")
        conn.commit()
        print(f"Deleted {deleted.rowcount} programs.")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    commands = parser.add_subparsers(dest="command", required=True)
    apply_parser = commands.add_parser("apply-migration")
    apply_parser.add_argument("file")
    apply_parser.set_defaults(handler=cmd_apply_migration)
    commands.add_parser("create-test-db").set_defaults(handler=cmd_create_test_db)
    commands.add_parser("drop-test-db").set_defaults(handler=cmd_drop_test_db)
    inventory_parser = commands.add_parser("inventory")
    inventory_parser.add_argument(
        "--list", action="store_true", help="list every program"
    )
    inventory_parser.set_defaults(handler=cmd_inventory)
    cleanup_parser = commands.add_parser("cleanup-test-programs")
    cleanup_parser.add_argument("--apply", action="store_true")
    cleanup_parser.set_defaults(handler=cmd_cleanup)
    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
