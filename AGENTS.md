# AGENTS.md

Guidance for AI coding agents working in this repository.

## Tooling Rules

### 1. File discovery — use the `fff` MCP tools

Use the `fff` MCP tools for all file discovery and file search operations instead of shell commands or the default tools:

- `find_files` — find files by name, glob, or path prefix → **replaces `ls`, `find`, and `tree`**.
- `grep` — search file contents for an identifier → replaces `grep` / `rg`.
- `multi_grep` — OR-search several identifiers in one call.

Do not use `ls` or `find` to list or explore the filesystem; use `find_files` instead. Only fall back to a shell command when `fff` cannot express the operation.

### 2. Library & API knowledge — `context7` first, then `deepwiki`

When the behavior, API, configuration, or usage of a library, framework, SDK, or CLI tool is unclear, do not guess — look it up. Use the MCP documentation servers in this order:

1. **`context7` MCP** — resolve the library with `resolve-library-id`, then query it with `query-docs`. Preferred for concrete API syntax, setup/configuration, version-specific behavior, and current official examples.
2. **`deepwiki` MCP** — if `context7` has no coverage, or the question is about a GitHub repository's architecture, internals, or design rationale, use `read_wiki_structure` / `read_wiki_contents`.

Fall back to prior knowledge only when both sources are exhausted or the API is trivial and stable.

### 3. Shell commands — always use `rtk`

`rtk` is a token-optimized CLI proxy that filters and summarizes command output before it reaches the model context (up to ~90% fewer output tokens).

> **Status:** rtk's automatic hook/plugin integration does **not** support OpenCode v2 yet. Until it does, the rules in this file are the mechanism — apply the `rtk` prefix manually on every command.

**Rule:** whenever `rtk` is installed, run shell commands through its subcommands instead of the native binaries — for example `rtk git status` instead of `git status`.

> Exception: for listing and locating files, the `fff` tools from section 1 take precedence over `rtk ls` / `rtk find`. Use the `rtk` wrappers for everything else and whenever a shell command is genuinely required.

**Availability check (once per session):**

```bash
rtk --version 2>/dev/null || echo "rtk unavailable"
```

- Prints `rtk <version>` → `rtk` is available: use the `rtk` form for every command in the mapping below.
- `command not found` or non-zero exit → fall back to the native commands for the rest of the session. Do not retry `rtk` on every call.

#### Command mapping

| Native                                  | Use instead            |
| --------------------------------------- | ---------------------- |
| `ls` *(prefer `fff find_files`)*        | `rtk ls`               |
| `tree` *(prefer `fff find_files`)*      | `rtk tree`             |
| `cat`, `head`, `tail`                   | `rtk read <file>`      |
| `grep`                                  | `rtk grep <pattern>`   |
| `rg`                                    | `rtk rg <pattern>`     |
| `find` *(prefer `fff find_files`)*      | `rtk find`             |
| `wc`                                    | `rtk wc`               |
| `git …`                                 | `rtk git …`            |
| `gh …`                                  | `rtk gh …`             |
| `glab …`                                | `rtk glab …`           |
| `docker …`                              | `rtk docker …`         |
| `kubectl …`                             | `rtk kubectl …`        |
| `npm …`                                 | `rtk npm …`            |
| `npx …`                                 | `rtk npx …`            |
| `pnpm …`                                | `rtk pnpm …`           |
| `cargo …`                               | `rtk cargo …`          |
| `tsc`                                   | `rtk tsc`              |
| `eslint` / `lint`                       | `rtk lint`             |
| `prettier`                              | `rtk prettier`         |
| `jest`                                  | `rtk jest`             |
| `vitest`                                | `rtk vitest`           |
| `playwright`                            | `rtk playwright`       |
| `next build`                            | `rtk next`             |
| `prisma …`                              | `rtk prisma …`         |
| `curl …`                                | `rtk curl …`           |
| `wget …`                                | `rtk wget …`           |
| `aws …`                                 | `rtk aws …`            |
| `psql …`                                | `rtk psql …`           |
| `dotnet …`                              | `rtk dotnet …`         |
| any test runner (e.g. `cargo test`)     | `rtk test <cmd>`       |
| any command, errors/warnings only       | `rtk err <cmd>`        |
| any command, heuristic summary          | `rtk summary <cmd>`    |
| any command, unfiltered                 | `rtk proxy <cmd>`      |

#### Notes

- `rtk` subcommands pass native flags through: `rtk ls -la`, `rtk grep -i -A 3 "foo" src/`, `rtk git diff --staged` all work.
- For listing files or building a tree, prefer `fff find_files` (section 1). `rtk ls`, `rtk tree`, and `rtk find` are the shell fallback and proxy the native tools.
- Meta/analytics commands are always called directly on `rtk`: `rtk gain`, `rtk gain --history`, `rtk discover`, `rtk config`.
- If `rtk` filtering hides information you need (e.g. exact file contents with line numbers), re-run with the native command or `rtk read --level none -n`.
- Do not wrap commands that `rtk` does not support. If no rtk subcommand exists, run the native command directly.
- Do **not** rely on `rtk init --opencode`: the OpenCode hook/plugin is not supported on OpenCode v2 yet. Once support lands, the automatic rewrite can replace the manual prefixing described here.

⚠️ **Name collision:** if `rtk gain` fails, a different `rtk` (reachingforthejack/rtk, "Rust Type Kit") may be on `PATH`. Verify with `which rtk`; if it is the wrong binary, fall back to the native commands.
