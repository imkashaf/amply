
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

# 1. Load API key from .env
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path, override=True)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise SystemExit("API key not found. Check D:\\dev\\.env")

print("API key loaded successfully.")

# 2. Configure Gemini client
client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=60000),
)

MODEL = "gemini-3.5-flash-lite"# 3. Hardware lab assistant instructions
SYSTEM_PROMPT = """
You are a Senior Hardware Lab Assistant for an Electrical Engineering
student.

Explain electronics in simple, beginner-friendly language.
Solve circuit problems step by step and define formulas.
Help with diodes, Zener diodes, rectifiers, clippers, clampers,
op-amps, circuit calculations, and lab viva questions.
Never invent missing circuit values.
Ask for missing information when necessary.
Prioritize electrical safety.
Keep answers concise unless more detail is requested.
"""

# 4. Start the assistant
print("=" * 38)
print("      AI HARDWARE LAB ASSISTANT")
print("=" * 38)
print("Ask about circuits, components, or lab work.")
print("Type 'exit' to quit.\n")

conversation = []

while True:
    try:
        question = input("\nYou: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nAssistant: Goodbye!")
        break

    if question.lower() in ("exit", "quit"):
        print("\nAssistant: Good luck with your labs!")
        break

    if not question:
        continue

    conversation.append({
        "role": "user",
        "parts": [{"text": question}],
    })

    start_time = time.perf_counter()
    print("Thinking...", flush=True)

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=conversation,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,
                max_output_tokens=300,
            ),
        )

        answer = response.text

        if not answer:
            answer = "No text response received. Please try again."

        print(f"\nAssistant:\n{answer}")

        elapsed = time.perf_counter() - start_time
        print(f"\n[Response time: {elapsed:.1f} seconds]")

        conversation.append({
            "role": "model",
            "parts": [{"text": answer}],
        })

        # Keep only the last three exchanges
        conversation = conversation[-6:]

    except errors.APIError as error:
        conversation.pop()
        elapsed = time.perf_counter() - start_time
        print(f"\nGemini API error after {elapsed:.1f} seconds:")
        print(error)

    except Exception as error:
        conversation.pop()
        elapsed = time.perf_counter() - start_time
        print(f"\nUnexpected error after {elapsed:.1f} seconds:")
        print(error)
