import pytest

from devtools_signal_engine.cohorts import (
    enrichment_targets,
    format_cohort_catalog,
    get_cohort,
    runnable_targets,
)


def test_global_cohort_has_five_runnable_targets():
    targets = runnable_targets("global")
    assert [target.github_org for target in targets] == [
        "getsentry",
        "grafana",
        "hashicorp",
        "PostHog",
        "cloudflare",
    ]
    assert not enrichment_targets("global")


def test_qatar_cohort_separates_observable_from_enrichment_targets():
    assert [target.github_org for target in runnable_targets("qatar")] == ["qcri"]
    assert [target.organization for target in enrichment_targets("qatar")] == [
        "Qatar Science & Technology Park (QSTP)",
        "Qatar Development Bank (QDB)",
        "Ooredoo Qatar",
        "Qatar Financial Centre (QFC)",
    ]


def test_get_cohort_is_case_insensitive_and_rejects_unknown_names():
    assert get_cohort(" Qatar ") == get_cohort("qatar")
    with pytest.raises(ValueError, match="available cohorts: global, qatar"):
        get_cohort("emea")


def test_catalog_labels_unverified_targets_without_inventing_handles():
    catalog = format_cohort_catalog()
    assert "Qatar Computing Research Institute (QCRI): qcri [github]" in catalog
    assert "Ooredoo Qatar: no verified GitHub org [enrichment]" in catalog
