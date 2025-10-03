
---

### ✅ File: `CONTRIBUTING.md`

```md
# Contributing to Avito UI Automation

This document outlines how to contribute to the Avito UI automation framework. All contributions must follow this guide to ensure consistency, quality, and fast reviews.

## 🌿 Branching

- Use **GitHub Flow**: create short-lived feature branches from `main`.
- Name branches using:  
  `type/scope-brief-description`  
  Examples:  
  - `feat/search-filters`  
  - `fix/login-timeout`  
  - `chore/update-playwright`

## 📝 Commits

- Follow **[Conventional Commits](https://www.conventionalcommits.org/)**.  
  Format: `type(scope): description`  
  Example: `feat(home): add price filter selector`
- Keep commits **small, atomic, and logical**.
- In the commit body, explain **why** the change was made.

## 📤 Pull Requests (PRs)

- PRs must:
  - Be ≤ 300 lines of changed code.
  - Include a **linked issue** (e.g., `Closes #123`).
  - Fill out the **PR template** (automatically provided).
- Required PR sections:
  - **Context**: Why this change?
  - **Changes**: Bullet list of key modifications.
  - **Testing**: How you tested (command + result). For UI changes, include **screenshots or video**.
  - **Risk & Rollout**: Any migration, rollback, or breaking notes.

## 🧪 Testing

- **Unit tests**: required for new helpers or POM logic (`tests/unit/`).
- **UI tests**: required for new P0 flows (`tests/smoke/` or feature tests).
- Run locally before pushing:
  ```bash
  # Lint & types
  ruff check . && ruff format --check .
  mypy .

  # Unit tests
  pytest tests/unit/

  # Smoke tests (requires auth bootstrap)
  pytest tests/smoke/
  ```
- **Never commit secrets** — use `.env` locally; CI uses GitHub Secrets.

## 📚 Documentation

Update these when relevant:
- `README.md` (if setup or usage changes)
- `CHANGELOG.md` (for user-facing changes)
- Add an **ADR** in `/docs/adr/` for major architectural decisions

## 👀 Reviews

- All PRs require **at least 1 approval**.
- **Critical paths** (`pages/`, `tests/`, `.github/workflows/`) enforce **CODEOWNERS** review.
- Reviewers should be **kind, specific, and actionable**.
- Authors must **respond within 1 business day** to keep PRs unblocked.

## 🚫 What Not to Do

- Don’t add raw selectors in tests (violates POM).
- Don’t skip lint/type/unit checks.
- Don’t force-push to `main`.
- Don’t merge without green CI and approval.

---

> 💡 **First-time contributor?**  
> 1. Read `README.md`  
> 2. Run `pytest tests/unit/` to verify setup  
> 3. Make a tiny PR (e.g., typo fix) to confirm CI works
```