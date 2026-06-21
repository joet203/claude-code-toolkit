---
description: Delegate a task to OpenAI Codex CLI as a subagent
argument-hint: <prompt>
allowed-tools: [Bash, Read]
---

# Codex Subagent

Run a task using OpenAI's Codex CLI (`codex exec`) and bring the results back.

## Task

The user wants to delegate this task to Codex: $ARGUMENTS

## Instructions

1. Craft a clear, self-contained prompt for Codex. The prompt you pass is the entire instruction — Codex doesn't have conversation context. Include:
   - Relevant file paths (absolute)
   - Working directory context
   - Expected output format
   - Any specific files to create or modify

2. Run the task using the canonical command (do NOT deviate from these flags — each fixes a specific failure mode discovered in production):
```bash
codex exec --sandbox workspace-write --skip-git-repo-check -o /tmp/codex-output.md -C "<working-dir>" "<prompt>" < /dev/null
```

3. Read the output file and present the results to the user.

## ⚠️ Required flags (don't omit any of these)

| Flag | Why it's required |
|---|---|
| `--sandbox workspace-write` | The canonical sandbox mode for auto-approval. **`--full-auto` is deprecated** (emits a warning and may break in future codex versions). |
| `--skip-git-repo-check` | Codex refuses to run outside a git repo with "Not inside a trusted directory and --skip-git-repo-check was not specified." Always include this — even when `-C` points to a git repo, it's harmless. |
| `< /dev/null` | **Closes stdin.** Without this, codex emits "Reading additional input from stdin..." and may hang waiting for piped input that never comes. The redirect tells codex stdin is empty. |
| `-o /tmp/codex-FOO.md` | Captures final answer to a file (avoids stdout truncation; can be Read later). |
| `-C <dir>` | Codex's working root. Always set explicitly. |

## Optional flags

- `-m <MODEL>` — override model (e.g., `-m o3`, `-m gpt-5.5`)
- `--json` — full event stream as JSONL (use when you need the transcript, not just the final answer)
- `-i <FILE>` — attach images to the prompt (visual context)
- `--add-dir <DIR>` — give codex access to additional directories beyond `-C`

## For long-running or parallel tasks

Background mode prevents your turn from blocking. Each task needs a unique output filename:

```bash
codex exec --sandbox workspace-write --skip-git-repo-check \
  -o /tmp/codex-task1.md -C ~/project-a "<prompt1>" < /dev/null &
codex exec --sandbox workspace-write --skip-git-repo-check \
  -o /tmp/codex-task2.md -C ~/project-b "<prompt2>" < /dev/null &
wait
```

Or run via the Bash tool's `run_in_background: true` if available.

## Error handling

If `codex exec` fails, check stderr. Common issues and fixes:

| Error | Cause | Fix |
|---|---|---|
| `command not found: codex` | PATH doesn't include `/opt/homebrew/bin` in the spawned shell | Use full path: `/opt/homebrew/bin/codex` |
| `Reading additional input from stdin...` (hangs) | Stdin not closed | Add `< /dev/null` to the command |
| `Not inside a trusted directory and --skip-git-repo-check was not specified.` | `-C` points outside a git repo | Add `--skip-git-repo-check` (always include it as a default) |
| `--full-auto is deprecated` (warning) | Old flag | Replace with `--sandbox workspace-write` |
| `Not logged in` | Need auth | `codex login` (user must run interactively) |
| `Model unavailable` | Account doesn't have access | Try `-m o4-mini` or `-m o3` |
| `Permission denied` writing outside workspace | Sandbox limits | `--sandbox danger-full-access` (confirm with user first) |

## Important

- Use unique output filenames per call to avoid collisions
- Codex file changes are real — scoped to the working directory it can write
- For tasks needing writes outside the workspace, confirm with the user before using `--sandbox danger-full-access`
- If running on a Mac and `which codex` returns nothing, use the full path `/opt/homebrew/bin/codex` (the brew cask installs there)
