"""Tests for utility functions."""

from datetime import datetime
from freezegun import freeze_time

from osdu_mcp_server.shared.utils import get_timestamp, merge_dicts


@freeze_time("2025-01-15 10:30:00")
def test_get_timestamp():
    """Test timestamp generation."""
    timestamp = get_timestamp()
    assert timestamp == "2025-01-15T10:30:00Z"
    # Verify it's a valid ISO format
    datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def test_merge_dicts_simple():
    """Test simple dictionary merge."""
    base = {"a": 1, "b": 2}
    override = {"b": 3, "c": 4}
    result = merge_dicts(base, override)

    assert result == {"a": 1, "b": 3, "c": 4}
    # Ensure original dictionaries are not modified
    assert base == {"a": 1, "b": 2}
    assert override == {"b": 3, "c": 4}


def test_merge_dicts_nested():
    """Test nested dictionary merge."""
    base = {
        "server": {"url": "http://base.com", "timeout": 30},
        "auth": {"scope": "base-scope"}
    }
    override = {
        "server": {"url": "http://override.com"},
        "auth": {"scope": "override-scope", "method": "oauth"}
    }

    result = merge_dicts(base, override)

    expected = {
        "server": {"url": "http://override.com", "timeout": 30},
        "auth": {"scope": "override-scope", "method": "oauth"}
    }
    assert result == expected


def test_merge_dicts_deep_nested():
    """Test deeply nested dictionary merge."""
    base = {
        "level1": {
            "level2": {
                "level3": {"a": 1, "b": 2}
            }
        }
    }
    override = {
        "level1": {
            "level2": {
                "level3": {"b": 3, "c": 4}
            }
        }
    }

    result = merge_dicts(base, override)

    expected = {
        "level1": {
            "level2": {
                "level3": {"a": 1, "b": 3, "c": 4}
            }
        }
    }
    assert result == expected


def test_merge_dicts_non_dict_override():
    """Test merge when override value is not a dict."""
    base = {"config": {"nested": "value"}}
    override = {"config": "simple"}

    result = merge_dicts(base, override)

    assert result == {"config": "simple"}


def test_merge_dicts_empty():
    """Test merge with empty dictionaries."""
    assert merge_dicts({}, {}) == {}
    assert merge_dicts({"a": 1}, {}) == {"a": 1}
    assert merge_dicts({}, {"b": 2}) == {"b": 2}
