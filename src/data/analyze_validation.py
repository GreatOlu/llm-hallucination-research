from datasets import load_dataset


def main():
    dataset = load_dataset("rajpurkar/squad_v2")
    validation = dataset["validation"]

    answerable = []
    unanswerable = []

    for example in validation:
        if example["answers"]["text"]:
            answerable.append(example)
        else:
            unanswerable.append(example)

    print("SQuAD 2.0 Validation Split")
    print("--------------------------")
    print(f"Total examples: {len(validation)}")
    print(f"Answerable: {len(answerable)}")
    print(f"Unanswerable: {len(unanswerable)}")

    unique_contexts = set(example["context"] for example in validation)

    print(f"Unique contexts: {len(unique_contexts)}")

    print("\nExample answerable question:")
    print(f"Question: {answerable[0]['question']}")
    print(f"Answer: {answerable[0]['answers']['text']}")

    print("\nExample unanswerable question:")
    print(f"Question: {unanswerable[0]['question']}")
    print(f"Answer: {unanswerable[0]['answers']['text']}")


if __name__ == "__main__":
    main()