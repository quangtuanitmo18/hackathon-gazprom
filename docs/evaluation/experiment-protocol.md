# Experimental protocol — preregistration draft

**No measurements have been made. Never present a formula or synthetic scenario as observed outcomes.**

## Hypotheses
H1 hybrid BM25+dense retrieval improves Recall@5 vs each individually on held-out Russian technical tickets.
H2 constrained pair verification reduces false merges compared with cosine threshold.
H3 AI-assisted human triage saves minutes **including correction/review**, without unacceptable correctness loss.
H4 chronological replay finds actionable problems sufficiently early, while reporting missed incidents.

## Evidence preparation
Collect permissioned, anonymized source data and annotate ticket intent/product/component separately from same_incident / related_topic / different / uncertain pairs. Two reviewers on an overlap, adjudication, hard negatives, class balance, sparse/singleton tickets. Synthetic samples = demonstration, not independent real-world accuracy evidence.

## Leakage prevention
Holdout untouched until final; temporal split where possible, dedup overlapping problems, use only arrival-time data in replay, never use final resolution/root cause as model input. Preserve provenance and label uncertainty.

## Baselines
Classification: majority/rule, TF-IDF+logistic regression, embedding or LLM fallback.
Matching: exact codes and BM25; dense nearest neighbors; hybrid + metadata constraints + pair verification.

## Metrics
Macro F1 (class); Recall@5/10 (retrieval); pairwise P/R/F1, B-cubed and false-merge examples (clustering); alert precision, important-incident recall, detection latency (signals); evidence validity and correct team (agent). Report abstention coverage and model failure count.

## Chronological replay
Sort by timestamp and stable ID. Feed only currently known tickets. Record first_seen_at, detected_at, report_created_at, accepted_at **when observed**. TTAI = accepted_at - first_seen_at, with undetected/unaccepted denominator shown separately. If historic manual escalation timestamp absent, do NOT claim manual TTAI comparison.

## Human experiment
Balanced ticket sets, randomized/counterbalanced manual vs AI-assisted order, distinct cases per participant, record start/finish, corrections, false routing and final quality. If testers are students, label as laboratory proxy; never call it Gazprom Neft support staff productivity.

## Reproducibility gate
Each published figure has run_id, dataset license/checksum, git SHA, split/seed, model versions, hardware, full duration, token logs, 95% CI when appropriate, limitations. Negative results are acceptable and must be reported. No external write actions during evaluation.
