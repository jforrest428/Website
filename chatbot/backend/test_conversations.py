"""
Test script: 5 simulated visitor conversations via the Claude API directly.
Run with: python test_conversations.py
Requires ANTHROPIC_API_KEY in env.
"""
import os
import sys
import json
import textwrap
from system_prompt import SYSTEM_PROMPT

try:
    import anthropic
    from dotenv import load_dotenv
except ImportError:
    print("Install requirements first: pip install -r requirements.txt")
    sys.exit(1)

# Load .env if present
load_dotenv()

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not set.")
    print("Create chatbot/backend/.env with:  ANTHROPIC_API_KEY=sk-ant-...")
    sys.exit(1)

client = anthropic.Anthropic(api_key=api_key)

DIVIDER = "=" * 70


def chat(messages):
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return resp.content[0].text


def run_conversation(title, turns):
    """
    turns: list of user strings. We interleave with assistant replies.
    Returns full transcript.
    """
    print(f"\n{DIVIDER}")
    print(f"  SCENARIO: {title}")
    print(DIVIDER)

    messages = []
    for user_text in turns:
        messages.append({"role": "user", "content": user_text})
        print(f"\n[VISITOR]\n{textwrap.fill(user_text, 70)}")

        reply = chat(messages)
        messages.append({"role": "assistant", "content": reply})

        print(f"\n[ASSISTANT]")
        # Wrap long lines for readability
        for para in reply.split("\n"):
            if para.strip():
                print(textwrap.fill(para, 70))
            else:
                print()

    return messages


def main():
    print(f"\n{'#'*70}")
    print("  FORREST ANALYTICS CHATBOT — TEST CONVERSATIONS")
    print(f"{'#'*70}")
    print("Running 5 simulated visitor conversations against the system prompt.")
    print("Model: claude-sonnet-4-6\n")

    # ── Scenario 1: Plumber asking about missed calls ──────────────────────
    run_conversation(
        "Scenario 1: Plumber — missed call pain point",
        [
            "hey, I run a plumbing company, 3 guys on the crew",
            "we lose calls all the time when we're all on jobs. what do you have for that?",
            "how much does it cost and does it actually work?",
            "ok what happens, like step by step, when someone calls and we miss it?",
        ],
    )

    # ── Scenario 2: HVAC asking about bundle pricing ───────────────────────
    run_conversation(
        "Scenario 2: HVAC company — bundle pricing inquiry",
        [
            "Hi, we're an HVAC company, around 8 technicians",
            "I've been looking at your site. What's the full stack bundle and what do I get?",
            "How much does it save vs buying them separately?",
            "Is there a contract? What if it's not working for us after 3 months?",
        ],
    )

    # ── Scenario 3: Skeptic — AI is overhyped ─────────────────────────────
    run_conversation(
        "Scenario 3: Skeptic — thinks AI is all hype",
        [
            "I'm a contractor, been in business 22 years. Every tech company tells me their thing will change my life and it never does.",
            "why would AI be any different",
            "ok fine. what does the missed call thing actually do, in plain english",
            "and if it doesn't work what do I lose",
        ],
    )

    # ── Scenario 4: Ready to book immediately ─────────────────────────────
    run_conversation(
        "Scenario 4: Motivated buyer — wants to book right now",
        [
            "I run a cleaning company and I want to sign up. How do I get started?",
            "I want all 4 products. Can we just do a call to get this going?",
            "My name is Sarah Chen, email is sarah@sparklecare.com, phone 215-555-0192",
        ],
    )

    # ── Scenario 5: Off-topic question ────────────────────────────────────
    run_conversation(
        "Scenario 5: Off-topic / out-of-scope questions",
        [
            "Can you help me with my taxes?",
            "What about website design, do you do that?",
            "Ok what DO you actually do then",
        ],
    )

    print(f"\n\n{DIVIDER}")
    print("  ALL 5 SCENARIOS COMPLETE")
    print(DIVIDER)
    print("\nReview the transcripts above to assess:")
    print("  • Brand voice consistency (confident, no corporate speak)")
    print("  • Pricing accuracy")
    print("  • Objection handling quality")
    print("  • Lead capture flow")
    print("  • Out-of-scope redirection")


if __name__ == "__main__":
    main()
