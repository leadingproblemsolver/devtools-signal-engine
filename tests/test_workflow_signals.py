from devtools_signal_engine.workflow_signals import build_workflow_surface


def test_workflow_surface_reports_observed_workflows_and_codeowners() -> None:
    surface = build_workflow_surface(
        [{"id": 1, "name": "ci"}, {"id": 2, "name": "release"}],
        codeowners_path=".github/CODEOWNERS",
    )

    assert surface.workflow_count == 2
    assert surface.uses_github_actions is True
    assert surface.codeowners_path == ".github/CODEOWNERS"
    assert "github_actions_workflows=2" in surface.observed_evidence
    assert "codeowners_path=.github/CODEOWNERS" in surface.observed_evidence
    assert surface.unknowns == ()


def test_absence_of_codeowners_is_unknown_not_negative_buying_signal() -> None:
    surface = build_workflow_surface([], codeowners_path=None)

    assert surface.workflow_count == 0
    assert surface.uses_github_actions is False
    assert surface.codeowners_path is None
    assert "codeowners_not_observed_in_supported_locations" in surface.unknowns
