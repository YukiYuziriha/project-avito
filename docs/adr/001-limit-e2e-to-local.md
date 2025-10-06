# 001 - Limit End-to-End UI Tests to Local Execution & Scope to One Core Flow

## Status  
Accepted

## Context  
The project charter originally defined three P0 end-to-end scenarios on Avito.ru:  
- Buyer: search → filter → open ad  
- Seller: post ad with image  
- Engagement: favorite + message seller  

However, Avito.ru employs aggressive anti-bot measures:  
- CAPTCHA and SMS verification on login  
- IP-based firewalling (CI IPs are blocked immediately)  
- Session state is ephemeral (~hours), large (~250 KB), and unsafe to commit  
- No public sandbox, test API, or reset mechanism for ads or messages  

These constraints make **reliable automation of seller and engagement flows impractical** for a public portfolio project. Even local execution requires manual CAPTCHA/SMS resolution and produces non-idempotent, unverifiable results.

## Decision  
- ✅ **Only the buyer journey** (`search → filter → open ad`) is implemented as a **working, repeatable, locally runnable P0 test**.  
- ❌ **Seller (post ad) and engagement (favorite + message) flows are intentionally excluded** — not due to effort, but due to **inherent testability limits** on Avito.ru.  
- ✅ **CI runs only static checks**: lint (`ruff`), type-check (`mypy`), unit tests, and a **logged-out smoke check** (if homepage loads).  
- 📄 This scope boundary is **explicitly documented** in `README.md` and this ADR.

## Consequences  
### Positive  
- Deliverable is **realistic, runnable, and verifiable** by reviewers (clone → bootstrap → run one test).  
- Framework demonstrates **professional judgment**: prioritizing **maintainable, demonstrable automation** over checkbox compliance.  
- Avoids shipping **fragile, unverifiable code** that reviewers cannot validate.  
- Frees time to build **two additional portfolio pieces on testable platforms** (e.g., saucedemo, practice.expandtesting.com), which **do** prove full E2E capability.

### Negative  
- Does not fulfill the *letter* of the original Project Plan.  
- May appear “incomplete” to a superficial reviewer.

### Mitigations  
- README clearly explains **why** only one flow is automated, framing it as a **strength** (realism, risk awareness).  
- Codebase still includes **full POM structure**, `login_factory`, auth reuse, and CI hygiene — proving architectural competence.  
- This project is **one of three** in the portfolio; the other two will demonstrate full E2E on cooperative sites.

## References  
- Observed behavior: Avito blocks headless logins from GitHub Actions IPs (Oct 2025)  
