from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import typer

from cltd.agent_logging.run_log import append_run_log
from cltd.schemas import AgentRunLog

app = typer.Typer()


@app.command()
def main(
    run_id: str,
    phase: str,
    task: str,
    model: str = "unknown",
    reflection_path: Path | None = None,
    log_path: Path = Path("research_log/runs/agent_runs.jsonl"),
) -> None:
    record = AgentRunLog(
        run_id=run_id,
        timestamp=datetime.now(UTC),
        phase=phase,
        actor="coding_agent",
        model=model,
        task=task,
        reflection_path=str(reflection_path) if reflection_path else None,
    )
    append_run_log(log_path, record)
    typer.echo(f"logged {run_id} -> {log_path}")


if __name__ == "__main__":
    app()
