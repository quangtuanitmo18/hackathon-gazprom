# Mermaid GitHub parse error — critical self-review (2026-10-31)

**Input:** user screenshot shows `Unable to render rich display` for section 4 in `docs/diagrams/README.md`. The error points to sequence message line `M-->>A: proposed intent, topic, symptom; not a diagnosis` and then complains about the next `I->>A` arrow.

## Root cause verified
Mermaid sequence syntax interprets literal semicolons as markup statement separators. Official documentation explains using `#59;` to escape a semicolon in message text: https://mermaid.js.org/syntax/sequenceDiagram . After `;` in the source, `not a diagnosis` became an invalid standalone statement. **No business logic or source PDF fact was wrong.**

## Changes
1. `docs/diagrams/feedback-sequence.mmd`: replace `symptom; not a diagnosis` with `symptom (not a diagnosis)` to avoid special syntax entirely.
2. `docs/diagrams/README.md`: synchronize exact four Mermaid preview fences against canonical source files; fourth fence now matches.
3. `scripts/validate_case_submission.py`: static guard for unescaped semicolon in sequence arrow messages. All original 15,000-character, PDF, 24 documented scenarios, seven original examples and financial checks retained.
4. `scripts/validate_mermaid.mjs`: add **actual Mermaid parser** on all four diagrams, not just textual matching.
5. `.github/workflows/webneft-case-docs.yml`: configure Node 22 and `mermaid@11.12.1` + `jsdom@26.1.0` from temporary install. jsdom is necessary because Mermaid's flowchart parser sanitizes labels through DOMPurify and fails in a bare Node process.

## Verification
- First real-parser run [41193648208](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41193648208) **FAILED** in three flowchart parser calls with `TypeError: purify.addHook is not a function`; sequence diagram **PASSED**. The failure was a **test harness DOM setup issue**, not evidence flowcharts had invalid grammar.
- Corrected run [41193711390](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41193711390) **SUCCESS** on `8b56cc364aaf966827a5de771a1f80b389a4ad6a`: parser logs show `c4-containers.mmd (flowchart-v2)`, `data-flow-trust-boundaries.mmd (flowchart-v2)`, `agent-workflow.mmd (flowchart-v2)`, `feedback-sequence.mmd (sequence)`. Python check confirms four source/gallery blocks synchronized.
- All changes documentation / documentation CI only. No application source changes, Qwen inference, external AI APIs, merge or deployment.
- **Residual limitation:** GitHub browser visual layout and Cyrillic legibility have not been independently screenshot-verified at the user's resolution. Parser validation demonstrates accepted Mermaid grammar, NOT end-user visual rendering quality.

**Status:** author self-review, not independent approval. Draft PR #24 remains open, no merge/deploy.
