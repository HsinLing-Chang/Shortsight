from repositories.utm_params import summarize_utm_user_stats


def test_summarize_utm_user_stats():
    result = [
        {"source": "Google", "medium": "cpc",
            "total_interactions": 10, "new_users": 5},
        {"source": "Facebook", "medium": "social",
            "total_interactions": 5, "new_users": 1},
        {"source": "Instagram", "medium": "social",
            "total_interactions": 17, "new_users": 13},
    ]
    summary = summarize_utm_user_stats(result)
    assert isinstance(summary, dict)
    assert len(summary["data"]) == 3
    assert summary["summary"]["total_users"] == 32
    assert summary["summary"]["overall_ratio"] == 59.4
    assert summary["data"][0]["source"] == "Google"


def test_empty_input():
    summary = summarize_utm_user_stats([])
    assert summary["summary"]["total_users"] == 0
    assert summary["summary"]["total_new_users"] == 0
    assert summary["summary"]["overall_ratio"] == 0.0
    assert summary["summary"]["new_user_level"] == "Unstable"
    assert len(summary["data"]) == 0


def test_zero_interactions():
    result = [
        {"source": "Google", "medium": "cpc",
            "total_interactions": 0, "new_users": 0},
    ]
    summary = summarize_utm_user_stats(result)
    assert summary["summary"]["total_users"] == 0
    assert summary["summary"]["overall_ratio"] == 0.0
    assert summary["data"][0]["new_user_ratio"] == 0.0
    assert summary["summary"]["new_user_level"] == "Unstable"
