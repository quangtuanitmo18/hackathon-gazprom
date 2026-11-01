# Superpowers plan — Fix GitHub Mermaid sequence parse error

**Date:** 2026-10-31. **Scope:** documentation-only correction on Draft PR #24. User screenshot confirms Mermaid parse error in Feedback Sequence block of docs/diagrams/README.md.

## Root cause verified against Mermaid docs
- Sequence message `M-->>A: proposed intent, topic, symptom; not a diagnosis` contains an unescaped `;`.
- Mermaid treats `;` as a statement separator. GitHub parser interprets `not a diagnosis` as a new statement and fails near next arrow.
- Mermaid documentation prescribes `#59;` to escape a literal semicolon. Here, replace it with ordinary parentheses to avoid a complex escape.

## Implementation and review checklist
- [x] Replace **only** the offending message in the canonical `docs/diagrams/feedback-sequence.mmd`.
- [x] Update the inlined Mermaid code fence in `docs/diagrams/README.md` exactly from the corrected source, preserving the other 3 diagrams.
- [x] Add a targeted regression guard to the source validator: sequence diagram must have no unescaped semicolon inside message text. Keep existing 4-block gallery-to-source exact sync validation.
- [x] Run GitHub Actions on exact HEAD and inspect job logs, not older CI. Distinguish source-check pass from actual Mermaid engine parsing.
- [ ] Author self-review in Draft PR #24 (COMMENT only), with screenshot finding, Mermaid docs link, source readback and remaining independent visual verification. Do not merge or deploy.

**Out of scope:** model code, financial metrics, slides, or live product team delivery.

## Verified implementation — 2026-10-31

- Canonical message changed to `M-->>A: proposed intent, topic, symptom (not a diagnosis)` without unescaped `;`.
- GitHub inline diagram now matches canonical `.mmd` exactly.
- Python source check protects against unescaped semicolons and checks 4-source/gallery identity.
- **Improved CI to run the actual Mermaid 11.12.1 parser** on each diagram, with Node 22 and jsdom 26.1.0 (required for DOMPurify's flowchart sanitizer). First experimental CI failed because Node lacked a DOM, not because of Mermaid grammar; follow-up fixed parser setup.
- [Actions run #41193711390](https://github.com/quangtuanitmo18/hackathon-gazprom/actions/runs/41193711390): **SUCCESS** on `8b56cc364aaf966827a5de771a1f80b389a4ad6a`, logs show `flowchart-v2` x3 and `sequence` x1 PASS.
- True visual/layout inspection in the **user's GitHub browser** is still a separate gate; parser success strongly suggests screenshot's reported parse error is resolved but is not a screenshot of GitHub UI.
