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