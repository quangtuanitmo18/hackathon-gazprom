# Superpowers plan — Fix GitHub Mermaid sequence parse error

**Date:** 2026-10-31. **Scope:** documentation-only correction on Draft PR #24. User screenshot confirms Mermaid parse error in Feedback Sequence block of docs/diagrams/README.md.

## Root cause verified against Mermaid docs
- Sequence message `M-->>A: proposed intent, topic, symptom; not a diagnosis` contains an unescaped `;`.
- Mermaid treats `;` as a statement separator. GitHub parser interprets `not a diagnosis` as a new statement and fails near next arrow.
- Mermaid documentation prescribes `#59;` to escape a literal semicolon. Here, replace it with ordinary parentheses to avoid a complex escape.

## Implementation and review checklist
- [ ] Replace **only** the offending message in the canonical `docs/diagrams/feedback-sequence.mmd`.
- [ ] Update the inlined Mermaid code fence in `docs/diagrams/README.md` exactly from the corrected source, preserving the other 3 diagrams.
- [ ] Add a targeted regression guard to the source validator: sequence diagram must have no unescaped semicolon inside message text. Keep existing 4-block gallery-to-source exact sync validation.
- [ ] Run GitHub Actions on exact HEAD and inspect job logs, not older CI. Distinguish source-check pass from actual Mermaid engine parsing.
- [ ] Author self-review in Draft PR #24 (COMMENT only), with screenshot finding, Mermaid docs link, source readback and remaining independent visual verification. Do not merge or deploy.

**Out of scope:** model code, financial metrics, slides, or live product team delivery.
