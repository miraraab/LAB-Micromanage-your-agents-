from dotenv import load_dotenv
load_dotenv()

from langsmith import traceable
from openai import OpenAI
import json

client = OpenAI()


@traceable(name="correctness_evaluator")
def correctness_evaluator(inputs: dict, outputs: dict) -> dict:
    """
    LLM-as-judge evaluator for customer support Q&A correctness.

    Evaluates whether the generated answer is correct and helpful.

    Args:
        inputs: Dictionary with 'question' key from dataset
        outputs: Dictionary with 'answer' key from target function

    Returns:
        Dictionary with evaluation result
    """
    question = inputs.get("question", "")
    generated_answer = outputs.get("answer", "")
    reference_answer = inputs.get("expected_answer", "")

    if not question or not generated_answer:
        return {
            "key": "correctness",
            "score": 0.0,
            "comment": "Missing question or answer"
        }

    evaluation_prompt = f"""You are an expert evaluator for customer support responses.
Evaluate the generated answer against the reference answer.

QUESTION: {question}

REFERENCE ANSWER: {reference_answer}

GENERATED ANSWER: {generated_answer}

Evaluate on a 0-10 scale:
1. Correctness: Is the answer factually correct and accurate?
2. Completeness: Does it address all parts of the question?
3. Clarity: Is the answer clear and easy to understand?
4. Helpfulness: Would this help the customer solve their problem?
5. Tone: Is the tone appropriate for customer support?

Provide your evaluation in JSON format with:
- correctness_score (0-10)
- completeness_score (0-10)
- clarity_score (0-10)
- helpfulness_score (0-10)
- tone_score (0-10)
- overall_score (0-10, average of above)
- reasoning (brief explanation)

Return ONLY valid JSON, no markdown or extra text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "user", "content": evaluation_prompt}
            ]
        )

        result_json = json.loads(response.choices[0].message.content)
        overall_score = result_json.get("overall_score", 0) / 10.0
        reasoning = result_json.get("reasoning", "No reasoning provided")

        return {
            "key": "correctness",
            "score": overall_score,
            "comment": reasoning
        }

    except Exception as e:
        return {
            "key": "correctness",
            "score": 0.0,
            "comment": f"Error: {str(e)}"
        }


@traceable(name="relevance_evaluator")
def relevance_evaluator(inputs: dict, outputs: dict) -> dict:
    """
    Evaluates whether the generated answer is relevant to the question.

    Args:
        inputs: Dictionary with 'question' key from dataset
        outputs: Dictionary with 'answer' key from target function

    Returns:
        Dictionary with evaluation result
    """
    question = inputs.get("question", "")
    generated_answer = outputs.get("answer", "")

    if not question or not generated_answer:
        return {
            "key": "relevance",
            "score": 0.0,
            "comment": "Missing question or answer"
        }

    evaluation_prompt = f"""You are an expert evaluator for customer support responses.
Evaluate whether the generated answer is relevant to the customer question.

QUESTION: {question}

GENERATED ANSWER: {generated_answer}

On a scale of 0-10:
1. Is the answer directly addressing the question? (0=off-topic, 10=perfectly relevant)
2. Does it avoid irrelevant information? (0=full of tangents, 10=laser-focused)

Provide JSON with:
- relevance_score (0-10)
- focus_score (0-10)
- overall_relevance (0-10, average)
- reasoning

Return ONLY valid JSON, no markdown."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "user", "content": evaluation_prompt}
            ]
        )

        result_json = json.loads(response.choices[0].message.content)
        overall_score = result_json.get("overall_relevance", 0) / 10.0
        reasoning = result_json.get("reasoning", "No reasoning provided")

        return {
            "key": "relevance",
            "score": overall_score,
            "comment": reasoning
        }

    except Exception as e:
        return {
            "key": "relevance",
            "score": 0.0,
            "comment": f"Error: {str(e)}"
        }


def test_evaluators():
    """Test evaluators with sample question and answers."""
    print("Testing Evaluators...\n")
    print("=" * 70)

    inputs = {"question": "How do I reset my password?"}
    outputs = {
        "answer": "To reset your password: 1) Go to login page, 2) Click 'Forgot Password' link, 3) Enter your email address, 4) Check your email for reset instructions and follow them."
    }

    print(f"Question: {inputs['question']}")
    print(f"Answer: {outputs['answer'][:100]}...")
    print("\n" + "-" * 70)

    # Test correctness evaluator
    print("\n📊 Correctness Evaluation:")
    result = correctness_evaluator(inputs, outputs)
    print(f"Score: {result.get('score', 0):.2f}/1.0")
    print(f"Comment: {result.get('comment', 'N/A')}")

    print("\n" + "-" * 70)

    # Test relevance evaluator
    print("\n📊 Relevance Evaluation:")
    result = relevance_evaluator(inputs, outputs)
    print(f"Score: {result.get('score', 0):.2f}/1.0")
    print(f"Comment: {result.get('comment', 'N/A')}")

    print("\n" + "=" * 70)
    print("✅ Evaluator Testing Complete")


if __name__ == "__main__":
    test_evaluators()
