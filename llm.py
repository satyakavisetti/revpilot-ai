import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_client():
    global client
    if client:
        return client
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        return client
    except:
        return None


def ask_llm(prompt):
    client = get_client()
    if not client:
        return None

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return res.choices[0].message.content
    except:
        return None