from ideation_tools.project_init import build_initial_state, build_initialization_transaction


def test_initial_state_is_minimal_and_records_provenance():
    fp = "a" * 40
    state = build_initial_state(project_id="demo", project_slug="demo", agent_fingerprint=fp)
    assert state["project"]["iteration"] == 1
    assert state["project"]["revision"] == 1
    assert state["workflow"]["spine_context"] == "orient_and_initialize"
    assert state["decisions"] == []
    assert state["assumptions"] == []
    assert state["evidence"] == []
    assert state["artifacts"] == []
    assert state["agent_provenance"]["repository_commit"] == fp


def test_initialization_transaction_uses_existing_canonical_state_model():
    tx = build_initialization_transaction(
        project_id="demo", project_slug="demo", agent_fingerprint="b" * 40,
        transaction_id="workflow:init-project:1",
    )
    assert tx["expected_revision"] == 0
    assert tx["project"]["iteration"] == 1
    assert tx["state_mutations"][0]["operation"] == "initialize"
    assert tx["state_mutations"][0]["patch"]["workflow"]["vision_status"] == "not_started"
