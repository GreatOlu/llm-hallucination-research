# Preliminary evaluation rubric — pilot draft 1

This rubric was drafted after inspecting this pilot. Its scores are exploratory, not preregistered or independent human judgments. Confirm and freeze the rubric before the full experiment. Do not use the generating model as the sole final evaluator.

## Evidence and correctness

For answerable items, compare the requested fact with all reference answers and the original source passage. Accept semantic equivalents when they preserve the fact; document borderline decisions. Assess the entire response for additional unsupported claims, not only its first answer phrase.

Correctness labels: `correct`, `partial`, `incorrect`, `nonresponsive`, `appropriate_abstention`, `appropriate_correction`, `needs_review`. For answerable items, an unjustified abstention is incorrect. For genuinely unanswerable items, either explicit abstention or a supported correction of a false premise can be appropriate. Merely restating a nearby fact without addressing the false premise is nonresponsive.

Support labels: `supported` (all material claims supported), `partial`, `unsupported` (at least one material claim not established), `not_applicable` (no factual answer claim). In this pilot, reference support is judged against the reviewed source/evidence passages for every condition. Baseline conditions did not receive these passages; reference support does not imply they used retrieval. Unsupported-by-evidence is not proof of real-world falsehood. Do not report it as a factual hallucination rate without a finalized definition and adjudication.

Behavior labels: `answer`, `conditional_answer`, `explicit_abstention`, `premise_correction`. Abstention and correctness are separate axes: a supported correction can be successful without saying “I don't know.”

## Groundedness for RAG

For RAG conditions only, inspect all five passages actually supplied. Check each substantive claim and whether the response answers the requested relation. A grounded answer can still be nonresponsive. For non-RAG conditions, prompt-evidence groundedness is not applicable; use reference support instead.

## Ambiguous items and adjudication

Flag uncertain answerability or acceptable paraphrases. Keep raw answers, labels, and reasons. Do not silently relabel data or overwrite results. Obtain human review before treating draft scores as final. For the full study, ideally use two independent reviewers, record disagreements, and adjudicate with a written rule.

Report counts with explicit denominators. For answer accuracy use confirmed answerable questions; for appropriate handling of unanswerable questions use confirmed unanswerable questions. Report ambiguous items separately and show any exclusion. Do not infer treatment superiority from five convenience-selected questions or run significance tests on this pilot.

## Pilot decisions needing confirmation

- Kublai / tribal nobles: partial rather than fully correct; decide how precise the target concept must be.
- Rock correlation: provisionally accept biostratigraphic correlation as a semantic match; confirm consistently across both non-RAG answers.
- Plenary sessions: quarantine all four scores from aggregate correctness. Doc_0051 says NGOs and IGOs may attend as observers. The wording “participants” may permit this reading, and the question omits the institution. Re-screen this item against the corpus before the full study. Preserve the original screened label in the raw data.
