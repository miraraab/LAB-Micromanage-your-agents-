from dotenv import load_dotenv
import os

load_dotenv()

from langsmith import Client
from openai import OpenAI

ls_client = Client()
oai_client = OpenAI()

projects = list(ls_client.list_projects())
print(f"✅ LangSmith verbunden – {len(projects)} Projekte gefunden")
print(f"Project: {os.environ.get('LANGCHAIN_PROJECT')}")
EOF