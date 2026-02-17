---
name: commit
description: Commit and push latest changes to remote
disable-model-invocation: true
allowed-tools: Bash(git *)
argument-hint: [optional message override]
---

# Commit and Push

Commit all current changes and push to remote.

## Steps

1. Run `git status` (no -uall flag) to see changed/untracked files
2. Run `git diff` to see staged and unstaged changes
3. Run `git log --oneline -5` to see recent commit message style
4. Stage relevant files by name (never `git add -A` or `git add .` — avoid secrets and binaries)
5. Draft a concise commit message:
   - If `$ARGUMENTS` is provided, use it as the message
   - Otherwise, summarize the changes (1-2 sentences focusing on "why")
   - End with: `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`
6. Commit using a HEREDOC for the message
7. Run `git push`
8. Run `git status` to verify clean state

## Rules

- NEVER use `--force`, `--no-verify`, or `--amend` unless explicitly requested
- NEVER commit `.env`, credentials, or secrets — warn if asked
- Always create NEW commits, never amend
- Use HEREDOC format for commit messages
- If pre-commit hook fails, fix the issue and create a NEW commit
