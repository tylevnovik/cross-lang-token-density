from datetime import UTC, datetime

from cltd.agent_logging.run_log import append_run_log, read_run_logs
from cltd.schemas import AgentRunLog


def test_append_and_read_run_log(tmp_path):
    path = tmp_path / "runs.jsonl"
    record = AgentRunLog(
        run_id="r1",
        timestamp=datetime(2026, 5, 26, tzinfo=UTC),
        phase="test",
        actor="coding_agent",
        model="gpt-5",
        task="write a test log",
    )

    append_run_log(path, record)
    loaded = read_run_logs(path)

    assert len(loaded) == 1
    assert loaded[0].run_id == "r1"
