"""One-shot runner: load problem-statement.md, invoke the full 3-stage council,
dump structured results to data/run-<timestamp>/."""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from backend.council import run_full_council

ROOT = Path(__file__).resolve().parent
PROBLEM_FILE = ROOT / "problem-statement.md"


async def main() -> None:
    problem = PROBLEM_FILE.read_text()
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    out_dir = ROOT / "data" / f"run-{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[runner] problem statement loaded: {len(problem)} chars")
    print(f"[runner] output directory: {out_dir}")

    stage1, stage2, stage3, metadata = await run_full_council(problem)

    (out_dir / "stage1.json").write_text(json.dumps(stage1, indent=2, ensure_ascii=False))
    (out_dir / "stage2.json").write_text(json.dumps(stage2, indent=2, ensure_ascii=False))
    (out_dir / "stage3.json").write_text(json.dumps(stage3, indent=2, ensure_ascii=False))
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False))

    chairman = stage3.get("response", "") if isinstance(stage3, dict) else ""
    (out_dir / "chairman-report.md").write_text(chairman)

    print(f"[runner] stage1 councillors: {len(stage1)}")
    print(f"[runner] stage2 reviewers:   {len(stage2)}")
    print(f"[runner] chairman output:    {len(chairman)} chars")
    print(f"[runner] done — see {out_dir}")


if __name__ == "__main__":
    asyncio.run(main())
