"""Helper functions for the Review Reply Streamlit UI."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

DRAFTS_PATH = ROOT / "products" / "02_review_reply" / "drafts.jsonl"
APPROVALS_PATH = ROOT / "products" / "02_review_reply" / "approvals.jsonl"


def load_drafts() -> list[dict]:
    if not DRAFTS_PATH.exists():
        return []
    seen = {}
    for line in DRAFTS_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            seen[rec["review_id"]] = rec  # last write wins (handles re-drafts)
    return list(seen.values())


def save_approval(review_id: str, final_reply: str) -> None:
    APPROVALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with APPROVALS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"review_id": review_id, "final_reply": final_reply}) + "\n")


def update_status(review_id: str, status: str) -> None:
    """Rewrite the drafts.jsonl with the updated status for review_id."""
    drafts = load_drafts()
    for d in drafts:
        if d["review_id"] == review_id:
            d["status"] = status
    DRAFTS_PATH.write_text(
        "\n".join(json.dumps(d) for d in drafts) + "\n",
        encoding="utf-8",
    )
