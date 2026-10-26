#!/usr/bin/env python3
"""Stop hook: run the suite; if it fails, block the stop and hand Claude the failure output."""

import json
import os
import subprocess
import sys

MAX_REASON_CHARS = 6000

project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
venv_python = os.path.join(project_dir, ".venv", "bin", "python")
python = venv_python if os.path.exists(venv_python) else sys.executable

result = subprocess.run(
    [python, "-m", "pytest", "tests/unit", "tests/api", "-q"],
    cwd=project_dir,
    capture_output=True,
    text=True,
    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
)

if result.returncode != 0:
    output = (result.stdout + result.stderr).strip()
    if len(output) > MAX_REASON_CHARS:
        output = "...[truncated]...\n" + output[-MAX_REASON_CHARS:]
    print(
        json.dumps(
            {
                "decision": "block",
                "reason": f"pytest tests/unit tests/api failed. Fix it, or say clearly that you could not.\n\n{output}",
            }
        )
    )

sys.exit(0)
