"""Create the sanitized Jjenga Code handover archive and source manifest.

Excludes developer credentials, virtual environments, node modules, build caches,
and internal run logs while bundling the full source, tests, contracts,
documentation, migrations, and verification evidence.
"""

from __future__ import annotations

import hashlib
import os
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HANDOVER_DIR = REPO_ROOT / "artifacts" / "handover"
ZIP_PATH = HANDOVER_DIR / "jjenga-code-current-progress.zip"
MANIFEST_PATH = HANDOVER_DIR / "SOURCE_MANIFEST.txt"
REPORT_PATH = HANDOVER_DIR / "PROGRESS_REPORT.md"

EXCLUDED_DIR_NAMES = {
    "node_modules",
    ".venv",
    ".nuxt",
    ".output",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".import_linter_cache",
    ".local_pg",
    ".data",
    ".git",
    ".vscode",
    "artifacts",  # Avoid self-inclusion; report & manifest are bundled explicitly
}

EXCLUDED_FILE_NAMES = {
    ".env",
    "scratch_files.txt",
    "jjenga-code-current-progress.zip",
}

EXCLUDED_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".log",
    ".zip",
}


def should_include_path(path: Path) -> bool:
    rel_parts = path.relative_to(REPO_ROOT).parts

    # Check directory exclusions
    for part in rel_parts[:-1]:
        if part in EXCLUDED_DIR_NAMES:
            return False

    # Check file exclusions
    if path.name in EXCLUDED_FILE_NAMES:
        return False

    return path.suffix not in EXCLUDED_EXTENSIONS


def collect_included_files() -> list[Path]:
    included: list[Path] = []
    for root, dirs, files in os.walk(REPO_ROOT):
        # Prune excluded directories in-place to avoid slow filesystem traversal
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIR_NAMES]

        for file in files:
            file_path = Path(root) / file
            if should_include_path(file_path):
                included.append(file_path)

    included.sort(key=lambda p: str(p.relative_to(REPO_ROOT)).replace("\\", "/"))
    return included


def write_manifest(files: list[Path]) -> None:
    manifest_lines = [
        "================================================================================",
        "JJENGA CODE LMS — SOURCE HANDOVER MANIFEST",
        "================================================================================",
        f"Archive Target: {ZIP_PATH.name}",
        "Date of Packaging: 2026-10-30",
        "",
        "SANITY AND SECURITY EXCLUSIONS:",
        "  - Credentials & Secrets: backend/.env excluded. (backend/.env.example included)",
        "  - Version Control: .git directory excluded.",
        "  - Virtual Environments: backend/.venv excluded.",
        "  - Node Dependencies: node_modules and frontend/node_modules excluded.",
        "  - Framework Build Output: frontend/.nuxt, frontend/.output excluded.",
        "  - Local Database Cluster: .local_pg cluster excluded.",
        "  - Caches & Bytecode: __pycache__, .mypy_cache, .ruff_cache, .pytest_cache excluded.",
        "  - Temporary Logs: server.log and process logs excluded.",
        "",
        "SUMMARY OF INCLUDED DIRECTORIES & ASSETS:",
        "  - backend/          : FastAPI service, configuration, domain use cases, repositories, tests",
        "  - frontend/         : Nuxt 4 application, Pinia store, components, layouts, pages, styles",
        "  - contracts/        : OpenAPI JSON contract schemas",
        "  - supabase/         : Database migrations (including receipt scoping) and seed SQL files",
        "  - scripts/          : Setup, verification, database tools, and image provenance scripts",
        "  - docs/             : Product, brand kit, architecture, assessment model, and evidence files",
        "  - tests/            : E2E Playwright test scaffolding",
        "  - Configuration     : Root & frontend package.json/lockfiles, uv.lock, pyproject.toml",
        "  - Assets            : SVG vector logos and pixel patterns in frontend/public/brand",
        "",
        "================================================================================",
        f"INCLUDED FILE INVENTORY ({len(files)} files):",
        "================================================================================",
    ]

    for p in files:
        rel_str = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
        manifest_lines.append(f"{p.stat().st_size:>8} bytes  {rel_str}")

    MANIFEST_PATH.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")


def create_zip(files: list[Path]) -> tuple[int, str]:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    with zipfile.ZipFile(
        ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
    ) as zf:
        for p in files:
            rel_path = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
            zf.write(p, arcname=rel_path)

        # Include the newly generated handover documents
        if REPORT_PATH.exists():
            zf.write(REPORT_PATH, arcname="artifacts/handover/PROGRESS_REPORT.md")
        if MANIFEST_PATH.exists():
            zf.write(MANIFEST_PATH, arcname="artifacts/handover/SOURCE_MANIFEST.txt")

    size_bytes = ZIP_PATH.stat().st_size

    # Compute SHA-256
    hasher = hashlib.sha256()
    with open(ZIP_PATH, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    sha256_hex = hasher.hexdigest()

    return size_bytes, sha256_hex


def verify_zip_integrity() -> list[str]:
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        bad_file = zf.testzip()
        if bad_file:
            raise RuntimeError(f"Zip corrupted at file: {bad_file}")
        namelist = zf.namelist()
    return namelist


def main() -> None:
    HANDOVER_DIR.mkdir(parents=True, exist_ok=True)
    files = collect_included_files()
    write_manifest(files)
    size_bytes, sha256_hex = create_zip(files)
    namelist = verify_zip_integrity()

    print(f"Archive successfully created: {ZIP_PATH}")
    print(f"Total files in archive: {len(namelist)}")
    print(f"Archive size: {size_bytes:,} bytes ({size_bytes / (1024 * 1024):.2f} MB)")
    print(f"SHA-256 checksum: {sha256_hex}")

    # Update PROGRESS_REPORT.md with final size and checksum
    report_text = REPORT_PATH.read_text(encoding="utf-8")
    import re

    report_text = re.sub(
        r"- \*\*Archive Size:\*\*.*?\n- \*\*SHA-256 Checksum:\*\*.*",
        f"- **Archive Size:** {size_bytes:,} bytes ({size_bytes / (1024 * 1024):.2f} MB)\n- **SHA-256 Checksum:** `{sha256_hex}`",
        report_text,
    )
    REPORT_PATH.write_text(report_text, encoding="utf-8")
    print("PROGRESS_REPORT.md updated with final metadata.")


if __name__ == "__main__":
    main()
