# Five-question pilot: provisional review

All 20 planned responses completed. The two RAG conditions used the same five document IDs for each question. Raw results remain unchanged. This is an AI-assisted draft requiring human confirmation, not a final evaluation.

## Implementation and usage

The revised pilot used gpt-6-luna, HybridRetriever top_k=5 (RRF k=60; candidate_k=10), and a 1,000-token output cap. Selection used the first three answerable and first two screened unanswerable items. Two answerable items share doc_0040, so the pilot has limited topic diversity.

| Condition | Input tokens | Output tokens |
|---|---:|---:|
| baseline | 111 | 2431 |
| hallucination_aware | 286 | 2066 |
| rag | 5044 | 449 |
| rag_hallucination_aware | 5219 | 667 |

Revised pilot total: 10,660 input and 5,613 output tokens. Including the separate failed 200-token attempt: 10,683 input and 5,813 output tokens. Output usage includes reasoning tokens; no monetary cost is inferred.

## Exploratory observations

- Both RAG conditions correctly identified the reference facts for all three answerable questions (3/3 each under this draft rubric).
- Baseline and hallucination-aware prompting each receive one provisional correct answer out of three, accepting the rock-correlation paraphrase. The hallucination-aware Kublai response is partial. These are draft judgments, not exact-match scores.
- On the reversed-age question, baseline supplied an unsupported conversion; hallucination-aware prompting abstained; RAG restated the true conversion without explicitly addressing the false premise; combined RAG and prompting corrected the premise.
- On the plenary-session question, both RAG responses are supported by doc_0051. The screened unanswerable label is ambiguous and needs review. The earlier suggestion that this response was a hallucination is not justified by the inspected evidence.
- Hallucination-aware prompting explicitly abstained on both originally labeled unanswerable questions (2/2). This describes behavior only; the ambiguous question prevents interpreting that count as two confirmed correct abstentions.

## Report-ready progress paragraph

A five-question pilot generated 20 completed responses across baseline, hallucination-aware prompting, RAG, and combined RAG with hallucination-aware prompting. The pipeline recorded answers, model metadata, token usage, prompts, and retrieved document IDs in resumable JSON checkpoints. Both RAG conditions reused identical top-five hybrid retrieval results for each question. Preliminary evidence review found accurate reference facts in the RAG responses to the three answerable items, while the unanswerable items exposed differences between abstention, false-premise correction, and nonresponsive passage restatement. One screened unanswerable item was flagged for re-screening because the retrieved passage supports an observer-attendance interpretation. These observations validate the pipeline and motivate rubric refinement; the small, convenience-selected pilot does not establish comparative performance.

## Next work

Confirm the flagged scoring decisions and plenary-session answerability with the student/reviewer. Freeze an evaluation rubric before the full 200-question experiment. Review topic diversity and report ambiguous cases separately. No additional paid generation is needed for the current review.

## Response-level draft

| Question | Condition | Correctness | Reference support | Behavior |
|---|---|---|---|---|
| Q1 | baseline | incorrect | unsupported | answer |
| Q1 | hallucination_aware | partial | partial | answer |
| Q1 | rag | correct | supported | answer |
| Q1 | rag_hallucination_aware | correct | supported | answer |
| Q2 | baseline | incorrect | unsupported | answer |
| Q2 | hallucination_aware | incorrect | unsupported | answer |
| Q2 | rag | correct | supported | answer |
| Q2 | rag_hallucination_aware | correct | supported | answer |
| Q3 | baseline | correct | supported | answer |
| Q3 | hallucination_aware | correct | supported | answer |
| Q3 | rag | correct | supported | answer |
| Q3 | rag_hallucination_aware | correct | supported | answer |
| Q4 | baseline | incorrect | unsupported | answer |
| Q4 | hallucination_aware | appropriate_abstention | not_applicable | explicit_abstention |
| Q4 | rag | nonresponsive | supported | answer |
| Q4 | rag_hallucination_aware | appropriate_correction | supported | premise_correction |
| Q5 | baseline | needs_review | unsupported | conditional_answer |
| Q5 | hallucination_aware | needs_review | not_applicable | explicit_abstention |
| Q5 | rag | needs_review | supported | answer |
| Q5 | rag_hallucination_aware | needs_review | supported | answer |
