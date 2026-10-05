from datasets import load_dataset


def main():
    dataset = load_dataset("rajpurkar/squad_v2")

    train = dataset["train"]

    answerable = []
    unanswerable = []

    for example in train:
        if len(example["answers"]["text"]) > 0:
            answerable.append(example)
        else:
            unanswerable.append(example)

    print(f"Total training examples: {len(train)}")
    print(f"Answerable: {len(answerable)}")
    print(f"Unanswerable: {len(unanswerable)}")

    print("\n--- ANSWERABLE EXAMPLE ---")
    print(f"Question: {answerable[0]['question']}")
    print(f"Answer: {answerable[0]['answers']['text']}")
    print(f"Context: {answerable[0]['context'][:300]}...")

    print("\n--- UNANSWERABLE EXAMPLE ---")
    print(f"Question: {unanswerable[0]['question']}")
    print(f"Answer: {unanswerable[0]['answers']['text']}")
    print(f"Context: {unanswerable[0]['context'][:300]}...")


if __name__ == "__main__":
    main()