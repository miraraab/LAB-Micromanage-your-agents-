from dotenv import load_dotenv
import os

load_dotenv()

from langsmith import Client
from openai import OpenAI

try:
    ls_client = Client()
    print("✅ LangSmith verbunden")
except Exception as e:
    print(f"❌ LangSmith Fehler: {e}")

try:
    oai_client = OpenAI()
    print("✅ OpenAI verbunden")
except Exception as e:
    print(f"❌ OpenAI Fehler: {e}")

print(f"Project: {os.environ.get('LANGCHAIN_PROJECT')}")