from dotenv import load_dotenv
load_dotenv()

from langsmith import Client
from datetime import datetime

from target_function import customer_support_qa
from evaluators import correctness_evaluator, relevance_evaluator

# Initialize LangSmith client
client = Client()

# Dataset and experiment configuration
DATASET_NAME = "customer-support-faq-v1"
EXPERIMENT_PREFIX = f"customer-support-gpt4o-mini-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
MAX_CONCURRENCY = 2


def target_function(inputs: dict) -> dict:
    """
    Target function wrapper for LangSmith evaluation.

    Accepts inputs dict with 'question' field and returns
    dict with 'answer' field.
    """
    question = inputs.get("question", "")
    result = customer_support_qa(question)
    return {"answer": result.get("answer", "")}




def run_evaluation():
    """Execute the evaluation experiment using LangSmith."""

    print("🚀 Starting Evaluation Experiment")
    print("=" * 70)
    print(f"Dataset: {DATASET_NAME}")
    print(f"Experiment Prefix: {EXPERIMENT_PREFIX}")
    print(f"Max Concurrency: {MAX_CONCURRENCY}")
    print("=" * 70)

    try:
        # Get the dataset
        print("\n📦 Loading dataset...")
        all_datasets = list(client.list_datasets())
        dataset = None

        for ds in all_datasets:
            if ds.name == DATASET_NAME:
                dataset = ds
                break

        if not dataset:
            print(f"❌ Dataset '{DATASET_NAME}' not found!")
            print(f"Available datasets: {[ds.name for ds in all_datasets]}")
            return

        print(f"✅ Dataset loaded: {dataset.name} (ID: {dataset.id})")

        # Count examples
        examples = list(client.list_examples(dataset_id=dataset.id))
        print(f"✅ Found {len(examples)} examples in dataset")

        print("\n🔄 Running evaluation...")
        print("-" * 70)

        # Run evaluation
        experiment_results = client.evaluate(
            target_function,
            data=dataset,
            evaluators=[
                correctness_evaluator,
                relevance_evaluator
            ],
            experiment_prefix=EXPERIMENT_PREFIX,
            max_concurrency=MAX_CONCURRENCY,
            blocking=True
        )

        print("\n✅ Evaluation completed!")
        print("=" * 70)

        # Collect and display results
        print("\n📊 Evaluation Results Summary:")
        print("-" * 70)

        results_list = list(experiment_results)

        correctness_scores = []
        relevance_scores = []
        errors = 0

        for run in results_list:
            # Extract scores from feedback data
            if hasattr(run, 'feedback') and run.feedback:
                for feedback_item in run.feedback:
                    if hasattr(feedback_item, 'key'):
                        if feedback_item.key == 'correctness' and hasattr(feedback_item, 'score'):
                            correctness_scores.append(feedback_item.score)
                        elif feedback_item.key == 'relevance' and hasattr(feedback_item, 'score'):
                            relevance_scores.append(feedback_item.score)

        print(f"Total Examples Evaluated: {len(results_list)}")
        print(f"Correctness Evaluations: {len(correctness_scores)}")
        print(f"Relevance Evaluations: {len(relevance_scores)}")

        if correctness_scores:
            avg_correctness = sum(correctness_scores) / len(correctness_scores)
            print(f"\n📈 Average Correctness Score: {avg_correctness:.2f}/1.0")
            print(f"   Min: {min(correctness_scores):.2f}, Max: {max(correctness_scores):.2f}")

        if relevance_scores:
            avg_relevance = sum(relevance_scores) / len(relevance_scores)
            print(f"📈 Average Relevance Score: {avg_relevance:.2f}/1.0")
            print(f"   Min: {min(relevance_scores):.2f}, Max: {max(relevance_scores):.2f}")

        print("\n" + "=" * 70)
        print("✅ Experiment Complete!")
        print(f"\n🔗 View results in LangSmith:")
        print(f"   https://eu.smith.langchain.com/projects")
        print(f"\nExperiment Prefix: {EXPERIMENT_PREFIX}")
        print("=" * 70)

        return experiment_results

    except Exception as e:
        print(f"\n❌ Error during evaluation: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = run_evaluation()
    if results:
        print("\n✅ Evaluation execution successful!")
    else:
        print("\n❌ Evaluation execution failed!")
