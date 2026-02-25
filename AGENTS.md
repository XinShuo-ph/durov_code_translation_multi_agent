# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

This is a Python-based multi-agent translation coordination system for the "Durov Code Book". There is no web server, database, or Docker dependency. All tools are CLI-based Python scripts in `tools/`.

### Running the tools

All three tools are documented in `README.md` and `tools/README.md`. Key commands:

- **Coordination**: `python3 tools/coord.py [--fetch] <command>` (status, next, check, claim, done, review-queue, heartbeat, collect)
- **Validation**: `python3 tools/validate_translation.py [--strict] <json_files...>`
- **PDF compilation**: `python3 tools/compile_pages.py <json_file> <output_dir>` (requires optional XeLaTeX + CJK fonts)

### Non-obvious caveats

- `coord.py status` only scans **remote** branches for completed pages (via `git ls-tree`). Local-only translations won't appear in status until pushed.
- `coord.py --fetch` triggers `git fetch origin --prune` before scanning. Omit `--fetch` when network access is unavailable or not needed.
- The `done` command both validates and marks a page complete in `WORKER_STATE.json`. Always prefer `done` over manual state updates.
- PDF compilation via `compile_pages.py` requires `texlive-xetex`, `texlive-lang-chinese`, and `fonts-noto-cjk` system packages (not installed by the update script; install manually if PDF output is needed).
- Python packages install to user site-packages (`~/.local/lib/python3.12`). No virtualenv is used.

### Linting and testing

There is no formal test suite or linter configuration in this repository. To verify Python code correctness:

- Syntax check: `python3 -m py_compile tools/<script>.py`
- Validate example translations: `python3 tools/validate_translation.py examples/*.json`
