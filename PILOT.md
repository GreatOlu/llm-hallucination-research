# Five-question pilot

Run commands from the repository root using the existing virtual environment. The active checkpoint is **`results/experiments/pilot_v2.json`**, which contains 20 completed responses. The pilot is complete; no further paid requests are needed to inspect it.

## Free inspection

```sh
.venv/bin/python -m src.experiments.run_pilot
```

The default is equivalent to:

```sh
.venv/bin/python -m src.experiments.run_pilot --output results/experiments/pilot_v2.json
```

With the included checkpoint and matching source/data files, the saved statuses are `{'completed': 20}`. Inspection does not load the API client or retriever, make network requests, or create an output file. It does not require an API key.

## Free automated verification

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_pilot.py' -v
```

The six tests use fake retrieval and responses and make no paid calls.

## Explicit paid execution

The completed checkpoint has no pending requests. These commands are relevant only when continuing a checkpoint with pending records:

```sh
# Allow one pending request, then inspect the result.
.venv/bin/python -m src.experiments.run_pilot --execute --max-calls 1 --output results/experiments/pilot_v2.json
.venv/bin/python -m src.experiments.run_pilot --output results/experiments/pilot_v2.json

# Resume the same checkpoint.
.venv/bin/python -m src.experiments.run_pilot --execute --output results/experiments/pilot_v2.json
```

The API key must be available in the process environment or the existing ignored `.env`. The client loads `.env` only when generating a response. Never paste credentials into commands or results. Dependencies are listed in `requirements.txt`.

## Design and verification

Selection is deterministic: the first three answerable questions and first two screened unanswerable questions in the processed files. This is a pipeline pilot, not a representative performance estimate. Two answerable questions share a supporting passage.

HybridRetriever uses `top_k=5`, `rrf_k=60`, and `candidate_k=10`. Retrieval occurs once per question; both RAG conditions reuse the same passages. Passages and exact prompts are checkpointed before generation. Initial retrieval may download the embedding model; no paid LLM request occurs until all retrieval succeeds.

A full pilot has 20 completed records, five per condition. Verify that both RAG conditions have the same five document IDs per question and that non-RAG records have none. Inspect answers and `response_status` for truncation. Reference answers and labels are saved for evaluation but never added to prompts. Human confirmation of the draft evaluations and re-screening of the ambiguous plenary-session question remain necessary.

The completed pilot used 10,660 input and 5,613 output tokens. Sum the per-record `input_tokens` and `output_tokens` to reproduce these totals.

## Request limits and recovery

Each output file contains at most 20 planned requests; `--max-calls` limits each invocation. The model is `gpt-6-luna`, with a 1,000-output-token cap per request including reasoning tokens. Input tokens cost extra; no monetary cap is claimed. The cap is not guaranteed sufficient for every question.

SDK automatic retries are disabled. Errors, empty responses, and incomplete responses stop the invocation. Re-running skips every previously attempted record, including errors and `in_flight` requests, and proceeds only with pending records. There is deliberately no automatic retry option.

A crash after the server processed a request but before its answer was saved cannot be resolved automatically. Check provider usage before deciding whether to attempt that record again. Missing token counts for failed or interrupted requests do not imply zero billing. Back up the checkpoint before any manual recovery.

Checkpoints are atomically replaced, and an OS lock prevents concurrent runners from using the same output. Source/data fingerprints reject resuming after changes to the client, prompts, retriever, or datasets. A fingerprint mismatch is not a reason to delete the saved results or blindly launch a new experiment. Identify the change first; existing results remain available for direct JSON review.

A new `--output` path creates a separate experiment and may incur another 20 requests. Preserve the active checkpoint to resume it. Error records contain sanitized descriptions rather than raw exception text.

## Historical incomplete attempt

`results/experiments/pilot.json` is retained only as a historical record of the first attempt, which exhausted a 200-token cap and returned no answer text. Its 23 input and 200 output tokens are additional to the completed pilot usage. Include them in overall cost accounting, but exclude that attempt from the revised experimental results.

The historical checkpoint uses an older configuration and is not intended to resume under the current client. All current inspection and execution instructions use `pilot_v2.json`. The runner defaults to that active file; the original attempt is preserved unchanged.
