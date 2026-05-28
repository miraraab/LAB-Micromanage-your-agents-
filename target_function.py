from dotenv import load_dotenv
load_dotenv()

from langsmith import traceable
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# System prompt for customer support
SYSTEM_PROMPT = """You are a helpful customer support representative.
Your role is to provide clear, accurate, and friendly answers to customer questions.
Keep responses concise but comprehensive.
If you don't know something, admit it and suggest contacting support."""


@traceable(name="customer_support_qa", run_type="llm")
def customer_support_qa(question: str) -> dict:
    """
    Target function for customer support Q&A evaluation.

    Args:
        question: Customer question (string)

    Returns:
        Dictionary with 'answer' key containing the model's response
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=500,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ]
        )

        answer = response.choices[0].message.content.strip()

        return {
            "answer": answer,
            "model": "gpt-4o-mini",
            "tokens_used": response.usage.total_tokens
        }

    except Exception as e:
        return {
            "answer": f"Error generating response: {str(e)}",
            "model": "gpt-4o-mini",
            "error": True
        }


def test_target_function():
    """Test the target function with sample questions."""
    test_questions = [
        "How do I reset my password?",
        "What payment methods do you accept?",
        "Can I use the service on multiple devices?"
    ]

    print("Testing Target Function...\n")
    print("=" * 60)

    for i, question in enumerate(test_questions, 1):
        print(f"\nTest {i}: {question}")
        print("-" * 60)

        result = customer_support_qa(question)

        print(f"Answer: {result['answer'][:200]}...")
        print(f"Model: {result['model']}")
        if 'tokens_used' in result:
            print(f"Tokens Used: {result['tokens_used']}")
        if result.get('error'):
            print("⚠️ Error occurred during processing")
        else:
            print("✅ Response generated successfully")

    print("\n" + "=" * 60)
    print("✅ Target Function Testing Complete")


if __name__ == "__main__":
    test_target_function()
