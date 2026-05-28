from dotenv import load_dotenv
load_dotenv()

from langsmith import Client
import statistics

# Initialize LangSmith client
client = Client()

DATASET_NAME = "customer-support-faq-v1"


def review_evaluation_results():
    """Review and summarize evaluation results from LangSmith."""

    print("📊 Reviewing Evaluation Results")
    print("=" * 80)

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
            return

        print(f"✅ Dataset loaded: {dataset.name}")
        print(f"   ID: {dataset.id}")

        # Get all examples
        examples = list(client.list_examples(dataset_id=dataset.id))
        print(f"✅ Total examples in dataset: {len(examples)}")

        # Get experiment sessions
        print("\n🔍 Fetching experiment sessions...")
        sessions = list(client.list_projects(reference_dataset_id=dataset.id))

        if not sessions:
            print("❌ No experiment sessions found!")
            return

        print(f"✅ Found {len(sessions)} experiment sessions")

        # Get runs from the most recent session
        latest_session = sessions[-1] if sessions else None
        if not latest_session:
            print("❌ No sessions to analyze!")
            return

        print(f"   Latest session: {latest_session.name}")

        runs = list(client.list_runs(session_id=latest_session.id))
        print(f"✅ Found {len(runs)} runs in latest session")

        # Analyze results
        print("\n" + "=" * 80)
        print("📈 EVALUATION RESULTS ANALYSIS")
        print("=" * 80)

        # Group runs by experiment
        experiments = {}
        for run in runs:
            exp_name = run.session_name or "Unknown"
            if exp_name not in experiments:
                experiments[exp_name] = []
            experiments[exp_name].append(run)

        # Analyze each experiment
        for exp_name, exp_runs in sorted(experiments.items(), reverse=True)[:1]:
            print(f"\n🔬 Experiment: {exp_name}")
            print("-" * 80)

            # Collect feedback data
            all_feedback = []
            correctness_scores = []
            relevance_scores = []
            run_details = []

            for i, run in enumerate(exp_runs, 1):
                run_info = {
                    "number": i,
                    "id": run.id,
                    "question": None,
                    "answer": None,
                    "correctness": None,
                    "relevance": None,
                    "feedback": []
                }

                # Get inputs
                if run.inputs:
                    run_info["question"] = run.inputs.get("question", "N/A")[:60]

                # Get outputs
                if run.outputs:
                    run_info["answer"] = run.outputs.get("answer", "N/A")[:60]

                # Get feedback
                if hasattr(run, 'feedback') and run.feedback:
                    for feedback in run.feedback:
                        if hasattr(feedback, 'key') and hasattr(feedback, 'score'):
                            if feedback.key == 'correctness':
                                run_info["correctness"] = feedback.score
                                correctness_scores.append(feedback.score)
                            elif feedback.key == 'relevance':
                                run_info["relevance"] = feedback.score
                                relevance_scores.append(feedback.score)

                            run_info["feedback"].append({
                                "key": feedback.key,
                                "score": feedback.score
                            })

                run_details.append(run_info)

            # Print summary metrics
            print(f"\n📊 Summary Metrics:")
            print(f"   Total Runs: {len(exp_runs)}")

            if correctness_scores:
                avg_corr = statistics.mean(correctness_scores)
                min_corr = min(correctness_scores)
                max_corr = max(correctness_scores)
                print(f"\n   Correctness Scores:")
                print(f"   ├─ Average: {avg_corr:.2f}/1.0")
                print(f"   ├─ Min: {min_corr:.2f}/1.0")
                print(f"   ├─ Max: {max_corr:.2f}/1.0")
                if len(correctness_scores) > 1:
                    std_dev = statistics.stdev(correctness_scores)
                    print(f"   └─ Std Dev: {std_dev:.2f}")

            if relevance_scores:
                avg_rel = statistics.mean(relevance_scores)
                min_rel = min(relevance_scores)
                max_rel = max(relevance_scores)
                print(f"\n   Relevance Scores:")
                print(f"   ├─ Average: {avg_rel:.2f}/1.0")
                print(f"   ├─ Min: {min_rel:.2f}/1.0")
                print(f"   ├─ Max: {max_rel:.2f}/1.0")
                if len(relevance_scores) > 1:
                    std_dev = statistics.stdev(relevance_scores)
                    print(f"   └─ Std Dev: {std_dev:.2f}")

            # Print detailed results
            print("\n" + "-" * 80)
            print("📋 DETAILED RESULTS BY EXAMPLE:")
            print("-" * 80)

            for run in run_details:
                status = "✅" if run["correctness"] and run["correctness"] >= 0.8 else "⚠️"
                print(f"\n{status} Example {run['number']}: {run['question']}")

                if run["correctness"] is not None:
                    print(f"   Correctness: {run['correctness']:.2f}/1.0")
                if run["relevance"] is not None:
                    print(f"   Relevance: {run['relevance']:.2f}/1.0")

            # Identify best and worst performers
            print("\n" + "=" * 80)
            print("🏆 PERFORMANCE ANALYSIS:")
            print("=" * 80)

            # Best performers
            if correctness_scores:
                best_idx = correctness_scores.index(max(correctness_scores))
                best_run = run_details[best_idx]
                print(f"\n✨ Best Correctness Score:")
                print(f"   Example: {best_run['question']}")
                print(f"   Score: {best_run['correctness']:.2f}/1.0")

            # Worst performers
            if correctness_scores:
                worst_idx = correctness_scores.index(min(correctness_scores))
                worst_run = run_details[worst_idx]
                print(f"\n⚠️ Lowest Correctness Score:")
                print(f"   Example: {worst_run['question']}")
                print(f"   Score: {worst_run['correctness']:.2f}/1.0")

            # Score distribution
            if correctness_scores:
                high_scores = sum(1 for s in correctness_scores if s >= 0.8)
                medium_scores = sum(1 for s in correctness_scores if 0.6 <= s < 0.8)
                low_scores = sum(1 for s in correctness_scores if s < 0.6)

                print(f"\n📊 Score Distribution (Correctness):")
                print(f"   High (≥0.8): {high_scores}/{len(correctness_scores)} ({high_scores/len(correctness_scores)*100:.0f}%)")
                print(f"   Medium (0.6-0.8): {medium_scores}/{len(correctness_scores)} ({medium_scores/len(correctness_scores)*100:.0f}%)")
                print(f"   Low (<0.6): {low_scores}/{len(correctness_scores)} ({low_scores/len(correctness_scores)*100:.0f}%)")

        # Print LangSmith links
        print("\n" + "=" * 80)
        print("🔗 VIEW IN LANGSMITH UI:")
        print("=" * 80)
        print(f"\nProject Dashboard:")
        print(f"  https://eu.smith.langchain.com/o/b1b7036f-bc62-4cd5-b9ee-3bc5f9a32a03/projects")
        print(f"\nDataset with Experiments:")
        print(f"  https://eu.smith.langchain.com/o/b1b7036f-bc62-4cd5-b9ee-3bc5f9a32a03/datasets/{dataset.id}")

        print("\n" + "=" * 80)
        print("✅ Review Complete!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    review_evaluation_results()
