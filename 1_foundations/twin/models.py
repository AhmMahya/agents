from dotenv import load_dotenv
from random import choice
from openai import OpenAI
import os

load_dotenv(override=True)

class OpenRouter:
    api_key = os.getenv("OPENROUTER_API_KRY")
    base_url = "https://openrouter.ai/api/v1"
    models = [
        "cohere/north-mini-code:free",
        "tencent/hy3:free",
        "google/gemma-4-26b-a4b-it:free",
        "poolside/laguna-xs-2.1:free",
        "openai/gpt-oss-20b:free"
    ]
    model_name = choice(models)
    client = OpenAI(api_key=api_key, base_url=base_url)


class Gemini:
    api_key = os.getenv("GOOGLE_API_KEY")
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
    models = [
        "gemini-2.5-flash-lite"
    ]
    model_name = choice(models)
    client = OpenAI(api_key=api_key, base_url=base_url)
