# GitBugs Hadoop — duplicate bug links (CC BY 4.0)

**Source:** [av9ash/gitbugs](https://github.com/av9ash/gitbugs), commit \`eadf2d6794990a1aaa26d0ae15391f29f8969301\`.

**Citation:** Patil, A. (2025). *GitBugs: Bug Reports for Duplicate Detection, Retrieval Augmented Generation, Triage, and More*, arXiv:2504.09651. The GitBugs author states **CC BY 4.0**: attribution required.

This directory holds only the small upstream numeric-ID \`duplicate-links.csv\` relation file, **after** the GitHub Actions audit confirms link format, original content checksum and ID coverage.

The full original Hadoop bug report CSV is intentionally **not** checked into public GitHub due to potential personal information in report bodies. The source remains downloadable from the pinned GitBugs commit; see \`scripts/datasets/audit_gitbugs.py\`.

See [measured audit JSON](../../../docs/data/gitbugs-hadoop-audit.json) after the workflow succeeds.

**Scientific limitation:** Missing a duplicate link does NOT prove two issues are unrelated, and a source-recorded duplicate link is not guaranteed equivalent to a single recurring support incident. Use positive links for retrieval evaluation and independently annotate negatives before reporting precision.
