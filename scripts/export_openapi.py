"""Export the API contract without loading developer secrets or opening a database."""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.bootstrap import create_app
from app.config import Settings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    destination = PROJECT_ROOT / "contracts/api/v1/openapi.json"
    content = (
        json.dumps(
            create_app(
                Settings(
                    _env_file=None,
                    environment="test",
                    database_url=None,
                    database_sslrootcert=None,
                    cors_origins=[],
                )
            ).openapi(),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    if arguments.check:
        if (
            not destination.exists()
            or destination.read_text(encoding="utf-8") != content
        ):
            print("API snapshot is stale. Run npm run contracts:generate.")
            return 1
        print("API snapshot matches the FastAPI schema.")
        return 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    print("Exported contracts/api/v1/openapi.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
