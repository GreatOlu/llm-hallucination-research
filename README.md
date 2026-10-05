# Evaluating Techniques for Reducing LLM Hallucinations

This project evaluates techniques for reducing factual hallucinations in large language model responses. The experiment compares four conditions: a baseline model, hallucination-aware prompting, retrieval-augmented generation (RAG), and RAG combined with hallucination-aware prompting.

## Current Progress

The project currently focuses on constructing the experimental dataset using the SQuAD 2.0 validation split.

Current work includes:
- Exploring and analyzing the SQuAD 2.0 dataset
- Selecting 150 answerable evaluation questions
- Limiting question selection to reduce context overrepresentation
- Constructing a 500-passage retrieval corpus
- Selecting 100 candidate unanswerable questions for corpus-wide verification

The final evaluation set will contain 200 questions:
- 150 answerable questions
- 50 verified unanswerable questions

## Planned Experiment

The four experimental conditions are:

1. Baseline
2. Hallucination-aware prompting
3. Retrieval-Augmented Generation (RAG)
4. RAG + hallucination-aware prompting

Evaluation will include answer accuracy, groundedness, refusal behavior, and retrieval performance.