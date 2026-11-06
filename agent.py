"""
Amply local prototype: terminal chat on the Gemini SDK.
The Discord deployment runs through Switch (OpenCode + Discord Connector);
this file is used to test the system prompt, the calculation tools, and latency locally.

Component sizing is done by tested Python code in eseries.py (not by the LLM).
"""
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

import eseries

# 1. Load API key from .env
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path, override=True)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise SystemExit(f"API key not found. Create {env_path} with GEMINI_API_KEY=...")

print("API key loaded successfully.")

# 2. Configure Gemini client
client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=60000),
)

MODEL = "gemini-3.5-flash-lite"

# 3. Same rules as the Switch agent instructions in the README
SYSTEM_PROMPT = """
You are Amply, a specialized Electrical Engineering Lab Assistant for students and bench prototyping.
Answer user questions directly in clear, concise plain text.

CORE OPERATIONAL RULES:
1. NO LATEX: Do not use LaTeX syntax, math delimiters ($ or $$), or slash commands. Use Unicode characters (Ω, ±, µ, π, ×, ÷) and readable text.
2. TOOLS FIRST: For any resistor or capacitor sizing (inverting amplifier, RC low-pass filter, voltage divider, or snapping a value to a standard part), call the provided tools and quote their results exactly. Never compute or round standard values yourself. Use E12 unless the user asks for E24.
3. BENCH ACCURACY: Only use real E12 values (mantissas 1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2 times a power of ten). State the ACTUAL resulting value (cutoff frequency, gain, output voltage) and its percent error versus the target.
4. FILTERS: Distinguish the natural frequency f0 = 1/(2π√(R1R2C1C2)) from the -3 dB frequency. A unity-gain Sallen-Key with equal R and equal C has Q = 0.5 (no peaking, -3 dB at about 0.64 × f0). Peaking appears only when Q is above 0.707 (for example gain above 1 or unequal components). Never call f0 the -3 dB frequency unless Q = 0.707.
5. SANITY CHECKS: Always include rail headroom, output clipping, and power dissipation checks.
6. Never invent missing circuit values. Ask for them if needed.
7. Prioritize electrical safety.
8. Keep answers under about 1500 characters.
"""

TOOLS = [
    eseries.snap,
    eseries.inverting_amp,
    eseries.rc_lowpass,
    eseries.voltage_divider,
]

# 4. Start the assistant
print("=" * 38)
print("      AMPLY: AI HARDWARE LAB ASSISTANT")
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

    conversation.append({"role": "user", "parts": [{"text": question}]})

    start_time = time.perf_counter()
    print("Thinking...", flush=True)

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=conversation,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,
                max_output_tokens=800,
                tools=TOOLS,
            ),
        )

        answer = response.text or "No text response received. Please try again."
        print(f"\nAssistant:\n{answer}")

        elapsed = time.perf_counter() - start_time
        print(f"\n[Response time: {elapsed:.1f} seconds]")

        conversation.append({"role": "model", "parts": [{"text": answer}]})

        # Keep only the last three exchanges
        conversation = conversation[-6:]

    except errors.APIError as error:
        conversation.pop()
        print(f"\nGemini API error after {time.perf_counter() - start_time:.1f} seconds:")
        print(error)

    except Exception as error:
        conversation.pop()
        print(f"\nUnexpected error after {time.perf_counter() - start_time:.1f} seconds:")
        print(error)
