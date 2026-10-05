import random
from collections import defaultdict

from datasets import load_dataset


SEED = 42
NUM_ANSWERABLE = 150
MAX_QUESTIONS_PER_CONTEXT = 2
NUM_CORPUS_PASSAGES = 500
NUM_UNANSWERABLE = 50
NUM_UNANSWERABLE_CANDIDATES = 100
MAX_UNANSWERABLE_PER_CONTEXT = 1


def sample_answerable_questions(validation):
    answerable = [
        example
        for example in validation
        if example["answers"]["text"]
    ]

    # Group questions by their context passage
    questions_by_context = defaultdict(list)

    for example in answerable:
        questions_by_context[example["context"]].append(example)

    # Shuffle the contexts reproducibly
    rng = random.Random(SEED)

    contexts = list(questions_by_context.keys())
    rng.shuffle(contexts)

    selected = []

    for context in contexts:
        questions = questions_by_context[context].copy()
        rng.shuffle(questions)

        selected.extend(
            questions[:MAX_QUESTIONS_PER_CONTEXT]
        )

        if len(selected) >= NUM_ANSWERABLE:
            break

    return selected[:NUM_ANSWERABLE]

def build_knowledge_base(validation, selected_answerable):
    rng = random.Random(SEED)

    # These passages MUST be present because they support
    # our selected answerable evaluation questions.
    required_contexts = sorted({
        example["context"]
        for example in selected_answerable
    })

    required_context_set = set(required_contexts)

    # Collect every unique context in the validation split.
    all_contexts = {}

    for example in validation:
        context = example["context"]

        if context not in all_contexts:
            all_contexts[context] = {
                "title": example["title"],
                "context": context
            }

    # Potential distractors cannot duplicate required contexts.
    distractor_contexts = [
        context
        for context in all_contexts
        if context not in required_context_set
    ]

    rng.shuffle(distractor_contexts)

    num_distractors_needed = (
        NUM_CORPUS_PASSAGES - len(required_contexts)
    )

    selected_distractors = distractor_contexts[
        :num_distractors_needed
    ]

    corpus_contexts = list(required_contexts) + selected_distractors

    # Give every passage a stable document ID.
    knowledge_base = []

    for i, context in enumerate(corpus_contexts):
        knowledge_base.append({
            "document_id": f"doc_{i:04d}",
            "title": all_contexts[context]["title"],
            "context": context,
            "is_answerable_reference": context in required_context_set
        })

    return knowledge_base

def sample_unanswerable_candidates(validation):
    unanswerable = [
        example
        for example in validation
        if not example["answers"]["text"]
    ]

    questions_by_context = defaultdict(list)

    for example in unanswerable:
        questions_by_context[example["context"]].append(example)

    rng = random.Random(SEED)

    contexts = list(questions_by_context.keys())
    rng.shuffle(contexts)

    selected = []

    for context in contexts:
        questions = questions_by_context[context].copy()
        rng.shuffle(questions)

        selected.extend(
            questions[:MAX_UNANSWERABLE_PER_CONTEXT]
        )

        if len(selected) >= NUM_UNANSWERABLE_CANDIDATES:
            break

    return selected[:NUM_UNANSWERABLE_CANDIDATES]

def main():
    dataset = load_dataset("rajpurkar/squad_v2")
    validation = dataset["validation"]

    selected = sample_answerable_questions(validation)

    knowledge_base = build_knowledge_base(
        validation,
        selected
    )

    required_count = sum(
        document["is_answerable_reference"]
        for document in knowledge_base
    )

    distractor_count = len(knowledge_base) - required_count

    print("Evaluation Set")
    print("--------------")
    print(f"Answerable questions: {len(selected)}")

    print("\nKnowledge Base")
    print("--------------")
    print(f"Total passages: {len(knowledge_base)}")
    print(f"Required supporting passages: {required_count}")
    print(f"Additional corpus passages: {distractor_count}")

    print("\nFirst 3 documents:")

    for document in knowledge_base[:3]:
        print(
            f"{document['document_id']} | "
            f"{document['title']} | "
            f"required={document['is_answerable_reference']}"
        )

    unanswerable_candidates = sample_unanswerable_candidates(
        validation
)

    print("\nUnanswerable Candidate Pool")
    print("---------------------------")
    print(
        f"Candidate questions: "
        f"{len(unanswerable_candidates)}"
    )

    unique_unanswerable_contexts = {
        example["context"]
        for example in unanswerable_candidates
    }

    print(
        f"Unique associated contexts: "
        f"{len(unique_unanswerable_contexts)}"
    )

    print("\nFirst 5 candidates:")

    for i, example in enumerate(
        unanswerable_candidates[:5],
        start=1
    ):
        print(f"\n{i}. {example['question']}")
        print(f"   Topic: {example['title']}")

if __name__ == "__main__":
    main()