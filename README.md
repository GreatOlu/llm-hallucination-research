# Evaluating Techniques for Reducing LLM Hallucinations

This research project compares hallucination-aware prompting and retrieval-augmented generation (RAG), individually and in combination, in a controlled question-answering experiment. The goal is to assess answer correctness, support from evidence, and appropriate abstention when information is insufficient.

## Current stage

The midterm implementation and five-question pilot are complete. The full experiment and final response evaluation have not yet been conducted.

Completed work includes:

- Reproducible sampling from the SQuAD 2.0 validation split using random seed 42.
- A prepared evaluation set containing 150 answerable and 50 retrieval-screened unanswerable questions.
- A 500-passage knowledge base, including all 76 supporting contexts for the answerable questions and 424 additional passages.
- Semantic retrieval, BM25, and hybrid Reciprocal Rank Fusion (RRF), evaluated on 150 answerable questions.
- Four working prompts, an OpenAI API client, and a resumable pilot runner.
- A completed pilot containing 20 responses: five questions across four conditions.
- Six passing offline tests and a preliminary evaluation rubric with 20 provisional response reviews.

The unanswerable questions were screened against the top ten semantic and top ten BM25 results, not exhaustively proven unanswerable across the corpus. One pilot question about plenary-session participation is flagged for re-screening because its retrieved passage supports an observer-attendance interpretation.

## Experimental conditions

| Condition | Question | Retrieved passages | Hallucination-aware instructions |
|---|---|---|---|
| Baseline | Yes | No | No |
| Hallucination-aware | Yes | No | Yes |
| RAG | Yes | Top five hybrid results | No |
| RAG + hallucination-aware | Yes | Same five hybrid results | Yes |

The implemented client uses `gpt-6-luna` with a maximum of 1,000 output tokens per request. This allowance includes reasoning tokens. Standard RAG does not include the additional abstention instruction, keeping the prompting intervention distinct from retrieval.

Hybrid retrieval combines the top ten semantic and BM25 results using RRF with a ranking constant of 60. Semantic retrieval uses `sentence-transformers/all-MiniLM-L6-v2`, cosine similarity, and cached passage embeddings.

## Retrieval results

Recall@k is the proportion of the 150 answerable questions whose designated supporting passage appears among the first k retrieved documents.

| Method | Recall@1 | Recall@5 | Recall@10 |
|---|---:|---:|---:|
| Semantic | 76.67% | 95.33% | 97.33% |
| BM25 | 88.00% | 97.33% | 97.33% |
| Hybrid RRF | 88.00% | 98.00% | 99.33% |

Hybrid top-five retrieval was selected for the pilot. These results measure retrieval within the constructed corpus; they do not establish response correctness or hallucination reduction.

## Setup

Run commands from the repository root. The current runner uses Unix file locking and supports macOS/Linux; native Windows requires an alternative lock implementation or a Linux environment such as WSL.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

API execution requires `OPENAI_API_KEY` in the process environment or a local `.env` file. Keep credentials out of version control. Viewing the saved pilot and running the offline tests do not require an API key.

## Inspect the completed pilot without API calls

```sh
.venv/bin/python -m src.experiments.run_pilot
```

The default checkpoint is `results/experiments/pilot_v2.json`. With the included results and matching source/data files, the command reports:

```text
Saved statuses: {'completed': 20}
```

This command does not import the API client or retriever and makes no network requests. The explicit equivalent is:

```sh
.venv/bin/python -m src.experiments.run_pilot --output results/experiments/pilot_v2.json
```

The completed pilot used 10,660 input and 5,613 output tokens. The two RAG conditions received identical retrieved passages for each question. The first three answerable and first two screened unanswerable questions were selected deterministically; this small convenience sample is intended to validate the pipeline, not estimate comparative performance.

The earlier `results/experiments/pilot.json` is retained as a historical record of an incomplete attempt with a 200-token cap. It is not the active checkpoint. Its 23 input and 200 output tokens are separate from the completed pilot totals.

## Offline verification

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_pilot.py' -v
```

The tests use fake retrieval and responses. They cover resumption, shared RAG evidence, error sanitization, interrupted requests, empty/incomplete responses, and concurrent access protection. They make no paid API calls.

## Paid execution and resumption

The completed pilot does not need to be rerun. If the active checkpoint has pending records, the following commands explicitly allow paid requests:

```sh
# Attempt at most one pending request.
.venv/bin/python -m src.experiments.run_pilot --execute --max-calls 1 --output results/experiments/pilot_v2.json

# Resume the same checkpoint, skipping all previously attempted records.
.venv/bin/python -m src.experiments.run_pilot --execute --output results/experiments/pilot_v2.json
```

With all 20 records completed, there are no pending requests to send. A new output path creates a separate experiment that may incur another 20 requests. Do not delete or reset the existing results to inspect them. See [PILOT.md](PILOT.md) for checkpoint and recovery details.

## Saved artifacts

| Location | Contents |
|---|---|
| `data/processed/` | Questions, corpus, candidate questions, and screening records |
| `src/data/` | Dataset exploration and sampling scripts |
| `src/retrieval/` | Semantic, BM25, hybrid retrieval, and screening export code |
| `src/evaluation/evaluate_retrieval.py` | Supporting-document retrieval evaluation |
| `src/experiments/` | Prompts, API client, and pilot runner |
| `tests/test_pilot.py` | Six offline pilot tests |
| `results/retrieval/` | Saved retrieval records and metrics |
| `results/experiments/pilot_v2.json` | Completed pilot answers, prompts, model metadata, token usage, retrieved evidence, and statuses |
| `results/experiments/pilot_review/` | Draft rubric, provisional response evaluations, and pilot summary |

## Evaluation status and next phase

The current response evaluations are AI-assisted draft judgments requiring human confirmation. Evidence support is assessed separately from correctness: an unsupported claim is not automatically false, and a supported statement can still fail to answer the question. The ambiguous plenary-session item is not counted as an established hallucination case.

Next steps are to:

1. Re-screen the ambiguous item and confirm the pilot scoring decisions.
2. Finalize the dataset, model configuration, and evaluation rubric.
3. Implement Exact Match and token-level F1, and validate evidence-support and abstention evaluation.
4. Extend the current five-question runner to the full 200-question study.
5. Collect the planned 800 responses across four conditions after reviewing the request and token budget.

Comprehensive analysis, visualizations, and final conclusions will follow. No final hallucination rates or statistically supported treatment comparisons are claimed at the current stage.
