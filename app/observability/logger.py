import json
import time
from datetime import datetime, timezone
from pathlib import Path


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def log_query(
    question: str,
    department: str | None,
    access_level: str | None,
    sources: list,
    latency_ms: float,
    abstained: bool,
):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "department": department,
        "access_level": access_level,
        "source_count": len(sources),
        "sources": [
            source["source"]
            for source in sources
        ],
        "latency_ms": round(latency_ms, 2),
        "abstained": abstained,
    }

    log_file = LOG_DIR / "queries.jsonl"

    with log_file.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")